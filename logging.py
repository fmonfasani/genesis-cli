"""
Sistema de logging específico para Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- SÍ proporciona logging elegante para UX
- SÍ maneja logs específicos de CLI
- Enfocado en experiencia de usuario
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

from genesis_cli.config import get_config, is_debug_mode, get_log_level

# Console para logging
console = Console(stderr=True)

class GenesisCliFormatter(logging.Formatter):
    """
    Formatter personalizado para Genesis CLI
    
    DOCTRINA: Enfocado en UX/UI elegante
    """
    
    def __init__(self):
        super().__init__()
        
    def format(self, record: logging.LogRecord) -> str:
        """Formatear mensaje de log"""
        
        # Mapear niveles a iconos y colores
        level_config = {
            logging.DEBUG: ("🐛", "dim"),
            logging.INFO: ("ℹ️", "cyan"),
            logging.WARNING: ("⚠️", "yellow"),
            logging.ERROR: ("❌", "red"),
            logging.CRITICAL: ("🚨", "bold red")
        }
        
        icon, color = level_config.get(record.levelno, ("•", "white"))
        
        # Formatear mensaje
        message = record.getMessage()
        timestamp = self.formatTime(record, datefmt="%H:%M:%S")
        
        # Formato para diferentes niveles
        if record.levelno >= logging.ERROR:
            return f"[{color}]{icon} {message}[/{color}]"
        elif record.levelno == logging.WARNING:
            return f"[{color}]{icon} {message}[/{color}]"
        elif is_debug_mode():
            return f"[dim]{timestamp}[/dim] [{color}]{icon} {message}[/{color}]"
        else:
            return f"[{color}]{icon} {message}[/{color}]"

class GenesisCliHandler(RichHandler):
    """
    Handler personalizado para Genesis CLI
    
    DOCTRINA: Enfocado en UX/UI elegante
    """
    
    def __init__(self, console: Optional[Console] = None):
        super().__init__(
            console=console or Console(stderr=True),
            show_time=is_debug_mode(),
            show_level=is_debug_mode(),
            show_path=is_debug_mode(),
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=is_debug_mode()
        )
        
    def emit(self, record: logging.LogRecord):
        """Emitir log record"""
        try:
            # Usar formatter personalizado solo para ciertos niveles
            if record.levelno >= logging.INFO:
                # Formatear mensaje con Rich markup
                formatter = GenesisCliFormatter()
                message = formatter.format(record)
                
                # Mostrar con Rich
                self.console.print(message, markup=True)
            else:
                # Usar handler normal para DEBUG
                super().emit(record)
                
        except Exception:
            # Fallback a handler normal en caso de error
            super().emit(record)

class GenesisCliLogger:
    """
    Logger principal para Genesis CLI
    
    DOCTRINA: Enfocado en UX/UI elegante
    """
    
    def __init__(self, name: str = "genesis-cli"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
        
    def _setup_logger(self):
        """Configurar logger"""
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Configurar nivel
        level = getattr(logging, get_log_level().upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Handler para Rich
        rich_handler = GenesisCliHandler(console)
        self.logger.addHandler(rich_handler)
        
        # Handler para archivo si está en modo debug
        if is_debug_mode():
            self._setup_file_handler()
        
        # Evitar propagación a root logger
        self.logger.propagate = False
    
    def _setup_file_handler(self):
        """Configurar handler para archivo"""
        try:
            # Crear directorio de logs
            log_dir = Path.home() / ".genesis-cli" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Archivo de log
            log_file = log_dir / "genesis-cli.log"
            
            # Handler para archivo
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter para archivo
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(file_handler)
            
        except Exception:
            # Si no se puede configurar archivo, continuar sin él
            pass
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log success message (custom level)"""
        self.logger.info(f"✅ {message}", **kwargs)
    
    def step(self, message: str, **kwargs):
        """Log step message (custom level)"""
        self.logger.info(f"📋 {message}", **kwargs)
    
    def progress(self, message: str, **kwargs):
        """Log progress message (custom level)"""
        self.logger.info(f"⏳ {message}", **kwargs)

# Logger global para Genesis CLI
cli_logger = GenesisCliLogger()

