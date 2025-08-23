import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from dataclasses import dataclass

# Importar las funciones a testear
from app.services import send_telegram_message, ask_llm


# Mock para el objeto mensaje que usa send_telegram_message
@dataclass
class MockMessage:
    chat_id: str
    text: str


class TestSendTelegramMessage:
    """Test suite para la función send_telegram_message"""
    
    @pytest.mark.asyncio
    @patch('app.services.TELEGRAM_API_URL', 'https://api.telegram.org')
    @patch('app.services.TELEGRAM_TOKEN', 'test_bot_token_123')
    async def test_send_telegram_message_success(self):
        """Test que send_telegram_message envía mensaje correctamente"""
        # Crear mensaje mock
        mock_msg = MockMessage(chat_id="123456789", text="Hello, world!")
        
        # Respuesta mock exitosa de Telegram API
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
        
        # Mock del cliente httpx
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        # Patch del AsyncClient
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            # Ejecutar función
            result = await send_telegram_message(mock_msg)
            
            # Verificaciones
            assert result == mock_response_data
            
            # Verificar que se hizo la llamada POST correcta
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
        """Test con configuración personalizada de Telegram API"""
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
            
            # Verificar URL personalizada
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
        """Test envío de mensaje con caracteres especiales"""
        mock_msg = MockMessage(
            chat_id="-100123456789",  # Group chat ID
            text="¡Hola! 🤖 Mensaje con émojis y acentos"
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
            
            # Verificar que se envían los caracteres especiales correctamente
            expected_payload = {
                "chat_id": "-100123456789",
                "text": "¡Hola! 🤖 Mensaje con émojis y acentos"
            }
            
            mock_client.post.assert_called_once_with(
                "https://api.telegram.org/bottest_token/sendMessage",
                json=expected_payload
            )
    
    @pytest.mark.asyncio
    @patch('app.services.TELEGRAM_API_URL', 'https://api.telegram.org')
    @patch('app.services.TELEGRAM_TOKEN', 'test_token')
    async def test_send_telegram_message_api_error_response(self):
        """Test que maneja respuesta de error de la API de Telegram"""
        mock_msg = MockMessage(chat_id="123", text="Error test")
        
        # Respuesta de error de Telegram
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
            
            # La función devuelve la respuesta tal como viene de la API
            assert result == mock_error_response
            assert result["ok"] == False
            assert result["error_code"] == 400


class TestAskLlm:
    """Test suite para la función ask_llm"""
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://localhost:8081/api/v1/chat/ask')
    async def test_ask_llm_success(self):
        """Test que ask_llm obtiene respuesta correctamente del LLM"""
        prompt = "¿Cuál es la capital de Francia?"
        
        # Respuesta mock del LLM
        mock_llm_response = {
            "response": "La capital de Francia es París."
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_llm_response
        mock_response.raise_for_status.return_value = None  # No error
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            result = await ask_llm(prompt)
            
            assert result == "La capital de Francia es París."
            
            # Verificar que se hizo la llamada correcta
            expected_payload = {"prompt": "¿Cuál es la capital de Francia?"}
            mock_client.post.assert_called_once_with(
                "http://localhost:8081/api/v1/chat/ask",
                json=expected_payload
            )
            mock_response.raise_for_status.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://custom-llm:9000/chat')
    async def test_ask_llm_with_custom_url(self):
        """Test ask_llm con URL personalizada del LLM"""
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
            
            # Verificar URL personalizada
            mock_client.post.assert_called_once_with(
                "http://custom-llm:9000/chat",
                json={"prompt": "Test prompt"}
            )
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://localhost:8081/api/v1/chat/ask')
    async def test_ask_llm_with_long_prompt(self):
        """Test ask_llm con prompt largo"""
        long_prompt = "Este es un prompt muy largo " * 100  # 3100+ caracteres
        
        mock_llm_response = {"response": "Respuesta a prompt largo"}
        mock_response = MagicMock()
        mock_response.json.return_value = mock_llm_response
        mock_response.raise_for_status.return_value = None
        
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            result = await ask_llm(long_prompt)
            
            assert result == "Respuesta a prompt largo"
            
            # Verificar que se envió el prompt completo
            expected_payload = {"prompt": long_prompt}
            mock_client.post.assert_called_once_with(
                "http://localhost:8081/api/v1/chat/ask",
                json=expected_payload
            )
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://localhost:8081/api/v1/chat/ask')
    async def test_ask_llm_http_error(self):
        """Test que ask_llm lanza excepción en error HTTP"""
        prompt = "Test prompt"
        
        # Mock response que lanza HTTPError
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
            
            # Verificar que se intentó hacer la llamada
            mock_client.post.assert_called_once()
            mock_response.raise_for_status.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.services.LLM_URL', 'http://localhost:8081/api/v1/chat/ask')
    async def test_ask_llm_connection_error(self):
        """Test que ask_llm maneja errores de conexión"""
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
        """Test ask_llm con respuesta JSON inválida"""
        prompt = "Test prompt"
        
        # Response que no tiene campo "response"
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


# Fixtures útiles para reutilizar en tests
@pytest.fixture
def sample_message():
    """Fixture que proporciona un mensaje de ejemplo"""
    return MockMessage(chat_id="123456789", text="Test message")


@pytest.fixture
def telegram_success_response():
    """Fixture con respuesta exitosa de Telegram API"""
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
    """Fixture con respuesta exitosa del LLM"""
    return {"response": "Esta es la respuesta del LLM"}


# Tests de integración usando las fixtures
class TestServicesIntegration:
    """Tests de integración para las funciones de servicios"""
    
    @pytest.mark.asyncio
    async def test_services_workflow(self, sample_message, telegram_success_response, llm_success_response):
        """Test del flujo completo: recibir mensaje, consultar LLM, responder"""
        # Este test simula el flujo completo que usaría la aplicación
        
        # Mock para ask_llm
        mock_llm_response = MagicMock()
        mock_llm_response.json.return_value = llm_success_response
        mock_llm_response.raise_for_status.return_value = None
        
        # Mock para send_telegram_message  
        mock_telegram_response = MagicMock()
        mock_telegram_response.json.return_value = telegram_success_response
        
        mock_client = AsyncMock()
        mock_client.post.side_effect = [mock_llm_response, mock_telegram_response]
        
        with patch('httpx.AsyncClient') as mock_async_client, \
             patch('app.services.LLM_URL', 'http://test-llm:8080/chat'), \
             patch('app.services.TELEGRAM_API_URL', 'https://api.telegram.org'), \
             patch('app.services.TELEGRAM_TOKEN', 'test_token'):
            
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            # 1. Consultar al LLM
            llm_response = await ask_llm(sample_message.text)
            assert llm_response == "Esta es la respuesta del LLM"
            
            # 2. Crear mensaje de respuesta
            response_message = MockMessage(
                chat_id=sample_message.chat_id,
                text=llm_response
            )
            
            # 3. Enviar respuesta por Telegram
            telegram_result = await send_telegram_message(response_message)
            assert telegram_result == telegram_success_response
            
            # Verificar que se hicieron ambas llamadas
            assert mock_client.post.call_count == 2