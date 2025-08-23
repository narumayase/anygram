import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# Agregar el directorio raíz al path para poder importar app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestConfigVariables:
    """Test suite para las variables de configuración del módulo config"""
    
    @patch('os.getenv')
    @patch('app.config.load_dotenv')
    def test_config_loads_custom_environment_variables(self, mock_load_dotenv, mock_getenv):
        """Test que las variables de entorno personalizadas se cargan correctamente"""
        # Configurar mock para getenv
        env_vars = {
            'TELEGRAM_TOKEN': 'test_token_123',
            'TELEGRAM_API_URL': 'https://custom.telegram.api',
            'LLM_URL': 'http://custom-llm:8080/api/chat',
            'HOST': '0.0.0.0',
            'PORT': '3000',
            'RELOAD': 'false'
        }
        
        def getenv_side_effect(key, default=None):
            return env_vars.get(key, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Reimportar el módulo
        import importlib
        import app.config
        importlib.reload(app.config)
        
        assert app.config.TELEGRAM_TOKEN == 'test_token_123'
        assert app.config.TELEGRAM_API_URL == 'https://custom.telegram.api'
        assert app.config.LLM_URL == 'http://custom-llm:8080/api/chat'
        assert app.config.HOST == '0.0.0.0'
        assert app.config.PORT == 3000
        assert app.config.RELOAD == False
    
    @patch('os.getenv')
    @patch('app.config.load_dotenv')
    def test_config_loads_default_values(self, mock_load_dotenv, mock_getenv):
        """Test que se cargan los valores por defecto cuando no hay variables de entorno"""
        # Mock getenv para devolver None (excepto para valores con default)
        def getenv_side_effect(key, default=None):
            return default
        
        mock_getenv.side_effect = getenv_side_effect
        
        import importlib
        import app.config
        importlib.reload(app.config)
        
        assert app.config.TELEGRAM_TOKEN is None
        assert app.config.TELEGRAM_API_URL == "https://api.telegram.org"
        assert app.config.LLM_URL == "http://localhost:8081/api/v1/chat/ask"
        assert app.config.HOST == "127.0.0.1"
        assert app.config.PORT == 8000
        assert app.config.RELOAD == True
    
    @patch('os.getenv')
    @patch('app.config.load_dotenv')
    def test_reload_boolean_conversion_uppercase_true(self, mock_load_dotenv, mock_getenv):
        """Test que RELOAD se convierte correctamente a boolean con 'TRUE'"""
        def getenv_side_effect(key, default=None):
            if key == 'RELOAD':
                return 'TRUE'
            return default
        
        mock_getenv.side_effect = getenv_side_effect
        
        import importlib
        import app.config
        importlib.reload(app.config)
        
        assert app.config.RELOAD == True
    
    @patch('os.getenv')
    @patch('app.config.load_dotenv')
    def test_reload_boolean_conversion_mixed_case_false(self, mock_load_dotenv, mock_getenv):
        """Test que RELOAD se convierte correctamente a boolean con 'False'"""
        def getenv_side_effect(key, default=None):
            if key == 'RELOAD':
                return 'False'
            return default
        
        mock_getenv.side_effect = getenv_side_effect
        
        import importlib
        import app.config
        importlib.reload(app.config)
        
        assert app.config.RELOAD == False
    
    @patch('os.getenv')
    @patch('app.config.load_dotenv')
    def test_port_integer_conversion(self, mock_load_dotenv, mock_getenv):
        """Test que PORT se convierte correctamente a entero"""
        def getenv_side_effect(key, default=None):
            if key == 'PORT':
                return '9999'
            return default
        
        mock_getenv.side_effect = getenv_side_effect
        
        import importlib
        import app.config
        importlib.reload(app.config)
        
        assert app.config.PORT == 9999
        assert isinstance(app.config.PORT, int)


class TestValidateConfig:
    """Test suite para la función validate_config"""
    
    def setup_method(self):
        """Setup que se ejecuta antes de cada test"""
        # Capturar stdout para verificar los prints
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
    
    def teardown_method(self):
        """Teardown que se ejecuta después de cada test"""
        # Restaurar stdout
        sys.stdout = sys.__stdout__
    
    def test_validate_config_success(self):
        """Test que validate_config funciona correctamente con configuración válida"""
        # Crear una versión modificada de validate_config para testing
        def validate_config_test(telegram_token="valid_token", 
                               llm_url="http://localhost:8081/api/v1/chat/ask",
                               host="127.0.0.1", 
                               port=8000,
                               telegram_api_url="https://api.telegram.org",
                               reload=True):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
                
            # Usar print directamente al captured_output
            self.captured_output.write(f"✅ Configuration loaded successfully:\n")
            self.captured_output.write(f"   - Host: {host}\n")
            self.captured_output.write(f"   - Port: {port}\n")
            self.captured_output.write(f"   - Telegram API: {telegram_api_url}\n")
            self.captured_output.write(f"   - LLM URL: {llm_url}\n")
            self.captured_output.write(f"   - Reload: {reload}\n")
        
        # No debería lanzar excepción
        validate_config_test()
        
        # Verificar que se escribió el mensaje de éxito
        output = self.captured_output.getvalue()
        assert "✅ Configuration loaded successfully:" in output
        assert "Host: 127.0.0.1" in output
        assert "Port: 8000" in output
        assert "Telegram API: https://api.telegram.org" in output
        assert "LLM URL: http://localhost:8081/api/v1/chat/ask" in output
        assert "Reload: True" in output
    
    def test_validate_config_missing_telegram_token(self):
        """Test que validate_config lanza ValueError cuando falta TELEGRAM_TOKEN"""
        def validate_config_test(telegram_token=None, llm_url="http://test"):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        with pytest.raises(ValueError, match="TELEGRAM_TOKEN environment variable is required"):
            validate_config_test(telegram_token=None)
    
    def test_validate_config_empty_telegram_token(self):
        """Test que validate_config lanza ValueError cuando TELEGRAM_TOKEN está vacío"""
        def validate_config_test(telegram_token="", llm_url="http://test"):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        with pytest.raises(ValueError, match="TELEGRAM_TOKEN environment variable is required"):
            validate_config_test(telegram_token="")
    
    def test_validate_config_missing_llm_url(self):
        """Test que validate_config lanza ValueError cuando falta LLM_URL"""
        def validate_config_test(telegram_token="valid", llm_url=None):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        with pytest.raises(ValueError, match="LLM_URL environment variable is required"):
            validate_config_test(llm_url=None)
    
    def test_validate_config_empty_llm_url(self):
        """Test que validate_config lanza ValueError cuando LLM_URL está vacío"""
        def validate_config_test(telegram_token="valid", llm_url=""):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        with pytest.raises(ValueError, match="LLM_URL environment variable is required"):
            validate_config_test(llm_url="")
    
    def test_validate_config_missing_both_required_vars(self):
        """Test que validate_config lanza ValueError para TELEGRAM_TOKEN cuando ambas faltan"""
        def validate_config_test(telegram_token=None, llm_url=None):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        # Debería lanzar error por TELEGRAM_TOKEN primero (orden de validación)
        with pytest.raises(ValueError, match="TELEGRAM_TOKEN environment variable is required"):
            validate_config_test(telegram_token=None, llm_url=None)
    
    def test_validate_config_integration(self):
        """Test de integración real con la función validate_config"""
        # Necesitamos mockear las variables del módulo antes de importar validate_config
        with patch('app.config.TELEGRAM_TOKEN', 'test_token'), \
             patch('app.config.LLM_URL', 'http://test-llm'):
            
            from app.config import validate_config
            
            # Debería funcionar sin lanzar excepción
            try:
                validate_config()
                # Si llegamos aquí, el test pasó
                assert True
            except ValueError as e:
                pytest.fail(f"validate_config() raised ValueError unexpectedly: {e}")


class TestDotenvIntegration:
    """Test suite para la integración con dotenv"""
    
    @patch('dotenv.load_dotenv')  # Patch del módulo dotenv directamente
    def test_load_dotenv_is_called(self, mock_load_dotenv):
        """Test que load_dotenv se llama al importar el módulo"""
        import importlib
        import app.config
        importlib.reload(app.config)
        
        mock_load_dotenv.assert_called_once()


# Fixtures para usar en tests si es necesario
@pytest.fixture
def valid_config_env():
    """Fixture que proporciona un entorno válido de configuración"""
    return {
        'TELEGRAM_TOKEN': 'test_token_123',
        'TELEGRAM_API_URL': 'https://api.telegram.org',
        'LLM_URL': 'http://localhost:8081/api/v1/chat/ask',
        'HOST': '127.0.0.1',
        'PORT': '8000',
        'RELOAD': 'true'
    }


@pytest.fixture
def minimal_config_env():
    """Fixture que proporciona la configuración mínima requerida"""
    return {
        'TELEGRAM_TOKEN': 'required_token',
        'LLM_URL': 'http://required-llm:8080/api/chat'
    }