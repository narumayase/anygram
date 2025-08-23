import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app, healthcheck

client = TestClient(app)

class TestHealthCheck:
    """Test suite for the /health endpoint"""

    def test_healthcheck_returns_ok(self):
        """Tests that the healthcheck endpoint returns a 200 status code and a valid JSON response."""
        response = client.get("/health")
        assert response.status_code == 200
        
        json_response = response.json()
        assert json_response["message"] == "anygram API is working!"
        assert json_response["status"] == "ok"
        assert "host" in json_response
        assert "port" in json_response

    def test_healthcheck_content_type(self):
        """Tests that the healthcheck endpoint returns the correct content type."""
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]

class TestGenericExceptionHandler:
    """Test suite for the generic exception handler"""

    def test_generic_exception_handler(self):
        # Create a new TestClient with the app's exception handlers
        client = TestClient(app, raise_server_exceptions=False)

        # Create a temporary route that raises an exception
        @app.get("/error-test")
        async def error_test():
            raise Exception("A wild exception appeared!")

        response = client.get("/error-test")

        # Clean up the temporary route
        app.routes.pop()

        assert response.status_code == 500
        json_response = response.json()
        assert "detail" in json_response
        assert json_response["detail"] == "A wild exception appeared!"
