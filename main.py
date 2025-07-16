#!/usr/bin/env python3
"""
Genesis CLI - Entry Point Principal

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- NO contiene templates ni agentes
- SÍ es la única interfaz de usuario
- SÍ valida entrada del usuario
- SÍ muestra progreso y estado
- Solo usa genesis-core como interfaz
"""

import sys
import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import typer
from typer.main import get_command
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

# DOCTRINA: Solo importamos genesis-core, nunca MCPturbo directamente
try:
    from genesis_core.orchestrator.core_orchestrator import CoreOrchestrator, ProjectGenerationRequest
    from genesis_core.config import initialize_config
    from genesis_core.logging import get_logger
except ImportError as e:
    print(f"ERROR: No se pudo importar genesis-core: {e}")
    print("Instala genesis-core: pip install genesis-core")
    sys.exit(1)

from genesis_cli import __version__
from genesis_cli.commands.utils import show_banner, check_dependencies
from genesis_cli.utils import get_terminal_size, is_interactive_terminal, get_user_confirmation
from genesis_cli.ui.console import genesis_console

# Configurar Rich Console
console = Console()
logger = get_logger("genesis.cli")

def version_callback(value: bool):
    """Callback para mostrar la versión y salir"""
    if value:
        console.print(f"[bold green]Genesis CLI v{__version__}[/bold green]")
        console.print("[cyan]Interfaz de línea de comandos para Genesis Engine[/cyan]")
        raise typer.Exit()

def validate_project_name(name: str) -> bool:
    """Validar nombre de proyecto según las reglas del ecosistema"""
    import re
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
        console.print("[red]❌ Nombre de proyecto inválido. Use solo letras, números, _ y -[/red]")
        return False
    
    if len(name) < 2 or len(name) > 50:
        console.print("[red]❌ Nombre debe tener entre 2 y 50 caracteres[/red]")
        return False
    
    return True

def validate_template_name(template: str) -> bool:
    """Validar nombre de template"""
    valid_templates = [
        "saas-basic", "api-only", "frontend-only", "microservices", 
        "e-commerce", "blog", "ai-ready", "minimal"
    ]
    
    if template not in valid_templates:
        console.print(f"[red]❌ Template inválido: {template}[/red]")
        console.print(f"[yellow]Templates disponibles: {', '.join(valid_templates)}[/yellow]")
        return False
    
    return True

# Crear aplicación Typer principal
app = typer.Typer(
    name="genesis",
    help="🚀 Genesis CLI - Interfaz de línea de comandos para Genesis Engine",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True
)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Mostrar versión de Genesis CLI",
        callback=version_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Mostrar información detallada"
    ),
    skip_project_check: bool = typer.Option(
        False,
        "--skip-project-check",
        help="Omitir verificación de genesis.json",
        envvar="GENESIS_SKIP_PROJECT_CHECK",
        hidden=True,
    )
):
    """
    🚀 Genesis CLI - Interfaz de línea de comandos para Genesis Engine

    Genesis CLI te permite crear, gestionar y desplegar aplicaciones
    completas usando el ecosistema Genesis Engine.
    """
    if ctx.invoked_subcommand is None:
        show_banner()
        console.print("\n[bold yellow]💡 Usa 'genesis --help' para ver comandos disponibles[/bold yellow]")
        console.print("[bold yellow]💡 Usa 'genesis init <nombre>' para crear un proyecto[/bold yellow]")
        
    # DOCTRINA: Solo inicializamos config de genesis-core
    try:
        initialize_config()
        if verbose:
            logger.info("Configuración inicializada en modo verbose")
    except Exception as e:
        console.print(f"[red]❌ Error inicializando configuración: {e}[/red]")
        raise typer.Exit(1)

    ctx.obj = {"skip_project_check": skip_project_check, "verbose": verbose}

