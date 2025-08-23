import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Importar el router y dependencias
from app.api import router
from app.models import TelegramMessage

# Crear aplicación FastAPI para testing
app = FastAPI()
app.include_router(router, prefix="/telegram")
client = TestClient(app)

class TestSendMessageEndpoint:
    """Test suite para el endpoint /send"""
    
    @patch('app.api.send_telegram_message')
    def test_send_message_success(self, mock_send_telegram):
        """Test exitoso del endpoint /send"""
        # Mock de la respuesta de send_telegram_message
        mock_telegram_response = {
            "ok": True,
            "result": {
                "message_id": 42,
                "chat": {"id": 123456789},
                "text": "Test message"
            }
        }
        mock_send_telegram.return_value = mock_telegram_response
        
        # Payload de prueba
        payload = {
            "chat_id": "123456789",
            "text": "Hello, this is a test message!"
        }
        
        # Hacer request al endpoint
        response = client.post("/telegram/send", json=payload)
        
        # Verificaciones
        assert response.status_code == 200
        assert response.json() == mock_telegram_response
        
        # Verificar que se llamó send_telegram_message con los parámetros correctos
        mock_send_telegram.assert_called_once()
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.chat_id == "123456789"
        assert called_msg.text == "Hello, this is a test message!"
    
    @patch('app.api.send_telegram_message')
    def test_send_message_with_group_chat(self, mock_send_telegram):
        """Test enviando mensaje a chat grupal"""
        mock_telegram_response = {"ok": True, "result": {"message_id": 99}}
        mock_send_telegram.return_value = mock_telegram_response
        
        # Chat grupal (ID negativo)
        payload = {
            "chat_id": "-100123456789",
            "text": "Mensaje para el grupo"
        }
        
        response = client.post("/telegram/send", json=payload)
        
        assert response.status_code == 200
        assert response.json() == mock_telegram_response
        
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.chat_id == "-100123456789"
    
    @patch('app.api.send_telegram_message')
    def test_send_message_with_special_characters(self, mock_send_telegram):
        """Test enviando mensaje con caracteres especiales"""
        mock_telegram_response = {"ok": True}
        mock_send_telegram.return_value = mock_telegram_response
        
        payload = {
            "chat_id": "123456789",
            "text": "¡Hola! 🚀 Mensaje con émojis y acentos: ñáéíóú"
        }
        
        response = client.post("/telegram/send", json=payload)
        
        assert response.status_code == 200
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.text == "¡Hola! 🚀 Mensaje con émojis y acentos: ñáéíóú"
    
    def test_send_message_invalid_payload(self):
        """Test con payload inválido (faltan campos requeridos)"""
        # Payload sin chat_id
        payload = {"text": "Missing chat_id"}
        
        response = client.post("/telegram/send", json=payload)
        
        # FastAPI debería retornar error de validación
        assert response.status_code == 422
        error_detail = response.json()
        assert "detail" in error_detail
    
    def test_send_message_empty_text(self):
        """Test con texto vacío"""
        payload = {
            "chat_id": "123456789",
            "text": ""
        }
        
        response = client.post("/telegram/send", json=payload)
        
        # Dependiendo de la validación en TelegramMessage, 
        # esto podría ser 422 o pasar
        # Asumiendo que texto vacío es válido en el modelo
        assert response.status_code in [200, 422]
    
    @patch('app.api.send_telegram_message')
    def test_send_message_service_error(self, mock_send_telegram):
        """Test cuando el servicio de Telegram falla"""
        # Mock que lanza excepción
        mock_send_telegram.side_effect = Exception("Telegram API error")
        
        payload = {
            "chat_id": "123456789",
            "text": "Test message"
        }
        
        response = client.post("/telegram/send", json=payload)
        
        # Con el manejo de errores, debería retornar 500
        assert response.status_code == 500
        error_detail = response.json()
        assert "detail" in error_detail
        assert error_detail["detail"] == "Internal server error"


