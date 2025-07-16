"""
Configuración de pytest para Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO testea lógica de generación
- NO testea agentes directamente
- SÍ testea interfaz de usuario
- SÍ testea validación de entrada
- Solo testea funcionalidad de CLI
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typer.testing import CliRunner

# Configuración global para todos los tests
pytest_plugins = []

def pytest_configure(config):
    """Configuración de pytest"""
    config.addinivalue_line(
        "markers", "unit: marca tests como tests unitarios"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests como tests de integración"
    )
    config.addinivalue_line(
        "markers", "cli: marca tests como tests de CLI"
    )
    config.addinivalue_line(
        "markers", "ui: marca tests como tests de interfaz de usuario"
    )
    config.addinivalue_line(
        "markers", "slow: marca tests como tests lentos"
    )

@pytest.fixture(scope="session")
def cli_runner():
    """
    Fixture de CliRunner para tests de CLI
    
    DOCTRINA: Solo testea interfaz de usuario
    """
    return CliRunner()

@pytest.fixture
def temp_dir():
    """Fixture para directorio temporal"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def temp_project_dir():
    """
    Fixture para directorio temporal con proyecto Genesis
    
    DOCTRINA: Solo testea interfaz de usuario
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Crear genesis.json
        genesis_file = Path(temp_dir) / "genesis.json"
        project_data = {
            "name": "test-project",
            "template": "saas-basic",
            "version": "1.0.0",
            "description": "Test project",
            "features": ["authentication", "database", "api", "frontend"],
            "generated_files": [
                "backend/app/main.py",
                "backend/app/models/user.py",
                "frontend/app/page.tsx",
                "frontend/components/Header.tsx",
                "docker-compose.yml",
                "README.md"
            ],
            "created_at": "2024-01-01T00:00:00Z",
            "generator": "genesis-cli@1.0.0"
        }
        with open(genesis_file, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        yield Path(temp_dir)

@pytest.fixture
def empty_project_dir():
    """Fixture para directorio vacío sin proyecto Genesis"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def mock_genesis_core():
    """
    Fixture para mock de Genesis Core
    
    DOCTRINA: Solo usamos genesis-core como interfaz
    """
    with patch('genesis_cli.main.CoreOrchestrator') as mock_orchestrator:
        mock_instance = Mock()
        
        # Mock para execute_project_generation
        mock_instance.execute_project_generation = AsyncMock(return_value=Mock(
            success=True,
            project_path="/tmp/test-project",
            generated_files=[
                "backend/app/main.py",
                "frontend/app/page.tsx",
                "docker-compose.yml"
            ],
            data={
                "template": "saas-basic",
                "features": ["authentication", "database"],
                "stack": {
                    "backend": "fastapi",
                    "frontend": "nextjs",
                    "database": "postgresql"
                }
            },
            error=None
        ))
        
        # Mock para execute_deployment
        mock_instance.execute_deployment = AsyncMock(return_value=Mock(
            success=True,
            deployment_url="http://localhost:3000",
            data={
                "environment": "local",
                "services": ["backend", "frontend", "database"],
                "status": "running"
            },
            error=None
        ))
        
        # Mock para execute_component_generation
        mock_instance.execute_component_generation = AsyncMock(return_value=Mock(
            success=True,
            generated_files=["models/user.py", "tests/test_user.py"],
            data={
                "component_type": "model",
                "component_name": "User",
                "files_created": 2
            },
            error=None
        ))
        
        mock_orchestrator.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_genesis_core_failure():
    """
    Fixture para mock de Genesis Core con fallos
    
    DOCTRINA: Solo usamos genesis-core como interfaz
    """
    with patch('genesis_cli.main.CoreOrchestrator') as mock_orchestrator:
        mock_instance = Mock()
        
        # Mock para execute_project_generation con fallo
        mock_instance.execute_project_generation = AsyncMock(return_value=Mock(
            success=False,
            project_path=None,
            generated_files=[],
            data={},
            error="Error simulado en Genesis Core"
        ))
        
        # Mock para execute_deployment con fallo
        mock_instance.execute_deployment = AsyncMock(return_value=Mock(
            success=False,
            deployment_url=None,
            data={},
            error="Error simulado en despliegue"
        ))
        
        # Mock para execute_component_generation con fallo
        mock_instance.execute_component_generation = AsyncMock(return_value=Mock(
            success=False,
            generated_files=[],
            data={},
            error="Error simulado en generación de componente"
        ))
        
        mock_orchestrator.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_dependencies_check():
    """
    Fixture para mock de verificación de dependencias
    
    DOCTRINA: Validamos entrada del usuario
    """
    with patch('genesis_cli.commands.utils.check_dependencies') as mock_check:
        mock_check.return_value = True
        yield mock_check

