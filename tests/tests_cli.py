"""
Tests para Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO testea lógica de generación
- NO testea agentes directamente
- SÍ testea interfaz de usuario
- SÍ testea validación de entrada
- SÍ testea comunicación con genesis-core
- Solo testea funcionalidad de CLI
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from typer.testing import CliRunner
from click.testing import Result

from genesis_cli.main import app
from genesis_cli.validators import (
    validate_project_name,
    validate_template,
    validate_directory,
    validate_features,
    ValidationResult
)
from genesis_cli.exceptions import (
    ProjectNameError,
    TemplateError,
    ValidationError,
    GenesisCliException
)
from genesis_cli.config import CLIConfig, CLIConfigManager
from genesis_cli.utils import (
    get_terminal_size,
    is_interactive_terminal,
    get_user_confirmation,
    validate_project_name as util_validate_project_name
)

# Configurar runner para tests
runner = CliRunner()

class TestCLIBasic:
    """
    Tests básicos de CLI
    
    DOCTRINA: Solo testea interfaz de usuario
    """
    
    def test_version_command(self):
        """Test comando --version"""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "Genesis CLI" in result.output
        assert "v1.0.0" in result.output
    
    def test_help_command(self):
        """Test comando --help"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Genesis CLI" in result.output
        assert "init" in result.output
        assert "deploy" in result.output
        assert "generate" in result.output
        assert "status" in result.output
        assert "doctor" in result.output
    
    def test_no_args_shows_help(self):
        """Test que sin argumentos muestra ayuda"""
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Genesis CLI" in result.output or "Bienvenido" in result.output

class TestInitCommand:
    """
    Tests para comando init
    
    DOCTRINA: Solo testea interfaz de usuario y validación
    """
    
    @patch('genesis_cli.main.CoreOrchestrator')
    def test_init_basic_project(self, mock_orchestrator):
        """Test creación básica de proyecto"""
        # Mock del orquestador
        mock_instance = Mock()
        mock_instance.execute_project_generation = AsyncMock(return_value=Mock(
            success=True,
            project_path="/tmp/test-project",
            generated_files=["file1.py", "file2.js"],
            data={}
        ))
        mock_orchestrator.return_value = mock_instance
        
        # Ejecutar comando
        result = runner.invoke(app, [
            "init", "test-project",
            "--template=saas-basic",
            "--no-interactive",
            "--skip-project-check"
        ])
        
        # Verificar resultado
        assert result.exit_code == 0
        assert "test-project" in result.output
        assert "creado exitosamente" in result.output or "successfully" in result.output
        
        # Verificar que se llamó al orquestador
        mock_orchestrator.assert_called_once()
        mock_instance.execute_project_generation.assert_called_once()
    
    def test_init_invalid_project_name(self):
        """Test nombre de proyecto inválido"""
        result = runner.invoke(app, [
            "init", "123-invalid",
            "--no-interactive"
        ])
        
        assert result.exit_code == 1
        assert "inválido" in result.output or "invalid" in result.output
    
    def test_init_invalid_template(self):
        """Test template inválido"""
        result = runner.invoke(app, [
            "init", "test-project",
            "--template=invalid-template",
            "--no-interactive"
        ])
        
        assert result.exit_code == 1
        assert "inválido" in result.output or "invalid" in result.output
    
    @patch('genesis_cli.main.CoreOrchestrator')
    def test_init_with_features(self, mock_orchestrator):
        """Test init con características específicas"""
        # Mock del orquestador
        mock_instance = Mock()
        mock_instance.execute_project_generation = AsyncMock(return_value=Mock(
            success=True,
            project_path="/tmp/test-project",
            generated_files=["file1.py"],
            data={}
        ))
        mock_orchestrator.return_value = mock_instance
        
        # Ejecutar comando
        result = runner.invoke(app, [
            "init", "test-project",
            "--template=saas-basic",
            "--no-interactive",
            "--skip-project-check"
        ])
        
        assert result.exit_code == 0
        
        # Verificar que se pasaron las características correctas
        call_args = mock_instance.execute_project_generation.call_args[0][0]
        assert call_args.features == ["authentication", "database", "api", "frontend", "docker", "cicd"]
    
    @patch('genesis_cli.main.CoreOrchestrator')
    def test_init_directory_exists_force(self, mock_orchestrator):
        """Test init con directorio existente y force"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear directorio existente
            existing_dir = Path(temp_dir) / "existing-project"
            existing_dir.mkdir()
            
            # Mock del orquestador
            mock_instance = Mock()
            mock_instance.execute_project_generation = AsyncMock(return_value=Mock(
                success=True,
                project_path=str(existing_dir),
                generated_files=["file1.py"],
                data={}
            ))
            mock_orchestrator.return_value = mock_instance
            
            # Ejecutar comando con force
            result = runner.invoke(app, [
                "init", "existing-project",
                "--template=saas-basic",
                "--no-interactive",
                "--force",
                "--output", temp_dir,
                "--skip-project-check"
            ])
            
            assert result.exit_code == 0

class TestDeployCommand:
    """
    Tests para comando deploy
    
    DOCTRINA: Solo testea interfaz de usuario
    """
    
    @patch('genesis_cli.main.CoreOrchestrator')
    def test_deploy_local(self, mock_orchestrator):
        """Test despliegue local"""
        # Mock del orquestador
        mock_instance = Mock()
        mock_instance.execute_deployment = AsyncMock(return_value=Mock(
            success=True,
            deployment_url="http://localhost:3000",
            data={}
        ))
        mock_orchestrator.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear genesis.json
            genesis_file = Path(temp_dir) / "genesis.json"
            with open(genesis_file, 'w') as f:
                json.dump({"name": "test-project"}, f)
            
            # Cambiar al directorio temporal
            original_cwd = Path.cwd()
            try:
                import os
                os.chdir(temp_dir)
                
                # Ejecutar comando
                result = runner.invoke(app, [
                    "deploy", "--env=local",
                    "--skip-project-check"
                ])
                
                assert result.exit_code == 0
                assert "exitoso" in result.output or "success" in result.output
                
            finally:
                os.chdir(original_cwd)
    
    def test_deploy_without_project(self):
        """Test deploy sin proyecto Genesis"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os
                os.chdir(temp_dir)
                
                # Ejecutar comando sin genesis.json
                result = runner.invoke(app, ["deploy", "--env=local"])
                
                assert result.exit_code == 1
                assert "proyecto Genesis" in result.output
                
            finally:
                os.chdir(original_cwd)
    
    def test_deploy_invalid_environment(self):
        """Test deploy con entorno inválido"""
        result = runner.invoke(app, [
            "deploy", "--env=invalid-env",
            "--skip-project-check"
        ])
        
        assert result.exit_code == 1
        assert "inválido" in result.output or "invalid" in result.output

