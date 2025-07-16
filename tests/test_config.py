"""
Tests para configuración de Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO testea lógica de generación
- NO testea agentes directamente
- SÍ testea configuración específica de CLI
- SÍ testea settings de UX/UI
- Solo configuración de interfaz de usuario
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from genesis_cli.config import (
    CLIConfig,
    CLIConfigManager,
    DEFAULT_CONFIG,
    get_config,
    update_config,
    reset_config,
    get_ui_theme,
    is_interactive_mode,
    should_show_banner,
    get_default_template,
    is_verbose_mode,
    should_skip_dependency_check,
    get_default_output_dir,
    should_create_git_repo,
    is_debug_mode,
    get_log_level,
    load_env_config
)


class TestCLIConfig:
    """
    Tests para CLIConfig
    
    DOCTRINA: Solo configuración de interfaz de usuario
    """
    
    def test_cli_config_default_values(self):
        """Test valores por defecto de configuración"""
        config = CLIConfig()
        
        # UI settings
        assert config.theme == "default"
        assert config.show_banner == True
        assert config.progress_style == "bar"
        assert config.color_output == True
        assert config.terminal_width == "auto"
        
        # Behavior settings
        assert config.interactive_mode == True
        assert config.auto_confirm == False
        assert config.verbose_output == False
        assert config.skip_dependency_check == False
        
        # Template settings
        assert config.default_template == "saas-basic"
        assert config.template_source == "official"
        
        # Project settings
        assert config.default_output_dir == "."
        assert config.auto_cd == True
        assert config.create_git_repo == True
        assert config.init_commit == True
        
        # Development settings
        assert config.debug_mode == False
        assert config.log_level == "INFO"
    
    def test_cli_config_custom_values(self):
        """Test configuración con valores personalizados"""
        config = CLIConfig(
            theme="dark",
            show_banner=False,
            interactive_mode=False,
            default_template="api-only",
            verbose_output=True,
            debug_mode=True,
            log_level="DEBUG"
        )
        
        assert config.theme == "dark"
        assert config.show_banner == False
        assert config.interactive_mode == False
        assert config.default_template == "api-only"
        assert config.verbose_output == True
        assert config.debug_mode == True
        assert config.log_level == "DEBUG"
    
    def test_cli_config_from_dict(self):
        """Test creación de configuración desde diccionario"""
        config_dict = {
            "ui": {
                "theme": "dark",
                "show_banner": False,
                "color_output": False
            },
            "behavior": {
                "interactive_mode": False,
                "verbose_output": True
            },
            "templates": {
                "default_template": "api-only"
            },
            "project": {
                "create_git_repo": False
            },
            "debug": {
                "debug_mode": True,
                "log_level": "DEBUG"
            }
        }
        
        config = CLIConfig.from_dict(config_dict)
        
        assert config.theme == "dark"
        assert config.show_banner == False
        assert config.color_output == False
        assert config.interactive_mode == False
        assert config.verbose_output == True
        assert config.default_template == "api-only"
        assert config.create_git_repo == False
        assert config.debug_mode == True
        assert config.log_level == "DEBUG"
    
    def test_cli_config_from_dict_partial(self):
        """Test creación de configuración desde diccionario parcial"""
        config_dict = {
            "ui": {
                "theme": "dark"
            },
            "behavior": {
                "interactive_mode": False
            }
        }
        
        config = CLIConfig.from_dict(config_dict)
        
        # Valores especificados
        assert config.theme == "dark"
        assert config.interactive_mode == False
        
        # Valores por defecto para no especificados
        assert config.show_banner == True
        assert config.default_template == "saas-basic"
        assert config.debug_mode == False
    
    def test_cli_config_to_dict(self):
        """Test conversión de configuración a diccionario"""
        config = CLIConfig(
            theme="dark",
            show_banner=False,
            interactive_mode=False,
            default_template="api-only",
            debug_mode=True,
            log_level="DEBUG"
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["ui"]["theme"] == "dark"
        assert config_dict["ui"]["show_banner"] == False
        assert config_dict["behavior"]["interactive_mode"] == False
        assert config_dict["templates"]["default_template"] == "api-only"
        assert config_dict["debug"]["debug_mode"] == True
        assert config_dict["debug"]["log_level"] == "DEBUG"
    
    def test_cli_config_from_dict_invalid_keys(self):
        """Test configuración con claves inválidas"""
        config_dict = {
            "ui": {
                "theme": "dark",
                "invalid_key": "value"
            },
            "invalid_section": {
                "key": "value"
            }
        }
        
        # Debería crear configuración ignorando claves inválidas
        config = CLIConfig.from_dict(config_dict)
        assert config.theme == "dark"
        assert not hasattr(config, "invalid_key")


class TestCLIConfigManager:
    """
    Tests para CLIConfigManager
    
    DOCTRINA: Solo maneja configuración de interfaz de usuario
    """
    
    def test_config_manager_initialization(self):
        """Test inicialización del gestor de configuración"""
        manager = CLIConfigManager()
        
        assert manager.config_dir == Path.home() / ".genesis-cli"
        assert manager.config_file == manager.config_dir / "config.json"
        assert manager._config is None
    
    def test_config_manager_load_default(self):
        """Test cargar configuración por defecto"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Cargar configuración (no existe archivo)
            config = manager.load_config()
            
            assert isinstance(config, CLIConfig)
            assert config.theme == "default"
            assert config.interactive_mode == True
            assert config.default_template == "saas-basic"
    
    def test_config_manager_load_from_file(self):
        """Test cargar configuración desde archivo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Crear archivo de configuración
            config_data = {
                "ui": {
                    "theme": "dark",
                    "show_banner": False
                },
                "behavior": {
                    "interactive_mode": False
                }
            }
            
            manager.config_dir.mkdir(parents=True, exist_ok=True)
            with open(manager.config_file, 'w') as f:
                json.dump(config_data, f)
            
            # Cargar configuración
            config = manager.load_config()
            
            assert config.theme == "dark"
            assert config.show_banner == False
            assert config.interactive_mode == False
            # Valores por defecto para no especificados
            assert config.default_template == "saas-basic"
    
    def test_config_manager_load_invalid_json(self):
        """Test cargar configuración con JSON inválido"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Crear archivo con JSON inválido
            manager.config_dir.mkdir(parents=True, exist_ok=True)
            with open(manager.config_file, 'w') as f:
                f.write("invalid json content")
            
            # Cargar configuración (debería usar defaults)
            config = manager.load_config()
            
            assert config.theme == "default"
            assert config.interactive_mode == True
    
    def test_config_manager_save_config(self):
        """Test guardar configuración"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Crear configuración personalizada
            config = CLIConfig(
                theme="dark",
                show_banner=False,
                interactive_mode=False
            )
            
            # Guardar configuración
            manager.save_config(config)
            
            # Verificar que se guardó correctamente
            assert manager.config_file.exists()
            
            with open(manager.config_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["ui"]["theme"] == "dark"
            assert saved_data["ui"]["show_banner"] == False
            assert saved_data["behavior"]["interactive_mode"] == False
    
    def test_config_manager_save_config_creates_dir(self):
        """Test que guardar configuración crea directorio"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir) / "nested" / "dir"
            manager.config_file = manager.config_dir / "config.json"
            
            # Verificar que directorio no existe
            assert not manager.config_dir.exists()
            
            # Guardar configuración
            config = CLIConfig()
            manager.save_config(config)
            
            # Verificar que directorio fue creado
            assert manager.config_dir.exists()
            assert manager.config_file.exists()
    
    def test_config_manager_update_config(self):
        """Test actualizar configuración específica"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Actualizar configuración
            manager.update_config(
                theme="dark",
                show_banner=False,
                interactive_mode=False
            )
            
            # Verificar que se actualizó
            config = manager.load_config()
            assert config.theme == "dark"
            assert config.show_banner == False
            assert config.interactive_mode == False
            # Otros valores deben mantener defaults
            assert config.default_template == "saas-basic"
    
    def test_config_manager_reset_config(self):
        """Test resetear configuración"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Configurar valores personalizados
            manager.update_config(
                theme="dark",
                show_banner=False,
                interactive_mode=False
            )
            
            # Resetear configuración
            manager.reset_config()
            
            # Verificar que volvió a defaults
            config = manager.load_config()
            assert config.theme == "default"
            assert config.show_banner == True
            assert config.interactive_mode == True
    
    def test_config_manager_get_config_value(self):
        """Test obtener valor específico de configuración"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Configurar valores
            manager.update_config(theme="dark", verbose_output=True)
            
            # Obtener valores específicos
            assert manager.get_config_value("theme") == "dark"
            assert manager.get_config_value("verbose_output") == True
            assert manager.get_config_value("nonexistent", "default") == "default"
    
    def test_config_manager_merge_config(self):
        """Test merge recursivo de configuraciones"""
        manager = CLIConfigManager()
        
        base_config = {
            "ui": {
                "theme": "default",
                "show_banner": True,
                "color_output": True
            },
            "behavior": {
                "interactive_mode": True,
                "verbose_output": False
            }
        }
        
        update_config = {
            "ui": {
                "theme": "dark",
                "show_banner": False
            },
            "behavior": {
                "verbose_output": True
            },
            "new_section": {
                "new_key": "new_value"
            }
        }
        
        manager._merge_config(base_config, update_config)
        
        # Verificar merge correcto
        assert base_config["ui"]["theme"] == "dark"
        assert base_config["ui"]["show_banner"] == False
        assert base_config["ui"]["color_output"] == True  # No modificado
        assert base_config["behavior"]["interactive_mode"] == True  # No modificado
        assert base_config["behavior"]["verbose_output"] == True  # Modificado
        assert base_config["new_section"]["new_key"] == "new_value"  # Nuevo


class TestConvenienceFunctions:
    """
    Tests para funciones de conveniencia
    
    DOCTRINA: Solo configuración de interfaz de usuario
    """
    
    def test_get_config_function(self):
        """Test función get_config"""
        config = get_config()
        assert isinstance(config, CLIConfig)
    
    @patch('genesis_cli.config.config_manager')
    def test_update_config_function(self, mock_manager):
        """Test función update_config"""
        mock_manager.update_config = lambda **kwargs: None
        
        update_config(theme="dark", verbose_output=True)
        mock_manager.update_config.assert_called_once_with(theme="dark", verbose_output=True)
    
    @patch('genesis_cli.config.config_manager')
    def test_reset_config_function(self, mock_manager):
        """Test función reset_config"""
        mock_manager.reset_config = lambda: None
        
        reset_config()
        mock_manager.reset_config.assert_called_once()
    
    @patch('genesis_cli.config.config_manager')
    def test_get_ui_theme_function(self, mock_manager):
        """Test función get_ui_theme"""
        mock_manager.get_config_value = lambda key, default: "dark" if key == "theme" else default
        
        theme = get_ui_theme()
        assert theme == "dark"
    
    @patch('genesis_cli.config.config_manager')
    def test_is_interactive_mode_function(self, mock_manager):
        """Test función is_interactive_mode"""
        mock_manager.get_config_value = lambda key, default: False if key == "interactive_mode" else default
        
        interactive = is_interactive_mode()
        assert interactive == False
    
    @patch('genesis_cli.config.config_manager')
    def test_should_show_banner_function(self, mock_manager):
        """Test función should_show_banner"""
        mock_manager.get_config_value = lambda key, default: False if key == "show_banner" else default
        
        show_banner = should_show_banner()
        assert show_banner == False
    
    @patch('genesis_cli.config.config_manager')
    def test_get_default_template_function(self, mock_manager):
        """Test función get_default_template"""
        mock_manager.get_config_value = lambda key, default: "api-only" if key == "default_template" else default
        
        template = get_default_template()
        assert template == "api-only"
    
    @patch('genesis_cli.config.config_manager')
    def test_is_verbose_mode_function(self, mock_manager):
        """Test función is_verbose_mode"""
        mock_manager.get_config_value = lambda key, default: True if key == "verbose_output" else default
        
        verbose = is_verbose_mode()
        assert verbose == True
    
    @patch('genesis_cli.config.config_manager')
    def test_should_skip_dependency_check_function(self, mock_manager):
        """Test función should_skip_dependency_check"""
        mock_manager.get_config_value = lambda key, default: True if key == "skip_dependency_check" else default
        
        skip = should_skip_dependency_check()
        assert skip == True
    
    @patch('genesis_cli.config.config_manager')
    def test_get_default_output_dir_function(self, mock_manager):
        """Test función get_default_output_dir"""
        mock_manager.get_config_value = lambda key, default: "/custom/path" if key == "default_output_dir" else default
        
        output_dir = get_default_output_dir()
        assert output_dir == "/custom/path"
    
    @patch('genesis_cli.config.config_manager')
    def test_should_create_git_repo_function(self, mock_manager):
        """Test función should_create_git_repo"""
        mock_manager.get_config_value = lambda key, default: False if key == "create_git_repo" else default
        
        create_git = should_create_git_repo()
        assert create_git == False
    
    @patch('genesis_cli.config.config_manager')
    def test_is_debug_mode_function(self, mock_manager):
        """Test función is_debug_mode"""
        mock_manager.get_config_value = lambda key, default: True if key == "debug_mode" else default
        
        debug = is_debug_mode()
        assert debug == True
    
    @patch('genesis_cli.config.config_manager')
    def test_get_log_level_function(self, mock_manager):
        """Test función get_log_level"""
        mock_manager.get_config_value = lambda key, default: "DEBUG" if key == "log_level" else default
        
        log_level = get_log_level()
        assert log_level == "DEBUG"


class TestEnvironmentConfiguration:
    """
    Tests para configuración por variables de entorno
    
    DOCTRINA: Solo configuración de interfaz de usuario
    """
    
    def test_load_env_config_no_banner(self):
        """Test cargar configuración sin banner"""
        with patch.dict(os.environ, {'GENESIS_CLI_NO_BANNER': '1'}):
            config = load_env_config()
            assert config.show_banner == False
    
    def test_load_env_config_no_interactive(self):
        """Test cargar configuración no interactiva"""
        with patch.dict(os.environ, {'GENESIS_CLI_NO_INTERACTIVE': '1'}):
            config = load_env_config()
            assert config.interactive_mode == False
    
    def test_load_env_config_verbose(self):
        """Test cargar configuración verbose"""
        with patch.dict(os.environ, {'GENESIS_CLI_VERBOSE': '1'}):
            config = load_env_config()
            assert config.verbose_output == True
    
    def test_load_env_config_debug(self):
        """Test cargar configuración debug"""
        with patch.dict(os.environ, {'GENESIS_CLI_DEBUG': '1'}):
            config = load_env_config()
            assert config.debug_mode == True
    
    def test_load_env_config_skip_deps(self):
        """Test cargar configuración para omitir dependencias"""
        with patch.dict(os.environ, {'GENESIS_CLI_SKIP_DEPS': '1'}):
            config = load_env_config()
            assert config.skip_dependency_check == True
    
    def test_load_env_config_default_template(self):
        """Test cargar configuración con template por defecto"""
        with patch.dict(os.environ, {'GENESIS_CLI_DEFAULT_TEMPLATE': 'api-only'}):
            config = load_env_config()
            assert config.default_template == "api-only"
    
    def test_load_env_config_multiple_vars(self):
        """Test cargar configuración con múltiples variables"""
        env_vars = {
            'GENESIS_CLI_NO_BANNER': '1',
            'GENESIS_CLI_VERBOSE': '1',
            'GENESIS_CLI_DEBUG': '1',
            'GENESIS_CLI_DEFAULT_TEMPLATE': 'minimal'
        }
        
        with patch.dict(os.environ, env_vars):
            config = load_env_config()
            assert config.show_banner == False
            assert config.verbose_output == True
            assert config.debug_mode == True
            assert config.default_template == "minimal"
    
    def test_load_env_config_no_vars(self):
        """Test cargar configuración sin variables de entorno"""
        # Asegurar que no hay variables relevantes
        env_vars_to_clear = [
            'GENESIS_CLI_NO_BANNER',
            'GENESIS_CLI_NO_INTERACTIVE',
            'GENESIS_CLI_VERBOSE',
            'GENESIS_CLI_DEBUG',
            'GENESIS_CLI_SKIP_DEPS',
            'GENESIS_CLI_DEFAULT_TEMPLATE'
        ]
        
        original_env = {}
        for var in env_vars_to_clear:
            if var in os.environ:
                original_env[var] = os.environ[var]
                del os.environ[var]
        
        try:
            config = load_env_config()
            # Debería usar valores por defecto
            assert config.show_banner == True
            assert config.interactive_mode == True
            assert config.verbose_output == False
            assert config.debug_mode == False
            assert config.skip_dependency_check == False
            assert config.default_template == "saas-basic"
        finally:
            # Restaurar variables originales
            for var, value in original_env.items():
                os.environ[var] = value


class TestDefaultConfig:
    """
    Tests para configuración por defecto
    
    DOCTRINA: Solo configuración de interfaz de usuario
    """
    
    def test_default_config_structure(self):
        """Test estructura de configuración por defecto"""
        assert "ui" in DEFAULT_CONFIG
        assert "behavior" in DEFAULT_CONFIG
        assert "templates" in DEFAULT_CONFIG
        assert "project" in DEFAULT_CONFIG
        
        # Verificar secciones UI
        ui_config = DEFAULT_CONFIG["ui"]
        assert "theme" in ui_config
        assert "show_banner" in ui_config
        assert "progress_style" in ui_config
        assert "color_output" in ui_config
        assert "terminal_width" in ui_config
        
        # Verificar secciones behavior
        behavior_config = DEFAULT_CONFIG["behavior"]
        assert "interactive_mode" in behavior_config
        assert "auto_confirm" in behavior_config
        assert "verbose_output" in behavior_config
        assert "skip_dependency_check" in behavior_config
        
        # Verificar secciones templates
        templates_config = DEFAULT_CONFIG["templates"]
        assert "default_template" in templates_config
        assert "template_source" in templates_config
        
        # Verificar secciones project
        project_config = DEFAULT_CONFIG["project"]
        assert "default_output_dir" in project_config
        assert "auto_cd" in project_config
        assert "create_git_repo" in project_config
        assert "init_commit" in project_config
    
    def test_default_config_values(self):
        """Test valores por defecto correctos"""
        # UI defaults
        assert DEFAULT_CONFIG["ui"]["theme"] == "default"
        assert DEFAULT_CONFIG["ui"]["show_banner"] == True
        assert DEFAULT_CONFIG["ui"]["progress_style"] == "bar"
        assert DEFAULT_CONFIG["ui"]["color_output"] == True
        assert DEFAULT_CONFIG["ui"]["terminal_width"] == "auto"
        
        # Behavior defaults
        assert DEFAULT_CONFIG["behavior"]["interactive_mode"] == True
        assert DEFAULT_CONFIG["behavior"]["auto_confirm"] == False
        assert DEFAULT_CONFIG["behavior"]["verbose_output"] == False
        assert DEFAULT_CONFIG["behavior"]["skip_dependency_check"] == False
        
        # Templates defaults
        assert DEFAULT_CONFIG["templates"]["default_template"] == "saas-basic"
        assert DEFAULT_CONFIG["templates"]["template_source"] == "official"
        
        # Project defaults
        assert DEFAULT_CONFIG["project"]["default_output_dir"] == "."
        assert DEFAULT_CONFIG["project"]["auto_cd"] == True
        assert DEFAULT_CONFIG["project"]["create_git_repo"] == True
        assert DEFAULT_CONFIG["project"]["init_commit"] == True


class TestConfigurationEdgeCases:
    """
    Tests para casos edge en configuración
    
    DOCTRINA: Solo configuración de interfaz de usuario
    """
    
    def test_config_with_none_values(self):
        """Test configuración con valores None"""
        config_dict = {
            "ui": {
                "theme": None,
                "show_banner": None
            },
            "behavior": {
                "interactive_mode": None
            }
        }
        
        config = CLIConfig.from_dict(config_dict)
        # Valores None deberían usar defaults
        assert config.theme is None  # Se preserva None si se especifica
        assert config.show_banner is None
        assert config.interactive_mode is None
    
    def test_config_file_permission_error(self):
        """Test error de permisos en archivo de configuración"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Crear archivo sin permisos de escritura
            manager.config_dir.mkdir(parents=True, exist_ok=True)
            manager.config_file.write_text("{}")
            manager.config_file.chmod(0o444)  # Solo lectura
            
            # Intentar guardar configuración
            config = CLIConfig(theme="dark")
            manager.save_config(config)  # No debería fallar
            
            # Debería seguir funcionando en memoria
            assert manager._config.theme == "dark"
    
    def test_config_directory_creation_error(self):
        """Test error al crear directorio de configuración"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            # Usar un path imposible de crear
            manager.config_dir = Path("/root/impossible/path")
            manager.config_file = manager.config_dir / "config.json"
            
            # Intentar guardar configuración
            config = CLIConfig(theme="dark")
            manager.save_config(config)  # No debería fallar
            
            # Debería seguir funcionando en memoria
            assert manager._config.theme == "dark"
    
    def test_config_invalid_json_structure(self):
        """Test JSON con estructura inválida"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = CLIConfigManager()
            manager.config_dir = Path(temp_dir)
            manager.config_file = manager.config_dir / "config.json"
            
            # Crear archivo con estructura inválida
            manager.config_dir.mkdir(parents=True, exist_ok=True)
            with open(manager.config_file, 'w') as f:
                json.dump(["invalid", "structure"], f)
            
            # Cargar configuración (debería usar defaults)
            config = manager.load_config()
            assert config.theme == "default"
            assert config.interactive_mode == True


# Marcadores para tests
pytestmark = [
    pytest.mark.unit,
    pytest.mark.config
]