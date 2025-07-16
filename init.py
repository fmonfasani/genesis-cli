"""
Genesis CLI - Interfaz de línea de comandos para Genesis Engine.

Genesis CLI es la interfaz de usuario principal del ecosistema Genesis Engine.
Proporciona comandos elegantes y funcionales para interactuar con el sistema
de generación de código basado en agentes IA.

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente  
- NO contiene templates ni agentes
- SÍ es la única interfaz de usuario
- SÍ valida entrada del usuario
- SÍ muestra progreso y estado
- Solo usa genesis-core como interfaz
"""

__version__ = "1.0.0"
__author__ = "Genesis Team"
__email__ = "team@genesis.dev"

# Configuración de logging
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Importaciones principales con manejo de errores
try:
    # Solo importamos genesis-core, nunca MCPturbo directamente
    from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator
    from genesis_core.project_manager import ProjectManager
except Exception as e:  # pragma: no cover - graceful fallback if deps fail
    logger.error(f"Failed to import genesis-core dependencies: {e}", exc_info=True)
    CoreOrchestrator = None
    ProjectManager = None

# Importaciones CLI específicas
try:
    from .commands.utils import show_banner, check_dependencies
    from .ui.console import genesis_console
    from .utils import get_terminal_size, is_interactive_terminal
except Exception as e:  # pragma: no cover - graceful fallback
    logger.error(f"Failed to import CLI utilities: {e}", exc_info=True)
    show_banner = None
    check_dependencies = None
    genesis_console = None
    get_terminal_size = None
    is_interactive_terminal = None

__all__ = [
    "CoreOrchestrator",
    "ProjectManager", 
    "show_banner",
    "check_dependencies",
    "genesis_console",
    "get_terminal_size",
    "is_interactive_terminal",
    "__version__",
    "__author__",
    "__email__"
]