class TestGenerateCommand:
    """
    Tests para comando generate
    
    DOCTRINA: Solo testea interfaz de usuario
    """
    
    @patch('genesis_cli.main.CoreOrchestrator')
    def test_generate_model(self, mock_orchestrator):
        """Test generación de modelo"""
        # Mock del orquestador
        mock_instance = Mock()
        mock_instance.execute_component_generation = AsyncMock(return_value=Mock(
            success=True,
            generated_files=["models/user.py", "tests/test_user.py"],
            data={}
        ))
        mock_orchestrator.return_value = mock_instance
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear genesis.json
            genesis_file = Path(temp_dir) / "genesis.json"
            with open(genesis_file, 'w') as f:
                json.dump({"name": "test-project"}, f)
            
            original_cwd = Path.cwd()
            try:
                import os
                os.chdir(temp_dir)
                
                # Ejecutar comando
                result = runner.invoke(app, [
                    "generate", "model", "User",
                    "--no-interactive",
                    "--skip-project-check"
                ])
                
                assert result.exit_code == 0
                assert "generado exitosamente" in result.output or "successfully" in result.output
                
            finally:
                os.chdir(original_cwd)
    
    def test_generate_invalid_component(self):
        """Test generate con componente inválido"""
        result = runner.invoke(app, [
            "generate", "invalid-component", "Test",
            "--skip-project-check"
        ])
        
        assert result.exit_code == 1
        assert "inválido" in result.output or "invalid" in result.output
    
    def test_generate_invalid_name(self):
        """Test generate con nombre inválido"""
        result = runner.invoke(app, [
            "generate", "model", "123-invalid",
            "--skip-project-check"
        ])
        
        assert result.exit_code == 1
        assert "inválido" in result.output or "invalid" in result.output