class TestTelegramWebhookEndpoint:
    """Test suite para el endpoint /webhook"""
    
    @patch('app.api.send_telegram_message')
    @patch('app.api.ask_llm')
    def test_webhook_success(self, mock_ask_llm, mock_send_telegram):
        """Test exitoso del webhook de Telegram"""
        # Mock de la respuesta del LLM
        mock_ask_llm.return_value = "Esta es la respuesta del LLM"
        
        # Mock de send_telegram_message
        mock_telegram_response = {"ok": True, "result": {"message_id": 42}}
        mock_send_telegram.return_value = mock_telegram_response
        
        # Payload simulando webhook de Telegram
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
                "text": "¿Cuál es la capital de Francia?"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # Verificaciones
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        
        # Verificar que se llamó ask_llm con el texto correcto
        mock_ask_llm.assert_called_once_with("¿Cuál es la capital de Francia?")
        
        # Verificar que se llamó send_telegram_message
        mock_send_telegram.assert_called_once()
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.chat_id == 987654321
        assert called_msg.text == "Esta es la respuesta del LLM"
    
    @patch('app.api.send_telegram_message')
    @patch('app.api.ask_llm')
    def test_webhook_group_chat(self, mock_ask_llm, mock_send_telegram):
        """Test webhook con mensaje de chat grupal"""
        mock_ask_llm.return_value = "Respuesta para el grupo"
        mock_send_telegram.return_value = {"ok": True}
        
        # Payload de chat grupal
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 987654321, "first_name": "User"},
                "chat": {
                    "id": -100123456789,  # Chat grupal
                    "title": "Grupo de Test",
                    "type": "group"
                },
                "date": 1640995200,
                "text": "Hola bot!"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        
        # Verificar chat_id grupal
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.chat_id == -100123456789
    
    @patch('app.api.send_telegram_message')
    @patch('app.api.ask_llm')
    def test_webhook_with_emojis_and_special_chars(self, mock_ask_llm, mock_send_telegram):
        """Test webhook con emojis y caracteres especiales"""
        mock_ask_llm.return_value = "¡Respuesta con émojis! 🤖"
        mock_send_telegram.return_value = {"ok": True}
        
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 123, "first_name": "User"},
                "chat": {"id": 123, "type": "private"},
                "date": 1640995200,
                "text": "¿Cómo estás? 😊"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        assert response.status_code == 200
        
        # Verificar que se procesaron correctamente los caracteres especiales
        mock_ask_llm.assert_called_once_with("¿Cómo estás? 😊")
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.text == "¡Respuesta con émojis! 🤖"
    
    def test_webhook_missing_message_field(self):
        """Test webhook sin campo 'message'"""
        webhook_payload = {
            "update_id": 123456789
            # Falta el campo "message"
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # Con el manejo de errores, debería retornar 400
        assert response.status_code == 400
        error_detail = response.json()
        assert "detail" in error_detail
        assert "message" in error_detail["detail"]
    
    def test_webhook_missing_text_field(self):
        """Test webhook sin campo 'text' en el mensaje"""
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 123, "first_name": "User"},
                "chat": {"id": 123, "type": "private"},
                "date": 1640995200
                # Falta el campo "text"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # Con el manejo de errores, debería retornar 400
        assert response.status_code == 400
        error_detail = response.json()
        assert "detail" in error_detail
        assert "text" in error_detail["detail"]
    
    def test_webhook_missing_chat_info(self):
        """Test webhook sin información del chat"""
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 123, "first_name": "User"},
                "date": 1640995200,
                "text": "Test message"
                # Falta el campo "chat"
            }
        }
        
        response = client.post("/telegram/webhook", json=webhook_payload)
        
        # Con el manejo de errores, debería retornar 400
        assert response.status_code == 400
        error_detail = response.json()
        assert "detail" in error_detail
        assert "chat" in error_detail["detail"]
    
    @patch('app.api.send_telegram_message')
    @patch('app.api.ask_llm')
    def test_webhook_llm_service_error(self, mock_ask_llm, mock_send_telegram):
        """Test cuando el servicio LLM falla"""
        # Mock que lanza excepción en ask_llm
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
        
        # Con el manejo de errores, debería retornar 500
        assert response.status_code == 500
        error_detail = response.json()
        assert "detail" in error_detail
        assert "Error processing query" in error_detail["detail"]
        
        # send_telegram_message no debería haber sido llamado
        mock_send_telegram.assert_not_called()
    
    @patch('app.api.send_telegram_message')
    @patch('app.api.ask_llm')
    def test_webhook_telegram_service_error(self, mock_ask_llm, mock_send_telegram):
        """Test cuando falla el envío por Telegram"""
        mock_ask_llm.return_value = "Respuesta del LLM"
        
        # Mock que lanza excepción en send_telegram_message
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
        
        # Con el manejo de errores, debería retornar 500
        assert response.status_code == 500
        error_detail = response.json()
        assert "detail" in error_detail
        assert "Error sending response" in error_detail["detail"]
        
        # Verificar que se llamó ask_llm pero falló en send_telegram_message
        mock_ask_llm.assert_called_once()
        mock_send_telegram.assert_called_once()


