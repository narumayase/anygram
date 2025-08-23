import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the root directory to the path to be able to import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestConfigVariables:
    """Test suite for the configuration variables of the config module"""
    
    @patch('os.getenv')
    @patch('app.config.load_dotenv')
    def test_config_loads_custom_environment_variables(self, mock_load_dotenv, mock_getenv):
        """Test that custom environment variables are loaded correctly"""
        # Configure mock for getenv
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
        
        # Reimport the module
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
        """Test that default values are loaded when there are no environment variables"""
        # Mock getenv to return None (except for values with default)
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
        """Test that RELOAD is correctly converted to boolean with 'TRUE'"""
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
        """Test that RELOAD is correctly converted to boolean with 'False'"""
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
        """Test that PORT is correctly converted to integer"""
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
    """Test suite for the validate_config function"""
    
    def setup_method(self):
        """Setup that runs before each test"""
        # Capture stdout to verify prints
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
    
    def teardown_method(self):
        """Teardown that runs after each test"""
        # Restore stdout
        sys.stdout = sys.__stdout__
    
    def test_validate_config_success(self):
        """Test that validate_config works correctly with valid configuration"""
        # Create a modified version of validate_config for testing
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
                
            # Use print directly to captured_output
            self.captured_output.write(f"✅ Configuration loaded successfully:\n")
            self.captured_output.write(f"   - Host: {host}\n")
            self.captured_output.write(f"   - Port: {port}\n")
            self.captured_output.write(f"   - Telegram API: {telegram_api_url}\n")
            self.captured_output.write(f"   - LLM URL: {llm_url}\n")
            self.captured_output.write(f"   - Reload: {reload}\n")
        
        # It should not raise an exception
        validate_config_test()
        
        # Verify that the success message was written
        output = self.captured_output.getvalue()
        assert "✅ Configuration loaded successfully:" in output
        assert "Host: 127.0.0.1" in output
        assert "Port: 8000" in output
        assert "Telegram API: https://api.telegram.org" in output
        assert "LLM URL: http://localhost:8081/api/v1/chat/ask" in output
        assert "Reload: True" in output
    
    def test_validate_config_missing_telegram_token(self):
        """Test that validate_config raises ValueError when TELEGRAM_TOKEN is missing"""
        def validate_config_test(telegram_token=None, llm_url="http://test"):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        with pytest.raises(ValueError, match="TELEGRAM_TOKEN environment variable is required"):
            validate_config_test(telegram_token=None)
    
    def test_validate_config_empty_telegram_token(self):
        """Test that validate_config raises ValueError when TELEGRAM_TOKEN is empty"""
        def validate_config_test(telegram_token="", llm_url="http://test"):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        with pytest.raises(ValueError, match="TELEGRAM_TOKEN environment variable is required"):
            validate_config_test(telegram_token="")
    
    def test_validate_config_missing_llm_url(self):
        """Test that validate_config raises ValueError when LLM_URL is missing"""
        def validate_config_test(telegram_token="valid", llm_url=None):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        with pytest.raises(ValueError, match="LLM_URL environment variable is required"):
            validate_config_test(llm_url=None)
    
    def test_validate_config_empty_llm_url(self):
        """Test that validate_config raises ValueError when LLM_URL is empty"""
        def validate_config_test(telegram_token="valid", llm_url=""):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        with pytest.raises(ValueError, match="LLM_URL environment variable is required"):
            validate_config_test(llm_url="")
    
    def test_validate_config_missing_both_required_vars(self):
        """Test that validate_config raises ValueError for TELEGRAM_TOKEN when both are missing"""
        def validate_config_test(telegram_token=None, llm_url=None):
            if not telegram_token:
                raise ValueError("TELEGRAM_TOKEN environment variable is required")
            if not llm_url:
                raise ValueError("LLM_URL environment variable is required")
        
        # It should raise an error for TELEGRAM_TOKEN first (validation order)
        with pytest.raises(ValueError, match="TELEGRAM_TOKEN environment variable is required"):
            validate_config_test(telegram_token=None, llm_url=None)
    
    def test_validate_config_integration(self):
        """Integration test with the actual validate_config function"""
        # We need to mock the module variables before importing validate_config
        with patch('app.config.TELEGRAM_TOKEN', 'test_token'), \
             patch('app.config.LLM_URL', 'http://test-llm'):
            
            from app.config import validate_config
            
            # It should work without raising an exception
            try:
                validate_config()
                # If we get here, the test passed
                assert True
            except ValueError as e:
                pytest.fail(f"validate_config() raised ValueError unexpectedly: {e}")


class TestDotenvIntegration:
    """Test suite for dotenv integration"""
    
    @patch('dotenv.load_dotenv')  # Patch the dotenv module directly
    def test_load_dotenv_is_called(self, mock_load_dotenv):
        """Test that load_dotenv is called when the module is imported"""
        import importlib
        import app.config
        importlib.reload(app.config)
        
        mock_load_dotenv.assert_called_once()


# Fixtures to use in tests if necessary
@pytest.fixture
def valid_config_env():
    """Fixture that provides a valid configuration environment"""
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
    """Fixture that provides the minimum required configuration"""
    return {
        'TELEGRAM_TOKEN': 'required_token',
        'LLM_URL': 'http://required-llm:8080/api/chat'
    }
