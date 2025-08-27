import pytest
import httpx
import json
from unittest.mock import AsyncMock, patch, MagicMock
from dataclasses import dataclass
import unittest.mock

# Import the functions to be tested
from app.services import send_telegram_message, ask_llm, send_kafka_message


# Mock for the message object used by send_telegram_message
@dataclass
class MockMessage:
    chat_id: str
    text: str


class TestSendTelegramMessage:
    """Test suite for the send_telegram_message function"""
    
    @pytest.mark.asyncio
    @patch('app.services.TELEGRAM_API_URL', 'https://api.telegram.org')
    @patch('app.services.TELEGRAM_TOKEN', 'test_bot_token_123')
    async def test_send_telegram_message_success(self):
        """Test that send_telegram_message sends a message correctly"""
        # Create a mock message
        mock_msg = MockMessage(chat_id="123456789", text="Hello, world!")
        
        # Successful mock response from the Telegram API
        mock_response_data = {
            "ok": True,
            "result": {
                "message_id": 42,
                "from": {"id": 123, "is_bot": True, "first_name": "TestBot"},
                "chat": {"id": 123456789, "type": "private"},
                "date": 1640995200,
                "text": "Hello, world!"
            }
        }
        
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        # Patch the AsyncClient
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            # Execute the function
            result = await send_telegram_message(mock_msg)
            
            # Verifications
            assert result == mock_response_data
            
            # Verify that the correct POST call was made
            expected_url = "https://api.telegram.org/bottest_bot_token_123/sendMessage"
            expected_payload = {"chat_id": "123456789", "text": "Hello, world!"}
            
            mock_client.post.assert_called_once_with(
                expected_url,
                json=expected_payload
            )
    
    @pytest.mark.asyncio
    @patch('app.services.TELEGRAM_API_URL', 'https://custom.telegram.api')
    @patch('app.services.TELEGRAM_TOKEN', 'custom_token_456')
    async def test_send_telegram_message_with_custom_config(self):
        """Test with custom Telegram API configuration"""
        mock_msg = MockMessage(chat_id="987654321", text="Custom message")
        
        mock_response_data = {"ok": True, "result": {"message_id": 99}}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            result = await send_telegram_message(mock_msg)
            
            assert result == mock_response_data
            
            # Verify custom URL
            expected_url = "https://custom.telegram.api/botcustom_token_456/sendMessage"
            expected_payload = {"chat_id": "987654321", "text": "Custom message"}
            
            mock_client.post.assert_called_once_with(
                expected_url,
                json=expected_payload
            )
    
    @pytest.mark.asyncio
    @patch('app.services.TELEGRAM_API_URL', 'https://api.telegram.org')
    @patch('app.services.TELEGRAM_TOKEN', 'test_token')
    async def test_send_telegram_message_with_special_characters(self):
        """Test sending a message with special characters"""
        mock_msg = MockMessage(
            chat_id="-100123456789",  # Group chat ID
            text="Hello! 🤖 Message with emojis and accents"
        )
        
        mock_response_data = {"ok": True}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            result = await send_telegram_message(mock_msg)
            
            assert result == mock_response_data
            
            # Verify that special characters are sent correctly
            expected_payload = {
                "chat_id": "-100123456789",
                "text": "Hello! 🤖 Message with emojis and accents"
            }
            
            mock_client.post.assert_called_once_with(
                "https://api.telegram.org/bottest_token/sendMessage",
                json=expected_payload
            )
    
    @pytest.mark.asyncio
    @patch('app.services.TELEGRAM_API_URL', 'https://api.telegram.org')
    @patch('app.services.TELEGRAM_TOKEN', 'test_token')
    async def test_send_telegram_message_api_error_response(self):
        """Test that it handles an error response from the Telegram API"""
        mock_msg = MockMessage(chat_id="123", text="Error test")
        
        # Telegram error response
        mock_error_response = {
            "ok": False,
            "error_code": 400,
            "description": "Bad Request: chat not found"
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_error_response
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            result = await send_telegram_message(mock_msg)
            
            # The function returns the response as it comes from the API
            assert result == mock_error_response
            assert result["ok"] == False
            assert result["error_code"] == 400


class TestAskLlm:
    """Test suite for the ask_llm function"""
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://localhost:8081/api/v1/chat/ask')
    async def test_ask_llm_success(self):
        """Test that ask_llm gets a response correctly from the LLM"""
        prompt = "What is the capital of France?"
        
        # Mock response from the LLM
        mock_llm_response = {
            "response": "The capital of France is Paris."
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_llm_response
        mock_response.raise_for_status.return_value = None  # No error
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            result = await ask_llm(prompt)
            
            assert result == "The capital of France is Paris."
            
            # Verify that the correct call was made
            expected_payload = {"prompt": "What is the capital of France?"}
            mock_client.post.assert_called_once_with(
                "http://localhost:8081/api/v1/chat/ask",
                json=expected_payload
            )
            mock_response.raise_for_status.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://custom-llm:9000/chat')
    async def test_ask_llm_with_custom_url(self):
        """Test ask_llm with a custom LLM URL"""
        prompt = "Test prompt"
        
        mock_llm_response = {"response": "Custom LLM response"}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_llm_response
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            result = await ask_llm(prompt)
            
            assert result == "Custom LLM response"
            
            # Verify custom URL
            mock_client.post.assert_called_once_with(
                "http://custom-llm:9000/chat",
                json={"prompt": "Test prompt"}
            )
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://localhost:8081/api/v1/chat/ask')
    async def test_ask_llm_with_long_prompt(self):
        """Test ask_llm with a long prompt"""
        long_prompt = "This is a very long prompt " * 100  # 3100+ characters
        
        mock_llm_response = {"response": "Response to a long prompt"}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_llm_response
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            result = await ask_llm(long_prompt)
            
            assert result == "Response to a long prompt"
            
            # Verify that the full prompt was sent
            expected_payload = {"prompt": long_prompt}
            mock_client.post.assert_called_once_with(
                "http://localhost:8081/api/v1/chat/ask",
                json=expected_payload
            )
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://localhost:8081/api/v1/chat/ask')
    async def test_ask_llm_http_error(self):
        """Test that ask_llm raises an exception on HTTP error"""
        prompt = "Test prompt"
        
        # Mock response that raises HTTPError
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=MagicMock(status_code=404)
        )
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(httpx.HTTPStatusError):
                await ask_llm(prompt)
            
            # Verify that the call was attempted
            mock_client.post.assert_called_once()
            mock_response.raise_for_status.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://localhost:8081/api/v1/chat/ask')
    async def test_ask_llm_connection_error(self):
        """Test that ask_llm handles connection errors"""
        prompt = "Test prompt"
        
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection failed")
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(httpx.ConnectError):
                await ask_llm(prompt)
            
            mock_client.post.assert_called_once_with(
                "http://localhost:8081/api/v1/chat/ask",
                json={"prompt": "Test prompt"}
            )
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://localhost:8081/api/v1/chat/ask')
    async def test_ask_llm_invalid_json_response(self):
        """Test ask_llm with an invalid JSON response"""
        prompt = "Test prompt"
        
        # Response that does not have a "response" field
        mock_llm_response = {"error": "Invalid response structure"}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_llm_response
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            with pytest.raises(KeyError):
                await ask_llm(prompt)


class TestSendKafkaMessage:
    """Test suite for the send_kafka_message function"""

    @patch('app.services.KafkaProducer')
    @patch('app.services.KAFKA_BROKER', 'localhost:9092')
    @patch('app.services.KAFKA_TOPIC', 'anygram.prompts')
    def test_send_kafka_message_success(self, mock_kafka_producer):
        """Test that send_kafka_message sends a message correctly to Kafka"""
        mock_producer_instance = MagicMock()
        mock_kafka_producer.return_value = mock_producer_instance
        
        prompt = "Test prompt for Kafka"
        chat_id = "12345"

        send_kafka_message(prompt, chat_id)

        # Check that KafkaProducer was instantiated correctly
        mock_kafka_producer.assert_called_once_with(
            bootstrap_servers='localhost:9092',
            value_serializer=unittest.mock.ANY
        )
        
        # Check that send was called with correct parameters
        mock_producer_instance.send.assert_called_once_with(
            'anygram.prompts',
            value={"prompt": prompt},
            headers=[('routing_id', f'telegram:{chat_id}'.encode('utf-8'))]
        )
        
        # Check that flush was called
        mock_producer_instance.flush.assert_called_once()


# Useful fixtures for reuse in tests
@pytest.fixture
def sample_message():
    """Fixture that provides a sample message"""
    return MockMessage(chat_id="123456789", text="Test message")


@pytest.fixture
def telegram_success_response():
    """Fixture with a successful response from the Telegram API"""
    return {
        "ok": True,
        "result": {
            "message_id": 42,
            "from": {"id": 123, "is_bot": True, "first_name": "TestBot"},
            "chat": {"id": 123456789, "type": "private"},
            "date": 1640995200,
            "text": "Test message"
        }
    }


@pytest.fixture
def llm_success_response():
    """Fixture with a successful response from the LLM"""
    return {"response": "This is the LLM's response"}


# Integration tests using fixtures
class TestServicesIntegration:
    """Integration tests for the service functions"""
    
    @pytest.mark.asyncio
    async def test_services_workflow(self, sample_message, telegram_success_response, llm_success_response):
        """Test the full flow: receive message, query LLM, respond"""
        # This test simulates the full flow that the application would use
        
        # Mock for ask_llm
        mock_llm_response = MagicMock()
        mock_llm_response.json.return_value = llm_success_response
        mock_llm_response.raise_for_status.return_value = None
        
        # Mock for send_telegram_message  
        mock_telegram_response = MagicMock()
        mock_telegram_response.json.return_value = telegram_success_response
        
        mock_client = AsyncMock()
        mock_client.post.side_effect = [mock_llm_response, mock_telegram_response]
        
        with patch('httpx.AsyncClient') as mock_async_client, \
             patch('app.services.LLM_URL', 'http://test-llm:8080/chat'), \
             patch('app.services.TELEGRAM_API_URL', 'https://api.telegram.org'), \
             patch('app.services.TELEGRAM_TOKEN', 'test_token'):
            
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            # 1. Query the LLM
            llm_response = await ask_llm(sample_message.text)
            assert llm_response == "This is the LLM's response"
            
            # 2. Create a response message
            response_message = MockMessage(
                chat_id=sample_message.chat_id,
                text=llm_response
            )
            
            # 3. Send the response via Telegram
            telegram_result = await send_telegram_message(response_message)
            assert telegram_result == telegram_success_response
            
            # Verify that both calls were made
            assert mock_client.post.call_count == 2