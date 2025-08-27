import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import router and dependencies
from app.api import router
from app.models import Message

# Create FastAPI app for testing
app = FastAPI()
app.include_router(router, prefix="/telegram")
client = TestClient(app)

class TestSendMessageEndpoint:
    """Test suite for the /send endpoint"""
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    def test_send_message_success(self, mock_send_telegram):
        """Successful test of the /send endpoint"""
        # Mock the response from send_telegram_message
        mock_telegram_response = {
            "ok": True,
            "result": {
                "message_id": 42,
                "chat": {"id": 123456789},
                "text": "Test message"
            }
        }
        mock_send_telegram.return_value = mock_telegram_response
        
        # Test payload
        payload = {
            "chat_id": "123456789",
            "text": "Hello, this is a test message!"
        }
        
        # Make request to the endpoint
        response = client.post("/telegram/send", json=payload)
        
        # Verifications
        assert response.status_code == 200
        assert response.json() == mock_telegram_response
        
        # Verify that send_telegram_message was called with the correct parameters
        mock_send_telegram.assert_called_once()
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.chat_id == "123456789"
        assert called_msg.text == "Hello, this is a test message!"
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    def test_send_message_with_group_chat(self, mock_send_telegram):
        """Test sending message to a group chat"""
        mock_telegram_response = {"ok": True, "result": {"message_id": 99}}
        mock_send_telegram.return_value = mock_telegram_response
        
        # Group chat (negative ID)
        payload = {
            "chat_id": "-100123456789",
            "text": "Message for the group"
        }
        
        response = client.post("/telegram/send", json=payload)
        
        assert response.status_code == 200
        assert response.json() == mock_telegram_response
        
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.chat_id == "-100123456789"
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    def test_send_message_with_special_characters(self, mock_send_telegram):
        """Test sending message with special characters"""
        mock_telegram_response = {"ok": True}
        mock_send_telegram.return_value = mock_telegram_response
        
        payload = {
            "chat_id": "123456789",
            "text": "Hello! 🚀 Message with emojis and accents: ñáéíóú"
        }
        
        response = client.post("/telegram/send", json=payload)
        
        assert response.status_code == 200
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.text == "Hello! 🚀 Message with emojis and accents: ñáéíóú"
    
    def test_send_message_invalid_payload(self):
        """Test with invalid payload (missing required fields)"""
        # Payload without chat_id
        payload = {"text": "Missing chat_id"}
        
        response = client.post("/telegram/send", json=payload)
        
        # FastAPI should return a validation error
        assert response.status_code == 400
        error_detail = response.json()
        assert "detail" in error_detail
    
    def test_send_message_empty_text(self):
        """Test with empty text"""
        payload = {
            "chat_id": "123456789",
            "text": ""
        }
        
        response = client.post("/telegram/send", json=payload)
        
        # Depending on the validation in Message,
        # this could be 422 or pass
        # Assuming empty text is valid in the model
        assert response.status_code in [200, 422]
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    def test_send_message_service_error(self, mock_send_telegram):
        """Test when the Telegram service fails"""
        # Mock that raises an exception
        mock_send_telegram.side_effect = Exception("Telegram API error")
        
        payload = {
            "chat_id": "123456789",
            "text": "Test message"
        }
        
        response = client.post("/telegram/send", json=payload)
        
        # With error handling, it should return 500
        assert response.status_code == 500
        error_detail = response.json()
        assert "detail" in error_detail
        assert error_detail["detail"] == "Internal server error"


