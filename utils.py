"""
Utilidades principales para Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- SÍ valida entrada del usuario
- SÍ proporciona utilities de UX/UI
- Solo usa genesis-core como interfaz
"""

import sys
import shutil
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()

def get_terminal_size() -> tuple[int, int]:
    """
    Obtener tamaño de terminal
    
    DOCTRINA: Utility para mejorar UX
    """
    try:
        return shutil.get_terminal_size()
    except Exception:
        return (80, 24)  # Fallback por defecto

def is_interactive_terminal() -> bool:
    """
    Verificar si estamos en terminal interactivo
    
    DOCTRINA: Utility para mejorar UX
    """
    return sys.stdin.isatty() and sys.stdout.isatty()

def get_user_confirmation(message: str, default: bool = False) -> bool:
    """
    Solicitar confirmación al usuario
    
    DOCTRINA: Validamos entrada del usuario
    """
    if not is_interactive_terminal():
        return default
    
    return Confirm.ask(f"[yellow]{message}[/yellow]", default=default)

def get_user_input(prompt: str, default: str = None, choices: List[str] = None) -> str:
    """
    Obtener entrada del usuario con validación
    
    DOCTRINA: Validamos entrada del usuario
    """
    if not is_interactive_terminal():
        return default or ""
    
    if choices:
        return Prompt.ask(
            f"[cyan]{prompt}[/cyan]", 
            choices=choices, 
            default=default
        )
    else:
        return Prompt.ask(
            f"[cyan]{prompt}[/cyan]", 
            default=default
        )

def validate_project_name(name: str) -> Dict[str, Any]:
    """
    Validar nombre de proyecto
    
    DOCTRINA: Validamos entrada del usuario
    
    Returns:
        Dict con 'valid' (bool) y 'errors' (list)
    """
    errors = []
    
    if not name:
        errors.append("El nombre del proyecto es requerido")
        return {"valid": False, "errors": errors}
    
    if len(name) < 2:
        errors.append("El nombre debe tener al menos 2 caracteres")
    
    if len(name) > 50:
        errors.append("El nombre no puede tener más de 50 caracteres")
    
    # Validar caracteres permitidos
    import re
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
        errors.append("El nombre debe comenzar con letra y solo contener letras, números, _ y -")
    
    # Validar nombres reservados
    reserved_names = [
        "con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", "com5",
        "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
        "lpt5", "lpt6", "lpt7", "lpt8", "lpt9", "test", "example", "sample"
    ]
    
    if name.lower() in reserved_names:
        errors.append(f"'{name}' es un nombre reservado")
    
    return {"valid": len(errors) == 0, "errors": errors}

def validate_template_name(template: str) -> Dict[str, Any]:
    """
    Validar nombre de template
    
    DOCTRINA: Validamos entrada del usuario
    """
    valid_templates = [
        "saas-basic",
        "api-only", 
        "frontend-only",
        "microservices",
        "e-commerce",
        "blog",
        "ai-ready",
        "minimal"
    ]
    
    if template in valid_templates:
        return {"valid": True, "errors": []}
    else:
        return {
            "valid": False,
            "errors": [f"Template inválido: {template}. Válidos: {', '.join(valid_templates)}"]
        }

def validate_project_directory(path: str, force: bool = False) -> Dict[str, Any]:
    """
    Validar directorio del proyecto
    
    DOCTRINA: Validamos entrada del usuario
    """
    errors = []
    project_path = Path(path)
    
    # Verificar si el directorio padre existe
    if not project_path.parent.exists():
        errors.append(f"El directorio padre no existe: {project_path.parent}")
        return {"valid": False, "errors": errors}
    
    # Verificar si el directorio del proyecto ya existe
    if project_path.exists():
        if not force:
            # Verificar si está vacío
            if any(project_path.iterdir()):
                errors.append(f"El directorio '{path}' no está vacío. Use --force para sobrescribir")
            else:
                # Directorio existe pero está vacío, está ok
                pass
        # Si force=True, está ok sobrescribir
    
    # Verificar permisos de escritura
    try:
        test_file = project_path.parent / ".test_write_permission"
        test_file.touch()
        test_file.unlink()
    except PermissionError:
        errors.append(f"Sin permisos de escritura en: {project_path.parent}")
    
    return {"valid": len(errors) == 0, "errors": errors}

