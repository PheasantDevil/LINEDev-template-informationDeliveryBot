"""Data persistence management module"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse


class Storage:
    """Class for managing data persistence"""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize

        Args:
            data_dir: Path to data directory
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sites_dir = self.data_dir / "sites"
        self.sites_dir.mkdir(parents=True, exist_ok=True)

        # Migrate existing sites.json to individual files (first time only)
        self._migrate_legacy_sites()

    def save_json(self, filename: str, data: Dict) -> bool:
        """
        Save data to JSON file

        Args:
            filename: File name
            data: Data to save

        Returns:
            bool: True if save succeeded, False otherwise
        """
        try:
            file_path = self.data_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Data saved: {file_path}")
            return True
        except Exception as e:
            print(f"Error: Failed to save data - {e}")
            return False

    def load_json(self, filename: str) -> Optional[Dict]:
        """
        Load data from JSON file

        Args:
            filename: File name

        Returns:
            Dict: Loaded data, or None if file doesn't exist
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error: Failed to load data - {e}")
            return None

    def _migrate_legacy_sites(self):
        """
        Migrate existing sites.json to individual files (first time only)
        """
        legacy_file = self.data_dir / "sites.json"
        if not legacy_file.exists():
            return

        # Skip if files already exist in sites directory
        if any(self.sites_dir.glob("*.json")):
            return

        print("Migrating existing sites.json to individual files...")
        legacy_data = self.load_json("sites.json")
        if legacy_data and legacy_data.get("sites"):
            for site in legacy_data["sites"]:
                site_id = site.get("id")
                if site_id:
                    self.save_site(site)
            print(f"✓ Migrated {len(legacy_data['sites'])} sites")

    def validate_site(self, site: Dict) -> Tuple[bool, List[str]]:
        """
        Validate site configuration

        Args:
            site: Site configuration

        Returns:
            Tuple[bool, List[str]]: (validation success, list of error messages)
        """
        errors = []

        # Required field checks
        if not site.get("id"):
            errors.append("id is required")
        else:
            # ID format check (alphanumeric and underscore only)
            site_id = site["id"]
            if not re.match(r"^[a-zA-Z0-9_]+$", site_id):
                errors.append(f"id can only contain alphanumeric characters and underscores (current value: {site_id})")

        if not site.get("name"):
            errors.append("name is required")

        if not site.get("url"):
            errors.append("url is required")
        else:
            # URL format validation
            url = site["url"]
            try:
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    errors.append(f"url must be a valid URL format (current value: {url})")
            except Exception:
                errors.append(f"url must be a valid URL format (current value: {url})")

        if not site.get("category"):
            errors.append("category is required")

        collector_type = site.get("collector_type")
        if not collector_type:
            errors.append("collector_type is required")
        elif collector_type not in ["email", "rss", "scraper"]:
            errors.append(f"collector_type must be one of: email, rss, scraper (current value: {collector_type})")

        # Collector-specific configuration checks
        collector_config = site.get("collector_config", {})

        if collector_type == "email":
            # For email type, email_account_id and subscription_email are required
            if not collector_config.get("email_account_id"):
                errors.append("collector_config.email_account_id is required for email type")

            if not collector_config.get("subscription_email"):
                errors.append("collector_config.subscription_email is required for email type")
            else:
                # Email address format check (simple)
                email = collector_config["subscription_email"]
                if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                    errors.append(f"subscription_email must be a valid email address format (current value: {email})")

        elif collector_type == "rss":
            # For rss type, feed_url is required (or use url)
            feed_url = collector_config.get("feed_url") or site.get("url", "")
            if not feed_url:
                errors.append("collector_config.feed_url or url is required for rss type")
            else:
                # URL format validation
                try:
                    parsed = urlparse(feed_url)
                    if not parsed.scheme or not parsed.netloc:
                        errors.append(f"feed_url must be a valid URL format (current value: {feed_url})")
                except Exception:
                    errors.append(f"feed_url must be a valid URL format (current value: {feed_url})")

        # For scraper type, selector is recommended (not required, warning only)
        if collector_type == "scraper" and not collector_config.get("selector"):
            # Warnings are not treated as errors (implement warning functionality separately in the future)
            pass

        # Range check for check_interval_minutes
        check_interval = collector_config.get("check_interval_minutes")
        if check_interval is not None:
            if not isinstance(check_interval, int):
                errors.append("check_interval_minutes must be an integer")
            elif check_interval <= 0:
                errors.append("check_interval_minutes must be a positive integer >= 1")

        return len(errors) == 0, errors

    def save_site(self, site: Dict) -> bool:
        """
        Save individual site configuration and update sites.json

        Args:
            site: Site configuration

        Returns:
            bool: True if save succeeded, False otherwise
        """
        # Run validation
        is_valid, errors = self.validate_site(site)
        if not is_valid:
            print("❌ Site configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False

        site_id = site.get("id")
        if not site_id:
            print("Error: Site ID is not set")
            return False

        # Add metadata
        site_data = {"updated_at": datetime.now().isoformat(), **site}

        filename = f"{site_id}.json"
        file_path = self.sites_dir / filename

        try:
            # Save individual file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(site_data, f, ensure_ascii=False, indent=2)

            # Update sites.json (aggregated file)
            self._update_sites_json()

            return True
        except Exception as e:
            print(f"Error: Failed to save site configuration - {e}")
            return False

    def _update_sites_json(self):
        """
        Aggregate individual files in data/sites/ and update sites.json
        """
        sites = []

        # Load all JSON files in sites directory
        for file_path in self.sites_dir.glob("*.json"):
            # Skip _index.json and example files
            if file_path.name.startswith("_") or file_path.name.endswith(".example.json"):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    site_data = json.load(f)
                    # Exclude updated_at as it's metadata
                    if "updated_at" in site_data:
                        del site_data["updated_at"]
                    sites.append(site_data)
            except Exception as e:
                print(f"Warning: Failed to load {file_path.name} - {e}")
                continue

        # Update sites.json
        data = {"updated_at": datetime.now().isoformat(), "count": len(sites), "sites": sites}
        self.save_json("sites.json", data)

    def load_site(self, site_id: str) -> Optional[Dict]:
        """
        Load individual site configuration

        Args:
            site_id: Site ID

        Returns:
            Dict: Site configuration data, or None if doesn't exist
        """
        filename = f"{site_id}.json"
        file_path = self.sites_dir / filename

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error: Failed to load site configuration - {e}")
            return None

    def load_sites(self) -> Optional[Dict]:
        """
        Load all site configurations

        Returns:
            Dict: Site configuration data (maintains backward compatibility with legacy format)
        """
        # Prefer sites.json if it exists
        sites_json_path = self.data_dir / "sites.json"
        if sites_json_path.exists():
            data = self.load_json("sites.json")
            if data:
                return data

        # Aggregate from individual files if sites.json doesn't exist
        sites = []

        # Load all JSON files in sites directory
        for file_path in self.sites_dir.glob("*.json"):
            # Skip _index.json and example files
            if file_path.name.startswith("_") or file_path.name.endswith(".example.json"):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    site_data = json.load(f)
                    # Exclude updated_at as it's metadata
                    if "updated_at" in site_data:
                        del site_data["updated_at"]
                    sites.append(site_data)
            except Exception as e:
                print(f"Warning: Failed to load {file_path.name} - {e}")
                continue

        data = {"updated_at": datetime.now().isoformat(), "count": len(sites), "sites": sites}

        # Update sites.json (so it can be loaded next time)
        self.save_json("sites.json", data)

        return data

    def save_sites(self, sites: List[Dict]) -> bool:
        """
        Save site configuration list (maintained for backward compatibility)

        Args:
            sites: List of site configurations

        Returns:
            bool: True if save succeeded, False otherwise
        """
        success = True
        for site in sites:
            if not self.save_site(site):
                success = False
        # _update_sites_json is called in save_site, but update once more at the end for safety
        self._update_sites_json()
        return success

    def delete_site(self, site_id: str) -> bool:
        """
        Delete site configuration and update sites.json

        Args:
            site_id: Site ID

        Returns:
            bool: True if deletion succeeded, False otherwise
        """
        filename = f"{site_id}.json"
        file_path = self.sites_dir / filename

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            # Update sites.json
            self._update_sites_json()
            return True
        except Exception as e:
            print(f"Error: Failed to delete site configuration - {e}")
            return False

    def save_information_items(self, items: List[Dict]) -> bool:
        """
        Save information items

        Args:
            items: List of information items

        Returns:
            bool: True if save succeeded, False otherwise
        """
        data = {"updated_at": datetime.now().isoformat(), "count": len(items), "items": items}
        return self.save_json("information_items.json", data)

    def load_information_items(self) -> Optional[Dict]:
        """
        Load information items

        Returns:
            Dict: Information items data
        """
        return self.load_json("information_items.json")

    def save_users(self, users: List[Dict]) -> bool:
        """
        Save user information

        Args:
            users: List of user information

        Returns:
            bool: True if save succeeded, False otherwise
        """
        data = {"updated_at": datetime.now().isoformat(), "count": len(users), "users": users}
        return self.save_json("users.json", data)

    def load_users(self) -> Optional[Dict]:
        """
        Load user information

        Returns:
            Dict: User information data
        """
        return self.load_json("users.json")

    def save_category_groups(self, groups: List[Dict]) -> bool:
        """
        Save category group information

        Args:
            groups: List of category group information

        Returns:
            bool: True if save succeeded, False otherwise
        """
        data = {"updated_at": datetime.now().isoformat(), "count": len(groups), "groups": groups}
        return self.save_json("category_groups.json", data)

    def load_category_groups(self) -> Optional[Dict]:
        """
        Load category group information

        Returns:
            Dict: Category group information data
        """
        return self.load_json("category_groups.json")

    def save_email_accounts(self, accounts: List[Dict]) -> bool:
        """
        Save email account information

        Args:
            accounts: List of email account information

        Returns:
            bool: True if save succeeded, False otherwise
        """
        data = {"updated_at": datetime.now().isoformat(), "count": len(accounts), "accounts": accounts}
        return self.save_json("email_accounts.json", data)

    def load_email_accounts(self) -> Optional[Dict]:
        """
        Load email account information

        Returns:
            Dict: Email account information data
        """
        return self.load_json("email_accounts.json")