class TestApiIntegration:
    """Tests de integración para los endpoints"""
    
    @patch('app.api.send_telegram_message')
    @patch('app.api.ask_llm')
    def test_full_conversation_flow(self, mock_ask_llm, mock_send_telegram):
        """Test del flujo completo: webhook -> LLM -> respuesta"""
        # Configurar mocks
        mock_ask_llm.return_value = "París es la capital de Francia"
        mock_send_telegram.return_value = {"ok": True, "result": {"message_id": 42}}
        
        # 1. Simular mensaje entrante via webhook
        webhook_payload = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {"id": 987654321, "first_name": "User"},
                "chat": {"id": 987654321, "type": "private"},
                "date": 1640995200,
                "text": "¿Cuál es la capital de Francia?"
            }
        }
        
        # Procesar webhook
        webhook_response = client.post("/telegram/webhook", json=webhook_payload)
        
        # Verificaciones del flujo completo
        assert webhook_response.status_code == 200
        assert webhook_response.json() == {"ok": True}
        
        # Verificar que se procesó correctamente
        mock_ask_llm.assert_called_once_with("¿Cuál es la capital de Francia?")
        mock_send_telegram.assert_called_once()
        
        # 2. Verificar que también podríamos enviar un mensaje manual
        manual_payload = {
            "chat_id": "987654321",
            "text": "Mensaje manual de prueba"
        }
        
        manual_response = client.post("/telegram/send", json=manual_payload)
        assert manual_response.status_code == 200
        
        # Verificar que send_telegram_message se llamó dos veces en total
        assert mock_send_telegram.call_count == 2


# Fixtures útiles para los tests de API
@pytest.fixture
def sample_webhook_payload():
    """Fixture con payload típico de webhook de Telegram"""
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
    """Fixture con payload típico para endpoint /send"""
    return {
        "chat_id": "123456789",
        "text": "Test message from fixture"
    }

# Test usando fixtures
class TestApiWithFixtures:
    """Tests usando fixtures para datos reutilizables"""
    
    @patch('app.api.send_telegram_message')
    @patch('app.api.ask_llm')
    def test_webhook_with_fixture(self, mock_ask_llm, mock_send_telegram, sample_webhook_payload):
        """Test webhook usando fixture"""
        mock_ask_llm.return_value = "Response from LLM"
        mock_send_telegram.return_value = {"ok": True}
        
        response = client.post("/telegram/webhook", json=sample_webhook_payload)
        
        assert response.status_code == 200
        mock_ask_llm.assert_called_once_with("Hello bot!")
    
    @patch('app.api.send_telegram_message')
    def test_send_with_fixture(self, mock_send_telegram, sample_send_payload):
        """Test endpoint /send usando fixture"""
        mock_send_telegram.return_value = {"ok": True, "result": {"message_id": 99}}
        
        response = client.post("/telegram/send", json=sample_send_payload)
        
        assert response.status_code == 200
        called_msg = mock_send_telegram.call_args[0][0]
        assert called_msg.text == "Test message from fixture"
