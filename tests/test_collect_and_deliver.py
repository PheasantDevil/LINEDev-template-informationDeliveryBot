"""Information collection and delivery tests"""

import os
from unittest.mock import MagicMock, patch

# Set dummy environment variables for testing
os.environ.setdefault("LINE_CHANNEL_ACCESS_TOKEN", "dummy_token")
os.environ.setdefault("GMAIL_ACCOUNT", "dummy@gmail.com")
os.environ.setdefault("GEMINI_API_KEY", "dummy_key")


@patch("src.collect_and_deliver.LineNotifier")
@patch("src.collect_and_deliver.Storage")
def test_main_no_sites(mock_storage_class, mock_notifier_class):
    """Test main function with no sites"""
    from src.collect_and_deliver import main

    # Mock Storage
    mock_storage = MagicMock()
    mock_storage.load_sites.return_value = {"sites": []}
    mock_storage_class.return_value = mock_storage

    # Mock LineNotifier
    mock_notifier = MagicMock()
    mock_notifier_class.return_value = mock_notifier

    # Should exit normally
    main()
    mock_storage.load_sites.assert_called_once()


@patch("src.collect_and_deliver.LineNotifier")
@patch("src.collect_and_deliver.Storage")
def test_main_with_enabled_sites(mock_storage_class, mock_notifier_class):
    """Test main function with enabled sites"""
    from src.collect_and_deliver import main

    # Mock Storage
    mock_storage = MagicMock()
    mock_storage.load_sites.return_value = {
        "sites": [
            {
                "id": "test_site",
                "name": "Test Site",
                "url": "https://example.com",
                "category": "AI",
                "collector_type": "rss",
                "enabled": True,
                "collector_config": {"check_interval_minutes": 60},
            }
        ]
    }
    mock_storage.load_information_items.return_value = {"items": []}
    mock_storage_class.return_value = mock_storage

    # Mock LineNotifier
    mock_notifier = MagicMock()
    mock_notifier_class.return_value = mock_notifier

    # Mock collector
    with patch("src.collect_and_deliver.RSSReaderCollector") as mock_collector_class:
        mock_collector = MagicMock()
        mock_collector.should_collect.return_value = True
        mock_collector.collect.return_value = []
        mock_collector_class.return_value = mock_collector

        main()
        mock_storage.load_sites.assert_called_once()
