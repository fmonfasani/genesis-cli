"""
Configuración específica para Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- SÍ maneja configuración específica de CLI
- SÍ proporciona settings de UX/UI
- Solo configuración de interfaz de usuario
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Configuración por defecto para la CLI
DEFAULT_CONFIG = {
    "ui": {
        "theme": "default",
        "show_banner": True,
        "progress_style": "bar",
        "color_output": True,
        "terminal_width": "auto"
    },
    "behavior": {
        "interactive_mode": True,
        "auto_confirm": False,
        "verbose_output": False,
        "skip_dependency_check": False
    },
    "templates": {
        "default_template": "saas-basic",
        "template_source": "official"
    },
    "project": {
        "default_output_dir": ".",
        "auto_cd": True,
        "create_git_repo": True,
        "init_commit": True
    }
}

@dataclass
class CLIConfig:
    """
    Configuración específica para Genesis CLI
    
    DOCTRINA: Solo configuración de interfaz de usuario
    """
    
    # Configuración de UI
    theme: str = "default"
    show_banner: bool = True
    progress_style: str = "bar"
    color_output: bool = True
    terminal_width: str = "auto"
    
    # Configuración de comportamiento
    interactive_mode: bool = True
    auto_confirm: bool = False
    verbose_output: bool = False
    skip_dependency_check: bool = False
    
    # Configuración de templates
    default_template: str = "saas-basic"
    template_source: str = "official"
    
    # Configuración de proyecto
    default_output_dir: str = "."
    auto_cd: bool = True
    create_git_repo: bool = True
    init_commit: bool = True
    
    # Configuración de desarrollo
    debug_mode: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'CLIConfig':
        """Crear configuración desde diccionario"""
        # Aplanar configuración anidada
        flattened = {}
        for section, values in config_dict.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    flattened[key] = value
            else:
                flattened[section] = values
        
        return cls(**flattened)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario"""
        return {
            "ui": {
                "theme": self.theme,
                "show_banner": self.show_banner,
                "progress_style": self.progress_style,
                "color_output": self.color_output,
                "terminal_width": self.terminal_width
            },
            "behavior": {
                "interactive_mode": self.interactive_mode,
                "auto_confirm": self.auto_confirm,
                "verbose_output": self.verbose_output,
                "skip_dependency_check": self.skip_dependency_check
            },
            "templates": {
                "default_template": self.default_template,
                "template_source": self.template_source
            },
            "project": {
                "default_output_dir": self.default_output_dir,
                "auto_cd": self.auto_cd,
                "create_git_repo": self.create_git_repo,
                "init_commit": self.init_commit
            },
            "debug": {
                "debug_mode": self.debug_mode,
                "log_level": self.log_level
            }
        }

class CLIConfigManager:
    """
    Gestor de configuración para Genesis CLI
    
    DOCTRINA: Solo maneja configuración de interfaz de usuario
    """
    
    def __init__(self):
        self.config_dir = Path.home() / ".genesis-cli"
        self.config_file = self.config_dir / "config.json"
        self._config: Optional[CLIConfig] = None
    
    def load_config(self) -> CLIConfig:
        """Cargar configuración desde archivo"""
        if self._config is not None:
            return self._config
        
        if self.config_file.exists():
            try:
                import json
                with open(self.config_file, 'r') as f:
                    config_dict = json.load(f)
                
                # Merge con configuración por defecto
                merged_config = DEFAULT_CONFIG.copy()
                self._merge_config(merged_config, config_dict)
                
                self._config = CLIConfig.from_dict(merged_config)
                return self._config
            
            except (json.JSONDecodeError, IOError):
                # Si hay error, usar configuración por defecto
                pass
        
        # Usar configuración por defecto
        self._config = CLIConfig.from_dict(DEFAULT_CONFIG)
        return self._config
    
    def save_config(self, config: CLIConfig):
        """Guardar configuración en archivo"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            import json
            with open(self.config_file, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            self._config = config
            
        except IOError:
            # Si no se puede guardar, continuar con configuración en memoria
            pass
    
    def update_config(self, **kwargs):
        """Actualizar configuración específica"""
        config = self.load_config()
        
        # Actualizar campos específicos
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.save_config(config)
    
    def reset_config(self):
        """Resetear configuración a valores por defecto"""
        self._config = CLIConfig.from_dict(DEFAULT_CONFIG)
        self.save_config(self._config)
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Obtener valor específico de configuración"""
        config = self.load_config()
        return getattr(config, key, default)
    
    def _merge_config(self, base: Dict[str, Any], update: Dict[str, Any]):
        """Merge recursivo de configuraciones"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

# Instancia global del gestor de configuración
config_manager = CLIConfigManager()

def get_config() -> CLIConfig:
    """Obtener configuración actual"""
    return config_manager.load_config()

def update_config(**kwargs):
    """Actualizar configuración"""
    config_manager.update_config(**kwargs)

def reset_config():
    """Resetear configuración"""
    config_manager.reset_config()

# Funciones de conveniencia para configuración específica
def get_ui_theme() -> str:
    """Obtener tema de UI"""
    return config_manager.get_config_value("theme", "default")

def is_interactive_mode() -> bool:
    """Verificar si está en modo interactivo"""
    return config_manager.get_config_value("interactive_mode", True)

def should_show_banner() -> bool:
    """Verificar si debe mostrar banner"""
    return config_manager.get_config_value("show_banner", True)

def get_default_template() -> str:
    """Obtener template por defecto"""
    return config_manager.get_config_value("default_template", "saas-basic")

def is_verbose_mode() -> bool:
    """Verificar si está en modo verbose"""
    return config_manager.get_config_value("verbose_output", False)

def should_skip_dependency_check() -> bool:
    """Verificar si debe omitir verificación de dependencias"""
    return config_manager.get_config_value("skip_dependency_check", False)

def get_default_output_dir() -> str:
    """Obtener directorio de salida por defecto"""
    return config_manager.get_config_value("default_output_dir", ".")

def should_create_git_repo() -> bool:
    """Verificar si debe crear repositorio Git"""
    return config_manager.get_config_value("create_git_repo", True)

def is_debug_mode() -> bool:
    """Verificar si está en modo debug"""
    return config_manager.get_config_value("debug_mode", False)

def get_log_level() -> str:
    """Obtener nivel de log"""
    return config_manager.get_config_value("log_level", "INFO")

# Configuración específica por entorno
def load_env_config():
    """Cargar configuración desde variables de entorno"""
    config = get_config()
    
    # Variables de entorno específicas para Genesis CLI
    if os.getenv("GENESIS_CLI_NO_BANNER"):
        config.show_banner = False
    
    if os.getenv("GENESIS_CLI_NO_INTERACTIVE"):
        config.interactive_mode = False
    
    if os.getenv("GENESIS_CLI_VERBOSE"):
        config.verbose_output = True
    
    if os.getenv("GENESIS_CLI_DEBUG"):
        config.debug_mode = True
    
    if os.getenv("GENESIS_CLI_SKIP_DEPS"):
        config.skip_dependency_check = True
    
    default_template = os.getenv("GENESIS_CLI_DEFAULT_TEMPLATE")
    if default_template:
        config.default_template = default_template
    
    return config