class TestStatusCommand:
    """
    Tests para comando status
    
    DOCTRINA: Solo testea interfaz de usuario
    """
    
    def test_status_with_project(self):
        """Test status con proyecto existente"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear genesis.json
            genesis_file = Path(temp_dir) / "genesis.json"
            project_data = {
                "name": "test-project",
                "template": "saas-basic",
                "version": "1.0.0",
                "features": ["authentication", "database"],
                "generated_files": ["file1.py", "file2.js"]
            }
            with open(genesis_file, 'w') as f:
                json.dump(project_data, f)
            
            original_cwd = Path.cwd()
            try:
                import os
                os.chdir(temp_dir)
                
                # Ejecutar comando
                result = runner.invoke(app, [
                    "status",
                    "--skip-project-check"
                ])
                
                assert result.exit_code == 0
                assert "test-project" in result.output
                assert "saas-basic" in result.output
                
            finally:
                os.chdir(original_cwd)
    
    def test_status_without_project(self):
        """Test status sin proyecto Genesis"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                import os
                os.chdir(temp_dir)
                
                # Ejecutar comando sin genesis.json
                result = runner.invoke(app, ["status"])
                
                assert result.exit_code == 1
                assert "proyecto Genesis" in result.output
                
            finally:
                os.chdir(original_cwd)

class TestDoctorCommand:
    """
    Tests para comando doctor
    
    DOCTRINA: Solo testea interfaz de usuario
    """
    
    @patch('genesis_cli.main.CoreOrchestrator')
    @patch('genesis_cli.commands.utils.check_dependencies')
    def test_doctor_success(self, mock_check_deps, mock_orchestrator):
        """Test doctor exitoso"""
        # Mock dependencias
        mock_check_deps.return_value = True
        
        # Mock orquestador
        mock_orchestrator.return_value = Mock()
        
        # Ejecutar comando
        result = runner.invoke(app, ["doctor"])
        
        assert result.exit_code == 0
        assert "listo" in result.output or "ready" in result.output
    
    @patch('genesis_cli.main.CoreOrchestrator')
    @patch('genesis_cli.commands.utils.check_dependencies')
    def test_doctor_missing_dependencies(self, mock_check_deps, mock_orchestrator):
        """Test doctor con dependencias faltantes"""
        # Mock dependencias faltantes
        mock_check_deps.return_value = False
        
        # Mock orquestrador
        mock_orchestrator.return_value = Mock()
        
        # Ejecutar comando
        result = runner.invoke(app, ["doctor"])
        
        assert result.exit_code == 1
        assert "no está listo" in result.output or "not ready" in result.output

class TestValidators:
    """
    Tests para validadores
    
    DOCTRINA: SÍ testea validación de entrada del usuario
    """
    
    def test_validate_project_name_valid(self):
        """Test validación de nombre válido"""
        result = validate_project_name("mi-proyecto")
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_project_name_invalid_start(self):
        """Test validación de nombre que comienza con número"""
        result = validate_project_name("123-proyecto")
        assert not result.is_valid
        assert "debe comenzar con una letra" in str(result.errors)
    
    def test_validate_project_name_too_short(self):
        """Test validación de nombre muy corto"""
        result = validate_project_name("a")
        assert not result.is_valid
        assert "al menos 2 caracteres" in str(result.errors)
    
    def test_validate_project_name_too_long(self):
        """Test validación de nombre muy largo"""
        long_name = "a" * 51
        result = validate_project_name(long_name)
        assert not result.is_valid
        assert "más de 50 caracteres" in str(result.errors)
    
    def test_validate_project_name_reserved(self):
        """Test validación de nombre reservado"""
        result = validate_project_name("con")
        assert not result.is_valid
        assert "reservado" in str(result.errors)
    
    def test_validate_template_valid(self):
        """Test validación de template válido"""
        result = validate_template("saas-basic")
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_template_invalid(self):
        """Test validación de template inválido"""
        result = validate_template("invalid-template")
        assert not result.is_valid
        assert "no encontrado" in str(result.errors)
    
    def test_validate_features_valid(self):
        """Test validación de características válidas"""
        result = validate_features(["authentication", "database", "api"])
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_features_invalid(self):
        """Test validación de características inválidas"""
        result = validate_features(["invalid-feature"])
        assert not result.is_valid
        assert "inválidas" in str(result.errors)
    
    def test_validate_directory_valid(self):
        """Test validación de directorio válido"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validate_directory(temp_dir, "new-project")
            assert result.is_valid
            assert len(result.errors) == 0
    
    def test_validate_directory_nonexistent(self):
        """Test validación de directorio inexistente"""
        result = validate_directory("/nonexistent/path", "project")
        assert not result.is_valid
        assert "no existe" in str(result.errors)

class TestConfiguration:
    """
    Tests para configuración
    
    DOCTRINA: Solo testea configuración de CLI
    """
    
    def test_cli_config_creation(self):
        """Test creación de configuración CLI"""
        config = CLIConfig()
        assert config.theme == "default"
        assert config.interactive_mode == True
        assert config.default_template == "saas-basic"
    
    def test_cli_config_from_dict(self):
        """Test creación de configuración desde diccionario"""
        config_dict = {
            "ui": {"theme": "dark"},
            "behavior": {"interactive_mode": False},
            "templates": {"default_template": "api-only"}
        }
        config = CLIConfig.from_dict(config_dict)
        assert config.theme == "dark"
        assert config.interactive_mode == False
        assert config.default_template == "api-only"
    
    def test_cli_config_to_dict(self):
        """Test conversión de configuración a diccionario"""
        config = CLIConfig(theme="dark", interactive_mode=False)
        config_dict = config.to_dict()
        assert config_dict["ui"]["theme"] == "dark"
        assert config_dict["behavior"]["interactive_mode"] == False
    
    def test_config_manager_load_default(self):
        """Test carga de configuración por defecto"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear manager con directorio temporal
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Cargar configuración (debería usar defaults)
            config = manager.load_config()
            assert config.theme == "default"
            assert config.interactive_mode == True

