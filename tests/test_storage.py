"""Storageクラスのテスト"""

import tempfile

from src.storage import Storage


class TestStorage:
    """Storageクラスのテスト"""

    def test_save_and_load_json(self):
        """JSONファイルの保存・読み込みテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Storage(data_dir=tmpdir)
            test_data = {"key": "value", "number": 123}

            # 保存
            result = storage.save_json("test.json", test_data)
            assert result is True

            # 読み込み
            loaded_data = storage.load_json("test.json")
            assert loaded_data == test_data

    def test_save_and_load_site(self):
        """サイト設定の保存・読み込みテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Storage(data_dir=tmpdir)
            test_site = {
                "id": "test_site",
                "name": "Test Site",
                "url": "https://example.com",
                "category": "AI",
                "collector_type": "rss",
                "collector_config": {"feed_url": "https://example.com/feed.xml", "check_interval_minutes": 60},
                "enabled": False,
            }

            # バリデーション
            is_valid, errors = storage.validate_site(test_site)
            assert is_valid is True
            assert len(errors) == 0

            # 保存
            result = storage.save_site(test_site)
            assert result is True

            # 読み込み
            loaded_site = storage.load_site("test_site")
            assert loaded_site is not None
            assert loaded_site.get("id") == "test_site"
            assert loaded_site.get("name") == "Test Site"

    def test_validate_site_required_fields(self):
        """必須フィールドのバリデーションテスト"""
        storage = Storage()

        # idが不足
        invalid_site = {"name": "Test Site", "url": "https://example.com", "category": "AI", "collector_type": "rss"}
        is_valid, errors = storage.validate_site(invalid_site)
        assert is_valid is False
        assert "idは必須です" in errors

    def test_validate_site_email_config(self):
        """email方式の設定バリデーションテスト"""
        storage = Storage()

        # subscription_emailが不足
        invalid_site = {
            "id": "test_site",
            "name": "Test Site",
            "url": "https://example.com",
            "category": "AI",
            "collector_type": "email",
            "collector_config": {
                "email_account_id": "gmail_account_001"
                # subscription_emailが不足
            },
        }
        is_valid, errors = storage.validate_site(invalid_site)
        assert is_valid is False
        assert any("subscription_emailは必須です" in error for error in errors)

    def test_validate_site_rss_config(self):
        """rss方式の設定バリデーションテスト"""
        storage = Storage()

        # feed_urlが不足
        invalid_site = {
            "id": "test_site",
            "name": "Test Site",
            # urlが不足
            "category": "AI",
            "collector_type": "rss",
            "collector_config": {
                # feed_urlが不足
            },
        }
        is_valid, errors = storage.validate_site(invalid_site)
        assert is_valid is False
        assert any("feed_urlまたはurlが必須です" in error for error in errors)

    def test_validate_site_check_interval(self):
        """check_interval_minutesの範囲チェックテスト"""
        storage = Storage()

        # check_interval_minutesが0以下
        invalid_site = {
            "id": "test_site",
            "name": "Test Site",
            "url": "https://example.com",
            "category": "AI",
            "collector_type": "rss",
            "collector_config": {"feed_url": "https://example.com/feed.xml", "check_interval_minutes": 0},  # 不正な値
        }
        is_valid, errors = storage.validate_site(invalid_site)
        assert is_valid is False
        assert any("check_interval_minutesは1以上の正の数" in error for error in errors)