class TestTelegramWebhookEndpoint:
    """Test suite for the /webhook endpoint"""
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    @patch('app.api.ask_llm', new_callable=AsyncMock)
    def test_webhook_success(self, mock_ask_llm, mock_send_telegram):
        """Successful test of the Telegram webhook"""
        # Mock the response from the LLM
        mock_ask_llm.return_value = "This is the LLM's response"
        
        # Mock send_telegram_message
        mock_telegram_response = {"ok": True, "result": {"message_id": 42}}
        mock_send_telegram.return_value = mock_telegram_response
        
        # Payload simulating a Telegram webhook
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 987654321,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": 987654321,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "What is the capital of France?"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # Verifications
        assert response.status_code == 200
        assert response.json() == {"ok": True, "source": "llm"}
        
        # Verify that ask_llm was called with the correct text
        mock_ask_llm.assert_called_once_with("What is the capital of France?")
        
        # Verify that send_telegram_message was called
        mock_send_telegram.assert_called_once()
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.chat_id == 987654321
        assert called_msg.text == "This is the LLM's response"
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    @patch('app.api.ask_llm', new_callable=AsyncMock)
    def test_webhook_group_chat(self, mock_ask_llm, mock_send_telegram):
        """Test webhook with a group chat message"""
        mock_ask_llm.return_value = "Response for the group"
        mock_send_telegram.return_value = {"ok": True}
        
        # Group chat payload
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 987654321, "first_name": "User"},
                "chat": {
                    "id": -100123456789,  # Group chat
                    "title": "Test Group",
                    "type": "group"
                },
                "date": 1640995200,
                "text": "Hello bot!"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        assert response.status_code == 200
        assert response.json() == {"ok": True, "source": "llm"}
        
        # Verify group chat_id
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.chat_id == -100123456789
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    @patch('app.api.ask_llm', new_callable=AsyncMock)
    def test_webhook_with_emojis_and_special_chars(self, mock_ask_llm, mock_send_telegram):
        """Test webhook with emojis and special characters"""
        mock_ask_llm.return_value = "Response with emojis! 🤖"
        mock_send_telegram.return_value = {"ok": True}
        
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 123, "first_name": "User"},
                "chat": {"id": 123, "type": "private"},
                "date": 1640995200,
                "text": "How are you? 😊"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        assert response.status_code == 200
        
        # Verify that special characters were processed correctly
        mock_ask_llm.assert_called_once_with("How are you? 😊")
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.text == "Response with emojis! 🤖"
    
    def test_webhook_missing_message_field(self):
        """Test webhook without 'message' field"""
        webhook_payload = {
            "update_id": 123456789
            # Missing "message" field
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # With error handling, it should return 400
        assert response.status_code == 400
        error_detail = response.json()
        assert "detail" in error_detail
        assert "Invalid Telegram webhook payload" in error_detail["detail"]
    
    def test_webhook_missing_text_field(self):
        """Test webhook without 'text' field in the message"""
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 123, "first_name": "User"},
                "chat": {"id": 123, "type": "private"},
                "date": 1640995200
                # Missing "text" field
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # With error handling, it should return 400
        assert response.status_code == 400
        error_detail = response.json()
        assert "detail" in error_detail
        assert "Invalid Telegram webhook payload" in error_detail["detail"]
    
    def test_webhook_missing_chat_info(self):
        """Test webhook without chat information"""
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 123, "first_name": "User"},
                "date": 1640995200,
                "text": "Test message"
                # Missing "chat" field
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # With error handling, it should return 400
        assert response.status_code == 400
        error_detail = response.json()
        assert "detail" in error_detail
        assert "Invalid Telegram webhook payload" in error_detail["detail"]
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    @patch('app.api.ask_llm', new_callable=AsyncMock)
    def test_webhook_llm_service_error(self, mock_ask_llm, mock_send_telegram):
        """Test when the LLM service fails"""
        # Mock that raises an exception in ask_llm
        mock_ask_llm.side_effect = Exception("LLM service unavailable")
        
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 123, "first_name": "User"},
                "chat": {"id": 123, "type": "private"},
                "date": 1640995200,
                "text": "Test message"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # With error handling, it should return 500
        assert response.status_code == 500
        error_detail = response.json()
        assert "detail" in error_detail
        assert "Error processing query" in error_detail["detail"]
        
        # send_telegram_message should not have been called
        mock_send_telegram.assert_not_called()
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    @patch('app.api.ask_llm', new_callable=AsyncMock)
    def test_webhook_telegram_service_error(self, mock_ask_llm, mock_send_telegram):
        """Test when sending via Telegram fails"""
        mock_ask_llm.return_value = "LLM's response"
        
        # Mock that raises an exception in send_telegram_message
        mock_send_telegram.side_effect = Exception("Telegram send failed")
        
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 123, "first_name": "User"},
                "chat": {"id": 123, "type": "private"},
                "date": 1640995200,
                "text": "Test message"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # With error handling, it should return 500
        error_detail = response.json()
        assert "detail" in error_detail
        assert "Error sending response" in error_detail["detail"]
        
        # Verify that ask_llm was called but failed in send_telegram_message
        mock_ask_llm.assert_called_once()
        mock_send_telegram.assert_called_once()