@app.command("init")
def init(
    project_name: str = typer.Argument(
        help="Nombre del proyecto a crear"
    ),
    template: str = typer.Option(
        "saas-basic",
        "--template",
        "-t",
        help="Plantilla a usar"
    ),
    no_interactive: bool = typer.Option(
        False,
        "--no-interactive",
        help="Modo no interactivo, usar valores por defecto"
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output",
        "-o", 
        help="Directorio de salida (por defecto: directorio actual)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Sobrescribir proyecto existente"
    )
):
    """
    🏗️ Inicializar un nuevo proyecto Genesis
    
    Crea un proyecto completo usando la plantilla seleccionada.
    Los agentes trabajarán en conjunto para generar código optimizado.
    """
    try:
        # DOCTRINA: Validamos entrada del usuario
        if not validate_project_name(project_name):
            raise typer.Exit(1)
        
        if not validate_template_name(template):
            raise typer.Exit(1)
        
        # Validar directorio de salida
        if output_dir:
            output_path = Path(output_dir)
            if not output_path.exists():
                console.print(f"[red]❌ Directorio de salida no existe: {output_dir}[/red]")
                raise typer.Exit(1)
        else:
            output_path = Path.cwd()
        
        project_path = output_path / project_name
        
        # Verificar si el proyecto ya existe
        if project_path.exists() and not force:
            if not no_interactive:
                if not get_user_confirmation(f"⚠️ El directorio '{project_name}' ya existe. ¿Continuar?"):
                    console.print("[yellow]Operación cancelada[/yellow]")
                    raise typer.Exit(0)
            else:
                console.print(f"[red]❌ El directorio '{project_name}' ya existe. Use --force para sobrescribir[/red]")
                raise typer.Exit(1)
        
        # DOCTRINA: Verificar dependencias como parte de UX
        if not check_dependencies():
            console.print("[red]❌ Algunas dependencias no están disponibles[/red]")
            if not no_interactive:
                if not get_user_confirmation("¿Continuar de todos modos?"):
                    raise typer.Exit(1)
            else:
                raise typer.Exit(1)
        
        # Configurar proyecto
        config = {
            "name": project_name,
            "template": template,
            "output_path": str(output_path),
            "force": force,
            "interactive": not no_interactive
        }
        
        # Modo interactivo para configuración adicional
        if not no_interactive:
            config["description"] = Prompt.ask(
                "[cyan]Descripción del proyecto[/cyan]", 
                default="Aplicación generada con Genesis Engine"
            )
            
            # Seleccionar características básicas
            features = []
            if Confirm.ask("¿Incluir autenticación?", default=True):
                features.append("authentication")
            if Confirm.ask("¿Incluir base de datos?", default=True):
                features.append("database")
            if Confirm.ask("¿Incluir API REST?", default=True):
                features.append("api")
            if Confirm.ask("¿Incluir frontend?", default=True):
                features.append("frontend")
            if Confirm.ask("¿Incluir Docker?", default=True):
                features.append("docker")
            if Confirm.ask("¿Incluir CI/CD?", default=True):
                features.append("cicd")
            
            config["features"] = features
        else:
            config["description"] = "Aplicación generada con Genesis Engine"
            config["features"] = ["authentication", "database", "api", "frontend", "docker", "cicd"]
        
        # DOCTRINA: Mostramos progreso y estado elegante
        console.print(f"\n[bold green]🚀 Creando proyecto '{project_name}'...[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Conectando con Genesis Core...", total=None)
            
            # DOCTRINA: Solo usamos genesis-core como interfaz
            result = asyncio.run(_create_project_async(config, progress, task))
            
            if result.get("success"):
                console.print(f"\n[bold green]✅ Proyecto '{project_name}' creado exitosamente![/bold green]")
                console.print(f"[green]📁 Ubicación: {result.get('project_path', project_path)}[/green]")
                
                if result.get("generated_files"):
                    console.print(f"[green]📄 Archivos generados: {len(result['generated_files'])}[/green]")
                
                # Mostrar siguientes pasos
                console.print("\n[bold cyan]📋 Siguientes pasos:[/bold cyan]")
                console.print(f"1. [cyan]cd {project_name}[/cyan]")
                console.print("2. [cyan]genesis deploy --env local[/cyan]")
                console.print("3. [cyan]genesis status[/cyan]")
                
            else:
                console.print(f"\n[red]❌ Error creando proyecto: {result.get('error', 'Error desconocido')}[/red]")
                raise typer.Exit(1)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Operación cancelada por el usuario[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Error en init: {e}", exc_info=True)
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        raise typer.Exit(1)

async def _create_project_async(config: Dict[str, Any], progress: Progress, task_id) -> Dict[str, Any]:
    """
    Crear proyecto de forma asíncrona
    DOCTRINA: Solo usamos genesis-core, nunca MCPturbo directamente
    """
    try:
        progress.update(task_id, description="Inicializando Genesis Core...")
        orchestrator = CoreOrchestrator()
        
        progress.update(task_id, description="Preparando solicitud de generación...")
        request = ProjectGenerationRequest(
            name=config.get("name", "project"),
            template=config.get("template", "saas-basic"),
            features=config.get("features", []),
            options=config,
        )
        
        progress.update(task_id, description="Ejecutando generación de proyecto...")
        result = await orchestrator.execute_project_generation(request)
        
        if result.success:
            return {
                "success": True,
                "project_path": result.project_path,
                "generated_files": result.generated_files,
                "result": result.data
            }
        else:
            return {
                "success": False,
                "error": result.error or "Error desconocido en generación"
            }
        
    except Exception as e:
        logger.error(f"Error en creación asíncrona: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@app.command("deploy")
def deploy(
    ctx: typer.Context,
    environment: str = typer.Option(
        "local",
        "--env",
        "-e",
        help="Entorno de despliegue (local, staging, production)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Forzar despliegue sin confirmación"
    )
):
    """
    🚀 Desplegar aplicación en el entorno especificado
    
    Ejecuta el proceso de despliegue usando Genesis Core.
    """
    try:
        skip_check = ctx.obj.get("skip_project_check") if ctx.obj else False
        
        # DOCTRINA: Validamos entrada del usuario
        if not skip_check and not Path("genesis.json").exists():
            console.print("[red]❌ No estás en un proyecto Genesis[/red]")
            console.print("[yellow]💡 Ejecuta 'genesis init <nombre>' para crear uno[/yellow]")
            raise typer.Exit(1)
        
        # Validar entorno
        valid_envs = ["local", "staging", "production"]
        if environment not in valid_envs:
            console.print(f"[red]❌ Entorno inválido: {environment}[/red]")
            console.print(f"[yellow]💡 Entornos válidos: {', '.join(valid_envs)}[/yellow]")
            raise typer.Exit(1)
        
        console.print(f"[bold blue]🚀 Desplegando en entorno: {environment}[/bold blue]")
        
        # Confirmación para production
        if environment == "production" and not force:
            if not get_user_confirmation("⚠️ ¿Confirmas despliegue en producción?"):
                console.print("[yellow]Despliegue cancelado[/yellow]")
                raise typer.Exit(0)
        
        # Ejecutar despliegue
        config = {
            "environment": environment,
            "force": force
        }
        
        result = asyncio.run(_deploy_async(config))
        
        if result.get("success"):
            console.print(f"[bold green]✅ Despliegue exitoso en {environment}[/bold green]")
            if result.get("url"):
                console.print(f"[green]🌐 URL: {result['url']}[/green]")
        else:
            console.print(f"[red]❌ Error en despliegue: {result.get('error', 'Error desconocido')}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Error en deploy: {e}", exc_info=True)
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        raise typer.Exit(1)

async def _deploy_async(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecutar despliegue de forma asíncrona
    DOCTRINA: Solo usamos genesis-core
    """
    try:
        orchestrator = CoreOrchestrator()
        
        request = ProjectGenerationRequest(
            name="deploy",
            template="deploy",
            options=config,
        )
        
        result = await orchestrator.execute_deployment(request)
        
        if result.success:
            return {
                "success": True,
                "url": result.deployment_url,
                "result": result.data
            }
        else:
            return {
                "success": False,
                "error": result.error or "Error desconocido en despliegue"
            }
            
    except Exception as e:
        logger.error(f"Error en deploy async: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@app.command("generate")
def generate(
    ctx: typer.Context,
    component: str = typer.Argument(
        help="Tipo de componente a generar (model, endpoint, page, component)"
    ),
    name: str = typer.Argument(
        help="Nombre del componente"
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        help="Modo interactivo para configuración"
    )
):
    """
    ⚡ Generar componentes específicos
    
    Genera componentes individuales usando Genesis Core.
    """
    try:
        skip_check = ctx.obj.get("skip_project_check") if ctx.obj else False
        
        # DOCTRINA: Validamos entrada del usuario
        if not skip_check and not Path("genesis.json").exists():
            console.print("[red]❌ No estás en un proyecto Genesis[/red]")
            console.print("[yellow]💡 Ejecuta 'genesis init <nombre>' para crear uno[/yellow]")
            raise typer.Exit(1)
        
        # Validar tipo de componente
        valid_components = ["model", "endpoint", "page", "component", "test"]
        if component not in valid_components:
            console.print(f"[red]❌ Tipo de componente inválido: {component}[/red]")
            console.print(f"[yellow]💡 Tipos válidos: {', '.join(valid_components)}[/yellow]")
            raise typer.Exit(1)
        
        # Validar nombre
        if not validate_project_name(name):
            raise typer.Exit(1)
        
        console.print(f"[bold blue]⚡ Generando {component}: {name}[/bold blue]")
        
        # Configurar generación
        config = {
            "component": component,
            "name": name,
            "interactive": interactive
        }
        
        # Ejecutar generación
        result = asyncio.run(_generate_async(config))
        
        if result.get("success"):
            console.print(f"[bold green]✅ {component.capitalize()} '{name}' generado exitosamente[/bold green]")
            if result.get("files"):
                console.print(f"[green]📄 Archivos creados: {len(result['files'])}[/green]")
                for file in result["files"]:
                    console.print(f"  • {file}")
        else:
            console.print(f"[red]❌ Error generando {component}: {result.get('error', 'Error desconocido')}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Error en generate: {e}", exc_info=True)
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        raise typer.Exit(1)

async def _generate_async(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecutar generación de forma asíncrona
    DOCTRINA: Solo usamos genesis-core
    """
    try:
        orchestrator = CoreOrchestrator()
        
        request = ProjectGenerationRequest(
            name="generate_component",
            template=config.get("component", "component"),
            options=config,
        )
        
        result = await orchestrator.execute_component_generation(request)
        
        if result.success:
            return {
                "success": True,
                "files": result.generated_files,
                "result": result.data
            }
        else:
            return {
                "success": False,
                "error": result.error or "Error desconocido en generación"
            }
            
    except Exception as e:
        logger.error(f"Error en generate async: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }

@app.command("status")
def status(ctx: typer.Context):
    """
    📊 Mostrar estado del proyecto actual
    
    Muestra información detallada sobre el proyecto Genesis.
    """
    try:
        console.print("[bold blue]📊 Estado del Proyecto Genesis[/bold blue]")
        
        # Verificar si estamos en un proyecto Genesis
        project_file = Path("genesis.json")
        skip_check = ctx.obj.get("skip_project_check") if ctx.obj else False
        
        if not skip_check and not project_file.exists():
            console.print("[red]❌ No estás en un proyecto Genesis[/red]")
            console.print("[yellow]💡 Ejecuta 'genesis init <nombre>' para crear uno[/yellow]")
            raise typer.Exit(1)
        
        # Leer metadata del proyecto
        try:
            with open(project_file, 'r') as f:
                metadata = json.load(f)
            
            console.print("[green]✅ Proyecto Genesis detectado[/green]")
            
            # DOCTRINA: Mostrar estado de manera elegante
            table = Table(title="Información del Proyecto")
            table.add_column("Propiedad", style="cyan")
            table.add_column("Valor", style="green")
            
            table.add_row("Nombre", metadata.get("name", "N/A"))
            table.add_row("Template", metadata.get("template", "N/A"))
            table.add_row("Versión", metadata.get("version", "N/A"))
            table.add_row("Generado", metadata.get("created_at", "N/A"))
            table.add_row("Archivos", str(len(metadata.get("generated_files", []))))
            
            console.print(table)
            
            # Mostrar características si existen
            features = metadata.get("features", [])
            if features:
                console.print(f"\n[bold]🎯 Características incluidas:[/bold]")
                for feature in features:
                    console.print(f"  • {feature}")
            
        except Exception as e:
            console.print(f"[red]❌ Error leyendo metadata: {e}[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Error en status: {e}", exc_info=True)
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        raise typer.Exit(1)

@app.command("doctor")
def doctor():
    """
    🔍 Diagnosticar el entorno de desarrollo
    
    Ejecuta un diagnóstico completo del sistema.
    """
    try:
        console.print("[bold blue]🔍 Diagnóstico del Sistema Genesis[/bold blue]")
        
        # DOCTRINA: Verificar dependencias como parte de UX
        deps_ok = check_dependencies()
        
        # Verificar conexión con genesis-core
        console.print("\n[bold cyan]⚙️ Verificando Genesis Core...[/bold cyan]")
        try:
            orchestrator = CoreOrchestrator()
            console.print("[green]✅ Genesis Core disponible[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error conectando con Genesis Core: {e}[/red]")
            deps_ok = False
        
        # Resultado final
        if deps_ok:
            console.print(f"\n[bold green]✅ Sistema listo para usar Genesis CLI[/bold green]")
            console.print("[green]💡 Ejecuta 'genesis init <nombre>' para crear un proyecto[/green]")
        else:
            console.print(f"\n[bold red]❌ Sistema no está listo[/bold red]")
            console.print("[red]🔧 Instala las dependencias faltantes y vuelve a ejecutar[/red]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Error en doctor: {e}", exc_info=True)
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        raise typer.Exit(1)

@app.command("help")
def help_cmd():
    """Mostrar la ayuda completa de la CLI"""
    show_banner()
    command = get_command(app)
    ctx = typer.Context(command)
    console.print(command.get_help(ctx))

# Punto de entrada principal
def main_entry():
    """Entry point principal para el script de consola"""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Operación cancelada por el usuario[/yellow]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado en main: {e}", exc_info=True)
        console.print(f"[red]❌ Error inesperado: {e}[/red]")
        sys.exit(1)

# Para compatibilidad con python -m
if __name__ == "__main__":
    main_entry()