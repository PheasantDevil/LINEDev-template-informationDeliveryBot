"""Webhook server tests"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.webhook_server import app


@pytest.fixture
def client():
    """Create test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestWebhookServer:
    """Webhook server tests"""

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.data.decode() == "OK"

    def test_index_endpoint(self, client):
        """Test index endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Information Delivery Bot" in response.data.decode()

    def test_webhook_without_signature(self, client):
        """Test webhook without signature (should fail)"""
        response = client.post("/webhook", data=json.dumps({"events": []}), content_type="application/json")
        # Should fail because LineNotifier initialization will fail without env vars
        assert response.status_code in [400, 500]

    @patch("src.webhook_server.LineNotifier")
    def test_webhook_with_valid_signature(self, mock_notifier_class, client):
        """Test webhook with valid signature"""
        # Mock LineNotifier
        mock_notifier = MagicMock()
        mock_notifier.channel_secret = "test_secret"
        mock_notifier.verify_signature.return_value = True
        mock_notifier_class.return_value = mock_notifier

        event = {
            "type": "message",
            "message": {"type": "text", "text": "test"},
            "replyToken": "test_reply_token",
            "source": {"userId": "test_user_id"},
        }

        response = client.post(
            "/webhook",
            data=json.dumps({"events": [event]}),
            content_type="application/json",
            headers={"X-Line-Signature": "test_signature"},
        )

        # Should process successfully
        assert response.status_code == 200
        assert response.data.decode() == "OK"

    @patch("src.webhook_server.LineNotifier")
    def test_webhook_invalid_signature(self, mock_notifier_class, client):
        """Test webhook with invalid signature"""
        # Mock LineNotifier
        mock_notifier = MagicMock()
        mock_notifier.channel_secret = "test_secret"
        mock_notifier.verify_signature.return_value = False
        mock_notifier_class.return_value = mock_notifier

        response = client.post(
            "/webhook",
            data=json.dumps({"events": []}),
            content_type="application/json",
            headers={"X-Line-Signature": "invalid_signature"},
        )

        # Should fail with 400
        assert response.status_code == 400