@pytest.fixture
def mock_dependencies_failure():
    """
    Fixture para mock de verificación de dependencias con fallo
    
    DOCTRINA: Validamos entrada del usuario
    """
    with patch('genesis_cli.commands.utils.check_dependencies') as mock_check:
        mock_check.return_value = False
        yield mock_check

@pytest.fixture
def mock_user_input():
    """
    Fixture para mock de entrada del usuario
    
    DOCTRINA: Validamos entrada del usuario
    """
    with patch('genesis_cli.utils.get_user_input') as mock_input:
        mock_input.return_value = "test-input"
        yield mock_input

@pytest.fixture
def mock_user_confirmation():
    """
    Fixture para mock de confirmación del usuario
    
    DOCTRINA: Validamos entrada del usuario
    """
    with patch('genesis_cli.utils.get_user_confirmation') as mock_confirm:
        mock_confirm.return_value = True
        yield mock_confirm

@pytest.fixture
def mock_user_confirmation_no():
    """
    Fixture para mock de confirmación del usuario (No)
    
    DOCTRINA: Validamos entrada del usuario
    """
    with patch('genesis_cli.utils.get_user_confirmation') as mock_confirm:
        mock_confirm.return_value = False
        yield mock_confirm

@pytest.fixture
def mock_terminal_interactive():
    """
    Fixture para mock de terminal interactivo
    
    DOCTRINA: Enfocado en UX/UI
    """
    with patch('genesis_cli.utils.is_interactive_terminal') as mock_interactive:
        mock_interactive.return_value = True
        yield mock_interactive

@pytest.fixture
def mock_terminal_non_interactive():
    """
    Fixture para mock de terminal no interactivo
    
    DOCTRINA: Enfocado en UX/UI
    """
    with patch('genesis_cli.utils.is_interactive_terminal') as mock_interactive:
        mock_interactive.return_value = False
        yield mock_interactive

@pytest.fixture
def mock_config():
    """
    Fixture para mock de configuración CLI
    
    DOCTRINA: Solo configuración de interfaz de usuario
    """
    from genesis_cli.config import CLIConfig
    
    with patch('genesis_cli.config.get_config') as mock_get_config:
        config = CLIConfig(
            theme="default",
            show_banner=True,
            interactive_mode=True,
            default_template="saas-basic",
            verbose_output=False
        )
        mock_get_config.return_value = config
        yield config

@pytest.fixture
def sample_project_data():
    """
    Fixture con datos de ejemplo de proyecto
    
    DOCTRINA: Solo testea interfaz de usuario
    """
    return {
        "name": "sample-project",
        "template": "saas-basic",
        "version": "1.0.0",
        "description": "Sample project for testing",
        "features": [
            "authentication",
            "database",
            "api",
            "frontend",
            "docker",
            "cicd"
        ],
        "stack": {
            "backend": "fastapi",
            "frontend": "nextjs",
            "database": "postgresql"
        },
        "generated_files": [
            "backend/app/main.py",
            "backend/app/models/__init__.py",
            "backend/app/models/user.py",
            "backend/app/routes/__init__.py",
            "backend/app/routes/auth.py",
            "backend/app/routes/users.py",
            "backend/requirements.txt",
            "backend/Dockerfile",
            "frontend/app/layout.tsx",
            "frontend/app/page.tsx",
            "frontend/components/Header.tsx",
            "frontend/components/Footer.tsx",
            "frontend/lib/api.ts",
            "frontend/package.json",
            "frontend/Dockerfile",
            "docker-compose.yml",
            ".github/workflows/ci.yml",
            "README.md",
            "genesis.json"
        ],
        "created_at": "2024-01-01T00:00:00Z",
        "generator": "genesis-cli@1.0.0"
    }

