"""
Tests para excepciones de Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO testea lógica de generación
- NO testea agentes directamente
- SÍ testea manejo de errores específicos de CLI
- SÍ testea mensajes de error elegantes
- Enfocado en UX/UI para manejo de errores
"""

import pytest
from rich.console import Console
from unittest.mock import Mock, patch

from genesis_cli.exceptions import (
    GenesisCliException,
    ValidationError,
    ProjectNameError,
    TemplateError,
    DirectoryError,
    DependencyError,
    ConfigurationError,
    UserInterruptError,
    NetworkError,
    GenesisCoreCommunicationError,
    CommandError,
    ProjectNotFoundError,
    IncompatibleVersionError,
    raise_validation_error,
    raise_project_name_error,
    raise_template_error,
    raise_directory_error,
    raise_dependency_error,
    raise_configuration_error,
    raise_user_interrupt_error,
    raise_network_error,
    raise_genesis_core_error,
    raise_command_error,
    raise_project_not_found_error,
    raise_incompatible_version_error,
    handle_cli_exception
)


class TestGenesisCliException:
    """
    Tests para excepción base GenesisCliException
    
    DOCTRINA: Solo maneja errores de interfaz de usuario
    """
    
    def test_genesis_cli_exception_basic(self):
        """Test excepción básica"""
        exc = GenesisCliException("Test error message")
        
        assert str(exc) == "Test error message"
        assert exc.message == "Test error message"
        assert exc.details == {}
    
    def test_genesis_cli_exception_with_details(self):
        """Test excepción con detalles"""
        details = {"field": "value", "context": "test"}
        exc = GenesisCliException("Test error", details=details)
        
        assert exc.message == "Test error"
        assert exc.details == details
    
    def test_genesis_cli_exception_formatted_message(self):
        """Test mensaje formateado"""
        exc = GenesisCliException("Test error")
        formatted = exc.get_formatted_message()
        
        assert formatted == "❌ Test error"
    
    def test_genesis_cli_exception_inheritance(self):
        """Test herencia de Exception"""
        exc = GenesisCliException("Test error")
        
        assert isinstance(exc, Exception)
        assert isinstance(exc, GenesisCliException)


class TestValidationError:
    """
    Tests para ValidationError
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def test_validation_error_basic(self):
        """Test error de validación básico"""
        exc = ValidationError("Invalid input")
        
        assert str(exc) == "Invalid input"
        assert exc.message == "Invalid input"
        assert exc.field is None
        assert exc.errors == []
    
    def test_validation_error_with_field(self):
        """Test error de validación con campo"""
        exc = ValidationError("Invalid value", field="username")
        
        assert exc.field == "username"
        assert exc.message == "Invalid value"
    
    def test_validation_error_with_errors(self):
        """Test error de validación con lista de errores"""
        errors = ["Error 1", "Error 2", "Error 3"]
        exc = ValidationError("Multiple errors", errors=errors)
        
        assert exc.e