class TestApiIntegration:
    """Integration tests for the endpoints"""
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    @patch('app.api.ask_llm', new_callable=AsyncMock)
    def test_full_conversation_flow(self, mock_ask_llm, mock_send_telegram):
        """Test the full flow: webhook -> LLM -> response"""
        # Configure mocks
        mock_ask_llm.return_value = "Paris is the capital of France"
        mock_send_telegram.return_value = {"ok": True, "result": {"message_id": 42}}
        
        # 1. Simulate incoming message via webhook
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 987654321, "first_name": "User"},
                "chat": {"id": 987654321, "type": "private"},
                "date": 1640995200,
                "text": "What is the capital of France?"
            }
        }
        
        # Process webhook
        webhook_response = client.post("/telegram/webhook", json=webhook_payload)
        
        # Verifications of the full flow
        assert webhook_response.status_code == 200
        assert webhook_response.json() == {"ok": True, "source": "llm"}
        
        # Verify that it was processed correctly
        mock_ask_llm.assert_called_once_with("What is the capital of France?")
        mock_send_telegram.assert_called_once()
        
        # 2. Verify that we could also send a manual message
        manual_payload = {
            "chat_id": "987654321",
            "text": "Manual test message"
        }
        
        manual_response = client.post("/telegram/send", json=manual_payload)
        assert manual_response.status_code == 200
        
        # Verify that send_telegram_message was called twice in total
        assert mock_send_telegram.call_count == 2


# Useful fixtures for API tests
@pytest.fixture
def sample_webhook_payload():
    """Fixture with a typical Telegram webhook payload"""
    return {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 987654321,
                "is_bot": False,
                "first_name": "TestUser",
                "username": "testuser"
            },
            "chat": {
                "id": 987654321,
                "first_name": "TestUser",
                "username": "testuser",
                "type": "private"
            },
            "date": 1640995200,
            "text": "Hello bot!"
        }
    }

@pytest.fixture
def sample_send_payload():
    """Fixture with a typical payload for the /send endpoint"""
    return {
        "chat_id": "123456789",
        "text": "Test message from fixture"
    }

# Test using fixtures
class TestApiWithFixtures:
    """Tests using fixtures for reusable data"""
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    @patch('app.api.ask_llm', new_callable=AsyncMock)
    def test_webhook_with_fixture(self, mock_ask_llm, mock_send_telegram, sample_webhook_payload):
        """Test webhook using a fixture"""
        mock_ask_llm.return_value = "Response from LLM"
        mock_send_telegram.return_value = {"ok": True}
        
        response = client.post("/telegram/webhook", json=sample_webhook_payload)
        
        assert response.status_code == 200
        mock_ask_llm.assert_called_once_with("Hello bot!")
    
    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    def test_send_with_fixture(self, mock_send_telegram, sample_send_payload):
        """Test /send endpoint using a fixture"""
        mock_send_telegram.return_value = {"ok": True, "result": {"message_id": 99}}
        
        response = client.post("/telegram/send", json=sample_send_payload)
        
        assert response.status_code == 200
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.text == "Test message from fixture"

class TestKafkaIntegration:
    """Tests for Kafka integration"""

    @patch('app.api.send_kafka_message')
    @patch('app.api.KAFKA_ENABLED', True)
    def test_webhook_with_kafka_enabled(self, mock_send_kafka_message, sample_webhook_payload):
        """Test that the webhook sends a message to Kafka when enabled"""
        response = client.post("/telegram/webhook", json=sample_webhook_payload)

        assert response.status_code == 200
        assert response.json() == {"ok": True, "source": "kafka"}
        mock_send_kafka_message.assert_called_once_with("Hello bot!", "987654321")

    @patch('app.api.send_telegram_message', new_callable=AsyncMock)
    def test_send_message_with_routing_id_header(self, mock_send_telegram):
        """Test /send endpoint with X-Routing-ID header"""
        # Mock the return value properly
        mock_send_telegram.return_value = {"ok": True, "result": {"message_id": 42}}
        
        payload = {"text": "Response from Kafka"}
        headers = {"X-Routing-ID": "telegram:12345"}

        response = client.post("/telegram/send", json=payload, headers=headers)

        assert response.status_code == 200
        mock_send_telegram.assert_called_once()
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.chat_id == "12345"
        assert called_msg.text == "Response from Kafka"

    def test_send_message_missing_routing_id_header(self):
        """Test /send endpoint with missing X-Routing-ID header"""
        payload = {"text": "Response from Kafka"}

        response = client.post("/telegram/send", json=payload)

        assert response.status_code == 400
        assert "chat_id is required" in response.json()["detail"]

    def test_send_message_invalid_routing_id_header(self):
        """Test /send endpoint with invalid X-Routing-ID header"""
        payload = {"text": "Response from Kafka"}
        headers = {"X-Routing-ID": "invalid-format"}

        response = client.post("/telegram/send", json=payload, headers=headers)

        assert response.status_code == 400
        assert "Invalid X-Routing-ID header format" in response.json()["detail"]