@pytest.fixture
def change_dir():
    """
    Fixture para cambiar directorio temporalmente
    
    DOCTRINA: Utility para mejorar tests
    """
    def _change_dir(path):
        original_cwd = os.getcwd()
        os.chdir(path)
        return original_cwd
    
    yield _change_dir

@pytest.fixture
def restore_cwd():
    """
    Fixture para restaurar directorio original
    
    DOCTRINA: Utility para mejorar tests
    """
    original_cwd = os.getcwd()
    yield
    os.chdir(original_cwd)

@pytest.fixture(autouse=True)
def skip_project_check():
    """
    Fixture para omitir verificación de proyecto por defecto
    
    DOCTRINA: Solo testea interfaz de usuario
    """
    os.environ['GENESIS_SKIP_PROJECT_CHECK'] = '1'
    yield
    if 'GENESIS_SKIP_PROJECT_CHECK' in os.environ:
        del os.environ['GENESIS_SKIP_PROJECT_CHECK']

@pytest.fixture
def mock_logger():
    """
    Fixture para mock de logger
    
    DOCTRINA: Enfocado en UX/UI
    """
    with patch('genesis_cli.logging.cli_logger') as mock_log:
        yield mock_log

@pytest.fixture
def capture_output():
    """
    Fixture para capturar output de consola
    
    DOCTRINA: Enfocado en UX/UI
    """
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        yield stdout_capture, stderr_capture

# Funciones de utilidad para tests
def create_test_project(temp_dir: Path, project_data: dict = None):
    """
    Crear proyecto de prueba
    
    DOCTRINA: Utility para mejorar tests
    """
    if project_data is None:
        project_data = {
            "name": "test-project",
            "template": "saas-basic",
            "version": "1.0.0",
            "features": ["authentication", "database"],
            "generated_files": ["file1.py", "file2.js"]
        }
    
    genesis_file = temp_dir / "genesis.json"
    with open(genesis_file, 'w') as f:
        json.dump(project_data, f, indent=2)
    
    return genesis_file

def assert_command_success(result, expected_output=None):
    """
    Verificar que comando fue exitoso
    
    DOCTRINA: Utility para mejorar tests
    """
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    
    if expected_output:
        assert expected_output in result.output, f"Expected '{expected_output}' in output: {result.output}"

def assert_command_failure(result, expected_error=None):
    """
    Verificar que comando falló
    
    DOCTRINA: Utility para mejorar tests
    """
    assert result.exit_code != 0, f"Command should have failed but succeeded with output: {result.output}"
    
    if expected_error:
        assert expected_error in result.output, f"Expected '{expected_error}' in output: {result.output}"

def assert_file_exists(file_path: Path, should_exist: bool = True):
    """
    Verificar que archivo existe o no existe
    
    DOCTRINA: Utility para mejorar tests
    """
    if should_exist:
        assert file_path.exists(), f"File should exist: {file_path}"
    else:
        assert not file_path.exists(), f"File should not exist: {file_path}"

def assert_project_structure(project_dir: Path, expected_files: list):
    """
    Verificar estructura del proyecto
    
    DOCTRINA: Utility para mejorar tests
    """
    # Verificar que genesis.json existe
    genesis_file = project_dir / "genesis.json"
    assert_file_exists(genesis_file)
    
    # Verificar archivos esperados
    for file_path in expected_files:
        expected_file = project_dir / file_path
        assert_file_exists(expected_file)

# Markers automáticos para todos los tests
def pytest_collection_modifyitems(config, items):
    """Modificar items de tests automáticamente"""
    for item in items:
        # Agregar marker 'unit' a todos los tests por defecto
        if not any(marker.name in ['integration', 'slow'] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
        
        # Agregar marker 'cli' a tests de CLI
        if 'test_cli' in item.nodeid or 'CLI' in str(item.cls):
            item.add_marker(pytest.mark.cli)
        
        # Agregar marker 'ui' a tests de interfaz
        if 'test_ui' in item.nodeid or 'UI' in str(item.cls):
            item.add_marker(pytest.mark.ui)

# Configuración de warnings
def pytest_configure(config):
    """Configurar warnings"""
    import warnings
    
    # Ignorar warnings específicos durante tests
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    
    # Configurar logging para tests
    import logging
    logging.getLogger("genesis_cli").setLevel(logging.WARNING)
    logging.getLogger("genesis_core").setLevel(logging.WARNING)