class TestUtils:
    """
    Tests para utilidades
    
    DOCTRINA: Solo testea utilities de UX/UI
    """
    
    def test_get_terminal_size(self):
        """Test obtención de tamaño de terminal"""
        width, height = get_terminal_size()
        assert isinstance(width, int)
        assert isinstance(height, int)
        assert width > 0
        assert height > 0
    
    def test_is_interactive_terminal(self):
        """Test verificación de terminal interactivo"""
        result = is_interactive_terminal()
        assert isinstance(result, bool)
    
    def test_validate_project_name_util(self):
        """Test utilidad de validación de nombre"""
        result = util_validate_project_name("valid-project")
        assert result["valid"] == True
        assert len(result["errors"]) == 0
    
    def test_validate_project_name_util_invalid(self):
        """Test utilidad de validación de nombre inválido"""
        result = util_validate_project_name("123-invalid")
        assert result["valid"] == False
        assert len(result["errors"]) > 0

class TestExceptions:
    """
    Tests para excepciones
    
    DOCTRINA: Solo testea manejo de errores de CLI
    """
    
    def test_genesis_cli_exception(self):
        """Test excepción base de Genesis CLI"""
        exc = GenesisCliException("Test error")
        assert str(exc) == "Test error"
        assert exc.get_formatted_message() == "❌ Test error"
    
    def test_validation_error(self):
        """Test error de validación"""
        exc = ValidationError("Invalid input", field="name")
        assert exc.field == "name"
        assert "Invalid input" in str(exc)
    
    def test_project_name_error(self):
        """Test error de nombre de proyecto"""
        exc = ProjectNameError("invalid-name", "starts with number")
        assert exc.name == "invalid-name"
        assert exc.reason == "starts with number"
        assert "invalid-name" in exc.get_formatted_message()
    
    def test_template_error(self):
        """Test error de template"""
        exc = TemplateError("invalid-template", ["saas-basic", "api-only"])
        assert exc.template == "invalid-template"
        assert "saas-basic" in exc.get_formatted_message()

# Fixtures para tests
@pytest.fixture
def temp_project_dir():
    """Fixture para directorio temporal de proyecto"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Crear genesis.json
        genesis_file = Path(temp_dir) / "genesis.json"
        project_data = {
            "name": "test-project",
            "template": "saas-basic",
            "version": "1.0.0",
            "features": ["authentication", "database"],
            "generated_files": ["file1.py", "file2.js"]
        }
        with open(genesis_file, 'w') as f:
            json.dump(project_data, f)
        
        yield temp_dir

@pytest.fixture
def mock_genesis_core():
    """Fixture para mock de Genesis Core"""
    with patch('genesis_cli.main.CoreOrchestrator') as mock_orchestrator:
        mock_instance = Mock()
        mock_instance.execute_project_generation = AsyncMock(return_value=Mock(
            success=True,
            project_path="/tmp/test-project",
            generated_files=["file1.py", "file2.js"],
            data={}
        ))
        mock_instance.execute_deployment = AsyncMock(return_value=Mock(
            success=True,
            deployment_url="http://localhost:3000",
            data={}
        ))
        mock_instance.execute_component_generation = AsyncMock(return_value=Mock(
            success=True,
            generated_files=["component.py"],
            data={}
        ))
        mock_orchestrator.return_value = mock_instance
        yield mock_instance

# Marcadores para categorías de tests
pytestmark = [
    pytest.mark.cli,
    pytest.mark.unit
]