def validate_features(features: List[str]) -> Dict[str, Any]:
    """
    Validar características del proyecto
    
    DOCTRINA: Validamos entrada del usuario
    """
    valid_features = [
        "authentication",
        "database", 
        "api",
        "frontend",
        "docker",
        "cicd",
        "monitoring",
        "ai",
        "testing",
        "documentation",
        "analytics",
        "caching",
        "search",
        "notifications",
        "payments"
    ]
    
    errors = []
    for feature in features:
        if feature not in valid_features:
            errors.append(f"Característica inválida: {feature}")
    
    return {"valid": len(errors) == 0, "errors": errors}

def detect_project_type() -> Optional[str]:
    """
    Detectar tipo de proyecto actual
    
    DOCTRINA: Utility para mejorar UX
    """
    current_dir = Path.cwd()
    
    # Verificar si es un proyecto Genesis
    if (current_dir / "genesis.json").exists():
        return "genesis"
    
    # Verificar otros tipos de proyecto
    if (current_dir / "package.json").exists():
        return "nodejs"
    
    if (current_dir / "requirements.txt").exists() or (current_dir / "pyproject.toml").exists():
        return "python"
    
    if (current_dir / "Cargo.toml").exists():
        return "rust"
    
    if (current_dir / "go.mod").exists():
        return "go"
    
    return None

def get_project_metadata() -> Optional[Dict[str, Any]]:
    """
    Obtener metadata del proyecto actual
    
    DOCTRINA: Utility para mejorar UX
    """
    genesis_file = Path("genesis.json")
    
    if not genesis_file.exists():
        return None
    
    try:
        import json
        with open(genesis_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def format_file_size(size_bytes: int) -> str:
    """
    Formatear tamaño de archivo de manera legible
    
    DOCTRINA: Utility para mejorar UX
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_directory_size(path: Path) -> int:
    """
    Obtener tamaño total de un directorio
    
    DOCTRINA: Utility para mejorar UX
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                try:
                    total_size += filepath.stat().st_size
                except (OSError, IOError):
                    # Skip files that can't be read
                    continue
    except (OSError, IOError):
        pass
    
    return total_size

def clean_ansi_codes(text: str) -> str:
    """
    Limpiar códigos ANSI de un texto
    
    DOCTRINA: Utility para mejorar UX
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def create_backup_name(original: str) -> str:
    """
    Crear nombre de backup único
    
    DOCTRINA: Utility para mejorar UX
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{original}_backup_{timestamp}"

def safe_remove_directory(path: Path) -> bool:
    """
    Eliminar directorio de manera segura
    
    DOCTRINA: Utility para mejorar UX
    """
    try:
        shutil.rmtree(path)
        return True
    except (OSError, IOError):
        return False

def safe_copy_file(src: Path, dst: Path) -> bool:
    """
    Copiar archivo de manera segura
    
    DOCTRINA: Utility para mejorar UX
    """
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except (OSError, IOError):
        return False

def get_available_port(start_port: int = 3000, max_attempts: int = 100) -> Optional[int]:
    """
    Encontrar puerto disponible
    
    DOCTRINA: Utility para mejorar UX
    """
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    return None

def format_duration(seconds: float) -> str:
    """
    Formatear duración de manera legible
    
    DOCTRINA: Utility para mejorar UX
    """
    if seconds < 1:
        return f"{seconds:.2f}s"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncar texto de manera elegante
    
    DOCTRINA: Utility para mejorar UX
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def get_env_info() -> Dict[str, Any]:
    """
    Obtener información del entorno
    
    DOCTRINA: Utility para mejorar UX
    """
    import platform
    
    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "system": platform.system(),
        "terminal_size": get_terminal_size(),
        "is_interactive": is_interactive_terminal(),
        "current_directory": str(Path.cwd()),
        "project_type": detect_project_type()
    }