# Funciones de conveniencia
def debug(message: str, **kwargs):
    """Log debug message"""
    cli_logger.debug(message, **kwargs)

def info(message: str, **kwargs):
    """Log info message"""
    cli_logger.info(message, **kwargs)

def warning(message: str, **kwargs):
    """Log warning message"""
    cli_logger.warning(message, **kwargs)

def error(message: str, **kwargs):
    """Log error message"""
    cli_logger.error(message, **kwargs)

def critical(message: str, **kwargs):
    """Log critical message"""
    cli_logger.critical(message, **kwargs)

def success(message: str, **kwargs):
    """Log success message"""
    cli_logger.success(message, **kwargs)

def step(message: str, **kwargs):
    """Log step message"""
    cli_logger.step(message, **kwargs)

def progress(message: str, **kwargs):
    """Log progress message"""
    cli_logger.progress(message, **kwargs)

# Configurar logging para bibliotecas externas
def setup_external_logging():
    """Configurar logging para bibliotecas externas"""
    
    # Reducir verbosidad de bibliotecas externas
    external_loggers = [
        'urllib3',
        'requests',
        'httpx',
        'httpcore',
        'asyncio',
        'aiohttp'
    ]
    
    for logger_name in external_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARNING)
    
    # Configurar logging específico para Genesis Core
    genesis_core_logger = logging.getLogger('genesis-core')
    genesis_core_logger.setLevel(logging.INFO)
    
    # Handler para Genesis Core
    if not genesis_core_logger.handlers:
        handler = GenesisCliHandler(console)
        genesis_core_logger.addHandler(handler)
        genesis_core_logger.propagate = False

# Contexto para logging con indentación
class LogContext:
    """
    Contexto para logging con indentación
    
    DOCTRINA: Enfocado en UX/UI elegante
    """
    
    def __init__(self, message: str, level: str = "info"):
        self.message = message
        self.level = level
        self.logger = cli_logger
        
    def __enter__(self):
        """Entrar al contexto"""
        getattr(self.logger, self.level)(f"🔄 {self.message}...")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salir del contexto"""
        if exc_type is None:
            self.logger.success(f"✅ {self.message} completado")
        else:
            self.logger.error(f"❌ {self.message} falló: {exc_val}")
        
        return False  # No suprimir excepciones

# Decorador para logging de funciones
def log_function_call(level: str = "debug"):
    """
    Decorador para logging de llamadas a funciones
    
    DOCTRINA: Enfocado en UX/UI elegante
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            if level == "debug":
                debug(f"🔧 Llamando a {func_name}")
            
            try:
                result = func(*args, **kwargs)
                
                if level == "debug":
                    debug(f"✅ {func_name} completado exitosamente")
                
                return result
                
            except Exception as e:
                error(f"❌ Error en {func_name}: {str(e)}")
                raise
                
        return wrapper
    return decorator

# Inicializar logging
def initialize_logging():
    """Inicializar sistema de logging"""
    setup_external_logging()
    
    # Log de inicialización
    if is_debug_mode():
        debug("Sistema de logging inicializado")
        debug(f"Nivel de log: {get_log_level()}")
        debug(f"Modo debug: {is_debug_mode()}")

# Función para obtener logs recientes
def get_recent_logs(lines: int = 100) -> Optional[str]:
    """
    Obtener logs recientes del archivo
    
    DOCTRINA: Utility para mejorar UX
    """
    try:
        log_file = Path.home() / ".genesis-cli" / "logs" / "genesis-cli.log"
        
        if not log_file.exists():
            return None
        
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return ''.join(recent_lines)
            
    except Exception:
        return None

# Función para limpiar logs antiguos
def cleanup_old_logs(days: int = 7):
    """
    Limpiar logs antiguos
    
    DOCTRINA: Utility para mejorar UX
    """
    try:
        log_dir = Path.home() / ".genesis-cli" / "logs"
        
        if not log_dir.exists():
            return
        
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_date.timestamp():
                log_file.unlink()
                
    except Exception:
        # Si no se puede limpiar, continuar silenciosamente
        pass

# Inicializar automáticamente
initialize_logging()