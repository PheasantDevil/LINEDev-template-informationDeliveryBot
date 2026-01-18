"""Information collection and delivery execution script"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv  # noqa: E402

load_dotenv(project_root / ".env")

from src.collectors.base import BaseInformationCollector, InformationItem  # noqa: E402
from src.collectors.email_collector import EmailCollector  # noqa: E402
from src.collectors.rss_reader import RSSReaderCollector  # noqa: E402
from src.diff_detector import DiffDetector  # noqa: E402
from src.line_notifier import LineNotifier  # noqa: E402
from src.storage import Storage  # noqa: E402
from src.user_manager import UserManager  # noqa: E402


def main():
    """Main process"""
    print("=" * 60)
    print("Information Collection and Delivery Script Started")
    print("=" * 60)

    # Check environment variables (for debugging)
    line_token_exists = bool(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
    gmail_account_exists = bool(os.getenv("GMAIL_ACCOUNT"))
    gemini_key_exists = bool(os.getenv("GEMINI_API_KEY"))

    print("Environment Variable Check:")
    print(f"  LINE_CHANNEL_ACCESS_TOKEN: {'✓' if line_token_exists else '✗'}")
    print(f"  GMAIL_ACCOUNT: {'✓' if gmail_account_exists else '✗'}")
    print(f"  GEMINI_API_KEY: {'✓' if gemini_key_exists else '✗'}")

    # Initialize
    storage = Storage()
    user_manager = UserManager(storage)
    diff_detector = DiffDetector()

    # Initialize LINE notifier
    try:
        line_notifier = LineNotifier()
    except ValueError as e:
        print(f"❌ LINE Notifier initialization error: {e}")
        print("Please check if environment variable LINE_CHANNEL_ACCESS_TOKEN is set")
        print("⚠️ LINE Notifier could not be initialized, but will continue with information collection only")
        line_notifier = None

    # Load site configurations
    sites_data = storage.load_sites()
    if not sites_data or not sites_data.get("sites"):
        print("⚠️ Warning: Site configurations not found")
        print("✓ Exiting normally as there are no site configurations")
        sys.exit(0)

    sites = sites_data.get("sites", [])
    enabled_sites = [s for s in sites if s.get("enabled", False)]

    print(f"Number of enabled sites: {len(enabled_sites)}")

    # Collect information from each site
    all_new_items = []

    for site in enabled_sites:
        site_id = site.get("id", "")
        site_name = site.get("name", "Unknown")
        collector_type = site.get("collector_type", "")

        print(f"\n--- Site: {site_name} ({site_id}) ---")

        # Check collection timing
        collector = _create_collector(collector_type, storage)
        if not collector:
            print(f"Warning: Collector type '{collector_type}' is not implemented")
            continue

        if not collector.should_collect(site):
            print("Skipped: Not time to collect yet")
            continue

        # Collect information
        try:
            items = collector.collect(site)
            print(f"Collected information: {len(items)} items")

            if items:
                # Extract new information using diff detection
                stored_items_data = storage.load_information_items()
                stored_items = stored_items_data.get("items", []) if stored_items_data else []

                new_items = diff_detector.detect_new_items(items, stored_items)
                print(f"New information: {len(new_items)} items")

                if new_items:
                    all_new_items.extend(new_items)

                    # Record collection completion
                    collector.mark_as_collected(site_id, items)

                    # Save information items
                    _save_new_items(storage, new_items, stored_items)
        except Exception as e:
            print(f"❌ Error: Failed to collect information - {e}")
            import traceback

            traceback.print_exc()
            continue

    # Deliver new information
    if all_new_items:
        if line_notifier is None:
            print(
                f"\n⚠️ Warning: There are {len(all_new_items)} new information items, but LINE Notifier was not initialized, so delivery is skipped"
            )
        else:
            print(f"\n--- Starting delivery of new information ({len(all_new_items)} items) ---")
            _deliver_new_items(all_new_items, user_manager, line_notifier)
    else:
        print("\nNo new information")

    print("\n" + "=" * 60)
    print("Information Collection and Delivery Script Completed")
    print("=" * 60)


def _create_collector(collector_type: str, storage: Storage) -> BaseInformationCollector:
    """
    Create collector

    Args:
        collector_type: Collector type
        storage: Storage instance

    Returns:
        BaseInformationCollector: Collector instance
    """
    if collector_type == "email":
        return EmailCollector(storage)
    elif collector_type == "rss":
        return RSSReaderCollector(storage)
    # Other types will be added in the future
    # elif collector_type == 'scraper':
    #     return ScraperCollector(storage)
    else:
        return None


def _save_new_items(storage: Storage, new_items: List[InformationItem], stored_items: List[Dict]):
    """
    Save new information items

    Args:
        storage: Storage instance
        new_items: List of new information items
        stored_items: List of existing information items
    """
    # Convert new items to dictionary format
    new_items_dict = [item.to_dict() for item in new_items]

    # Merge with existing items
    all_items = stored_items + new_items_dict

    # Keep only the latest 1000 items (simple implementation)
    if len(all_items) > 1000:
        all_items = sorted(all_items, key=lambda x: x.get("scraped_at", ""), reverse=True)[:1000]

    storage.save_information_items(all_items)


def _deliver_new_items(new_items: List[InformationItem], user_manager: UserManager, line_notifier: LineNotifier):
    """
    Deliver new information

    Args:
        new_items: List of new information items
        user_manager: UserManager instance
        line_notifier: LineNotifier instance
    """
    # Group by category
    items_by_category = {}
    for item in new_items:
        category = item.category
        if category not in items_by_category:
            items_by_category[category] = []
        items_by_category[category].append(item)

    # Deliver by category
    for category, items in items_by_category.items():
        # Get users subscribed to this category
        user_ids = user_manager.get_subscribed_users(category)

        if not user_ids:
            print(f"No users subscribed to category '{category}'")
            continue

        print(f"Category '{category}': Delivering to {len(user_ids)} users")

        # Deliver to each user
        for user_id in user_ids:
            try:
                success = line_notifier.send_information_items(user_id, [item.to_dict() for item in items])
                if success:
                    print(f"✓ Delivery successful: {user_id[:10]}...")
                else:
                    print(f"❌ Delivery failed: {user_id[:10]}...")
            except Exception as e:
                print(f"❌ Delivery error: {user_id[:10]}... - {e}")


if __name__ == "__main__":
    main()
