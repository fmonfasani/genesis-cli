"""
Utilidades para comandos CLI

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- SÍ valida entrada del usuario
- SÍ muestra progreso y estado elegante
- Solo usa genesis-core como interfaz
"""

import sys
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from genesis_cli import __version__

console = Console()

def show_banner():
    """
    Mostrar banner elegante de Genesis CLI
    DOCTRINA: Enfocado en UX/UI elegante
    """
    banner_text = Text()
    banner_text.append("🚀 ", style="bold cyan")
    banner_text.append("GENESIS CLI", style="bold white")
    banner_text.append(f" v{__version__}", style="bold green")
    banner_text.append("\n")
    banner_text.append("Interfaz de línea de comandos para Genesis Engine", style="italic cyan")
    banner_text.append("\n")
    banner_text.append("Crea aplicaciones full-stack modernas con agentes IA", style="dim cyan")
    
    console.print(Panel.fit(
        banner_text,
        border_style="cyan",
        padding=(1, 2),
        title="[bold blue]Genesis Engine[/bold blue]",
        subtitle="[dim]Powered by AI Agents[/dim]"
    ))

def check_dependencies() -> bool:
    """
    Verificar dependencias básicas del sistema
    
    DOCTRINA: Validamos entrada del usuario y mostramos estado
    
    Returns:
        bool: True si todas las dependencias están disponibles
    """
    missing = []
    warnings = []
    
    # Verificar Python
    if sys.version_info < (3, 8):
        missing.append("Python >= 3.8")
    
    # Verificar herramientas básicas
    def _check_tool(cmd: list, name: str, required: bool = True) -> bool:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    # Dependencias críticas
    if not _check_tool(["node", "--version"], "Node.js"):
        missing.append("Node.js")
    
    if not _check_tool(["git", "--version"], "Git"):
        missing.append("Git")
    
    # Dependencias opcionales
    if not _check_tool(["docker", "--version"], "Docker", required=False):
        warnings.append("Docker (recomendado para despliegue)")
    
    if not _check_tool(["npm", "--version"], "npm", required=False):
        warnings.append("npm (recomendado para proyectos frontend)")
    
    # Crear tabla de diagnóstico
    table = Table(title="🔍 Verificación de Dependencias")
    table.add_column("Componente", style="cyan")
    table.add_column("Estado", style="green")
    table.add_column("Notas", style="yellow")
    
    # Mostrar Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_status = "✅ OK" if sys.version_info >= (3, 8) else "❌ Muy antiguo"
    table.add_row("Python", python_status, f"v{python_version}")
    
    # Mostrar otras dependencias
    dependencies = [
        ("Node.js", ["node", "--version"]),
        ("Git", ["git", "--version"]),
        ("Docker", ["docker", "--version"]),
        ("npm", ["npm", "--version"])
    ]
    
    for name, cmd in dependencies:
        if _check_tool(cmd, name, required=False):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                version = result.stdout.strip()
                table.add_row(name, "✅ OK", version)
            except:
                table.add_row(name, "✅ OK", "Instalado")
        else:
            status = "❌ Faltante" if name in ["Node.js", "Git"] else "⚠️ Opcional"
            table.add_row(name, status, "No encontrado")
    
    console.print(table)
    
    # Mostrar errores y advertencias
    if missing:
        console.print(f"\n[bold red]❌ Dependencias faltantes:[/bold red]")
        for item in missing:
            console.print(f"  • {item}")
        console.print("\n[red]🔧 Instala las dependencias faltantes para continuar[/red]")
    
    if warnings:
        console.print(f"\n[bold yellow]⚠️ Recomendaciones:[/bold yellow]")
        for item in warnings:
            console.print(f"  • {item}")
    
    if not missing and not warnings:
        console.print("\n[bold green]🎉 ¡Todas las dependencias están listas![/bold green]")
    
    return len(missing) == 0

def validate_project_config(config: dict) -> list:
    """
    Validar configuración de proyecto
    
    DOCTRINA: Validamos entrada del usuario
    
    Args:
        config: Configuración del proyecto
        
    Returns:
        list: Lista de errores de validación
    """
    errors = []
    
    # Validar nombre
    name = config.get("name", "")
    if not name:
        errors.append("El nombre del proyecto es requerido")
    elif len(name) < 2:
        errors.append("El nombre del proyecto debe tener al menos 2 caracteres")
    elif len(name) > 50:
        errors.append("El nombre del proyecto no puede tener más de 50 caracteres")
    
    # Validar template
    template = config.get("template", "")
    valid_templates = [
        "saas-basic", "api-only", "frontend-only", "microservices",
        "e-commerce", "blog", "ai-ready", "minimal"
    ]
    
    if template and template not in valid_templates:
        errors.append(f"Template inválido: {template}. Válidos: {', '.join(valid_templates)}")
    
    # Validar features
    features = config.get("features", [])
    if features and not isinstance(features, list):
        errors.append("Las características deben ser una lista")
    
    valid_features = [
        "authentication", "database", "api", "frontend", "docker",
        "cicd", "monitoring", "ai", "testing", "documentation"
    ]
    
    for feature in features:
        if feature not in valid_features:
            errors.append(f"Característica inválida: {feature}")
    
    return errors

def format_validation_errors(errors: list) -> None:
    """
    Mostrar errores de validación de manera elegante
    
    DOCTRINA: Mostramos estado de manera elegante
    """
    if not errors:
        return
    
    console.print("[bold red]❌ Errores de validación:[/bold red]")
    for error in errors:
        console.print(f"  • {error}")
    console.print()

def show_project_info(project_data: dict) -> None:
    """
    Mostrar información del proyecto de manera elegante
    
    DOCTRINA: Mostramos estado de manera elegante
    """
    table = Table(title="📋 Información del Proyecto")
    table.add_column("Propiedad", style="cyan")
    table.add_column("Valor", style="green")
    
    table.add_row("Nombre", project_data.get("name", "N/A"))
    table.add_row("Template", project_data.get("template", "N/A"))
    table.add_row("Versión", project_data.get("version", "N/A"))
    table.add_row("Descripción", project_data.get("description", "N/A"))
    table.add_row("Creado", project_data.get("created_at", "N/A"))
    
    console.print(table)
    
    # Mostrar features si existen
    features = project_data.get("features", [])
    if features:
        console.print(f"\n[bold]🎯 Características incluidas:[/bold]")
        for feature in features:
            console.print(f"  • {feature}")
    
    # Mostrar archivos generados
    generated_files = project_data.get("generated_files", [])
    if generated_files:
        console.print(f"\n[bold]📁 Archivos generados ({len(generated_files)}):[/bold]")
        for file_path in generated_files[:10]:  # Mostrar solo los primeros 10
            console.print(f"  • {file_path}")
        
        if len(generated_files) > 10:
            console.print(f"  ... y {len(generated_files) - 10} archivos más")

def show_success_message(operation: str, details: dict = None) -> None:
    """
    Mostrar mensaje de éxito de manera elegante
    
    DOCTRINA: Mostramos estado de manera elegante
    """
    console.print(f"\n[bold green]✅ {operation} completado exitosamente![/bold green]")
    
    if details:
        for key, value in details.items():
            if isinstance(value, list):
                console.print(f"[green]{key}: {len(value)} elementos[/green]")
            else:
                console.print(f"[green]{key}: {value}[/green]")

def show_error_message(operation: str, error: str) -> None:
    """
    Mostrar mensaje de error de manera elegante
    
    DOCTRINA: Mostramos estado de manera elegante
    """
    console.print(f"\n[bold red]❌ Error en {operation}:[/bold red]")
    console.print(f"[red]{error}[/red]")

def show_next_steps(steps: list) -> None:
    """
    Mostrar siguientes pasos de manera elegante
    
    DOCTRINA: Mostramos estado de manera elegante
    """
    console.print("\n[bold cyan]📋 Siguientes pasos:[/bold cyan]")
    for i, step in enumerate(steps, 1):
        console.print(f"{i}. [cyan]{step}[/cyan]")

def confirm_action(message: str, default: bool = False) -> bool:
    """
    Solicitar confirmación del usuario
    
    DOCTRINA: Validamos entrada del usuario
    """
    from rich.prompt import Confirm
    return Confirm.ask(message, default=default)

def get_user_input(prompt: str, default: str = None) -> str:
    """
    Obtener entrada del usuario
    
    DOCTRINA: Validamos entrada del usuario
    """
    from rich.prompt import Prompt
    return Prompt.ask(prompt, default=default)

def show_progress_task(description: str):
    """
    Contexto para mostrar progreso de tarea
    
    DOCTRINA: Mostramos progreso y estado
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    )