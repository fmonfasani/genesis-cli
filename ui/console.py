"""
Console UI para Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- SÍ proporciona UI elegante y funcional
- SÍ maneja progreso y estado visual
- Enfocado en UX/UI excelente
"""

from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.syntax import Syntax
from rich.tree import Tree
from rich.align import Align
from rich.columns import Columns
from rich.markdown import Markdown
from rich.json import JSON
from contextlib import contextmanager
from pathlib import Path
import json

# Console principal para Genesis CLI
genesis_console = Console()

class GenesisUI:
    """
    Interfaz de usuario elegante para Genesis CLI
    
    DOCTRINA: Enfocado en UX/UI excelente
    """
    
    def __init__(self):
        self.console = genesis_console
    
    def show_welcome(self, version: str = "1.0.0"):
        """Mostrar mensaje de bienvenida elegante"""
        welcome_text = Text()
        welcome_text.append("🚀 ", style="bold cyan")
        welcome_text.append("Bienvenido a Genesis CLI", style="bold white")
        welcome_text.append(f" v{version}", style="bold green")
        welcome_text.append("\n\n")
        welcome_text.append("Crea aplicaciones full-stack modernas con agentes IA", style="italic cyan")
        
        self.console.print(Panel.fit(
            welcome_text,
            border_style="cyan",
            padding=(1, 2)
        ))
    
    def show_project_created(self, project_name: str, project_path: str, details: Dict[str, Any]):
        """Mostrar mensaje de proyecto creado exitosamente"""
        success_text = Text()
        success_text.append("✅ ", style="bold green")
        success_text.append(f"Proyecto '{project_name}' creado exitosamente!", style="bold green")
        success_text.append("\n\n")
        success_text.append(f"📁 Ubicación: {project_path}", style="cyan")
        
        if details.get("generated_files"):
            success_text.append(f"\n📄 Archivos generados: {len(details['generated_files'])}", style="green")
        
        if details.get("features"):
            success_text.append(f"\n🎯 Características: {', '.join(details['features'])}", style="yellow")
        
        self.console.print(Panel(
            success_text,
            title="[bold green]Proyecto Creado[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))
    
    def show_next_steps(self, project_name: str, steps: List[str]):
        """Mostrar siguientes pasos de manera elegante"""
        tree = Tree("📋 [bold cyan]Siguientes pasos:[/bold cyan]")
        
        for i, step in enumerate(steps, 1):
            tree.add(f"[cyan]{i}. {step}[/cyan]")
        
        self.console.print(tree)
    
    def show_project_status(self, project_data: Dict[str, Any]):
        """Mostrar estado del proyecto de manera elegante"""
        # Información básica
        basic_table = Table(title="📋 Información del Proyecto", show_header=True)
        basic_table.add_column("Propiedad", style="cyan")
        basic_table.add_column("Valor", style="green")
        
        basic_table.add_row("Nombre", project_data.get("name", "N/A"))
        basic_table.add_row("Template", project_data.get("template", "N/A"))
        basic_table.add_row("Versión", project_data.get("version", "N/A"))
        basic_table.add_row("Descripción", project_data.get("description", "N/A"))
        basic_table.add_row("Creado", project_data.get("created_at", "N/A"))
        
        self.console.print(basic_table)
        
        # Características
        features = project_data.get("features", [])
        if features:
            self.console.print(f"\n[bold]🎯 Características incluidas:[/bold]")
            feature_columns = []
            for feature in features:
                feature_columns.append(f"[green]• {feature}[/green]")
            
            # Mostrar en columnas si hay muchas características
            if len(feature_columns) > 6:
                self.console.print(Columns(feature_columns, equal=True))
            else:
                for feature in feature_columns:
                    self.console.print(f"  {feature}")
        
        # Archivos generados
        generated_files = project_data.get("generated_files", [])
        if generated_files:
            self.console.print(f"\n[bold]📁 Archivos generados ({len(generated_files)}):[/bold]")
            
            # Agrupar por tipo
            file_tree = Tree("📁 Estructura del proyecto")
            directories = {}
            
            for file_path in generated_files:
                parts = Path(file_path).parts
                if len(parts) > 1:
                    dir_name = parts[0]
                    if dir_name not in directories:
                        directories[dir_name] = []
                    directories[dir_name].append(str(Path(*parts[1:])))
                else:
                    file_tree.add(f"📄 {file_path}")
            
            for dir_name, files in directories.items():
                dir_branch = file_tree.add(f"📁 {dir_name}")
                for file in files[:5]:  # Mostrar solo los primeros 5
                    dir_branch.add(f"📄 {file}")
                if len(files) > 5:
                    dir_branch.add(f"[dim]... y {len(files) - 5} archivos más[/dim]")
            
            self.console.print(file_tree)
    
    def show_deployment_status(self, environment: str, status: str, details: Dict[str, Any]):
        """Mostrar estado del despliegue"""
        if status == "success":
            status_text = Text()
            status_text.append("✅ ", style="bold green")
            status_text.append(f"Despliegue exitoso en {environment}", style="bold green")
            
            if details.get("url"):
                status_text.append(f"\n🌐 URL: {details['url']}", style="cyan")
            
            if details.get("services"):
                status_text.append(f"\n🔧 Servicios: {', '.join(details['services'])}", style="yellow")
            
            self.console.print(Panel(
                status_text,
                title="[bold green]Despliegue Completado[/bold green]",
                border_style="green"
            ))
        else:
            error_text = Text()
            error_text.append("❌ ", style="bold red")
            error_text.append(f"Error en despliegue: {details.get('error', 'Error desconocido')}", style="bold red")
            
            self.console.print(Panel(
                error_text,
                title="[bold red]Error de Despliegue[/bold red]",
                border_style="red"
            ))
    
    def show_dependency_check(self, results: Dict[str, Any]):
        """Mostrar resultados de verificación de dependencias"""
        table = Table(title="🔍 Verificación de Dependencias")
        table.add_column("Componente", style="cyan")
        table.add_column("Estado", style="green")
        table.add_column("Versión", style="yellow")
        table.add_column("Notas", style="dim")
        
        for dep_name, dep_info in results.items():
            if dep_info.get("installed"):
                status = "✅ OK"
                version = dep_info.get("version", "Instalado")
                notes = dep_info.get("notes", "")
            else:
                status = "❌ Faltante" if dep_info.get("required") else "⚠️ Opcional"
                version = "No encontrado"
                notes = dep_info.get("notes", "")
            
            table.add_row(dep_name, status, version, notes)
        
        self.console.print(table)
    
    def show_template_options(self, templates: List[Dict[str, Any]]):
        """Mostrar opciones de templates disponibles"""
        table = Table(title="📋 Templates Disponibles")
        table.add_column("Template", style="cyan")
        table.add_column("Descripción", style="green")
        table.add_column("Características", style="yellow")
        table.add_column("Complejidad", style="magenta")
        
        for template in templates:
            features = ", ".join(template.get("features", []))
            complexity = template.get("complexity", "Media")
            
            table.add_row(
                template.get("name", "N/A"),
                template.get("description", "N/A"),
                features,
                complexity
            )
        
        self.console.print(table)
    
    def show_generation_result(self, component: str, name: str, files: List[str]):
        """Mostrar resultado de generación de componente"""
        success_text = Text()
        success_text.append("✅ ", style="bold green")
        success_text.append(f"{component.capitalize()} '{name}' generado exitosamente!", style="bold green")
        success_text.append(f"\n\n📄 Archivos creados: {len(files)}", style="cyan")
        
        self.console.print(Panel(
            success_text,
            title="[bold green]Generación Completada[/bold green]",
            border_style="green"
        ))
        
        # Mostrar archivos creados
        if files:
            file_tree = Tree("📁 Archivos creados")
            for file in files:
                file_tree.add(f"📄 {file}")
            
            self.console.print(file_tree)
    
    def show_error(self, title: str, message: str, details: Optional[str] = None):
        """Mostrar error de manera elegante"""
        error_text = Text()
        error_text.append("❌ ", style="bold red")
        error_text.append(message, style="bold red")
        
        if details:
            error_text.append(f"\n\n{details}", style="red")
        
        self.console.print(Panel(
            error_text,
            title=f"[bold red]{title}[/bold red]",
            border_style="red"
        ))
    
    def show_warning(self, title: str, message: str):
        """Mostrar advertencia de manera elegante"""
        warning_text = Text()
        warning_text.append("⚠️ ", style="bold yellow")
        warning_text.append(message, style="bold yellow")
        
        self.console.print(Panel(
            warning_text,
            title=f"[bold yellow]{title}[/bold yellow]",
            border_style="yellow"
        ))
    
    def show_json_data(self, data: Dict[str, Any], title: str = "Datos"):
        """Mostrar datos JSON de manera elegante"""
        json_data = JSON.from_data(data)
        
        self.console.print(Panel(
            json_data,
            title=f"[bold cyan]{title}[/bold cyan]",
            border_style="cyan"
        ))
    
    def show_code_snippet(self, code: str, language: str = "python", title: str = "Código"):
        """Mostrar snippet de código con syntax highlighting"""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        
        self.console.print(Panel(
            syntax,
            title=f"[bold cyan]{title}[/bold cyan]",
            border_style="cyan"
        ))
    
    @contextmanager
    def show_progress(self, description: str = "Procesando..."):
        """Context manager para mostrar progreso"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(description, total=None)
            yield progress, task
    
    def ask_user(self, question: str, default: Optional[str] = None, choices: Optional[List[str]] = None) -> str:
        """Solicitar entrada del usuario"""
        if choices:
            return Prompt.ask(
                f"[cyan]{question}[/cyan]",
                choices=choices,
                default=default
            )
        else:
            return Prompt.ask(
                f"[cyan]{question}[/cyan]",
                default=default
            )
    
    def ask_confirmation(self, question: str, default: bool = False) -> bool:
        """Solicitar confirmación del usuario"""
        return Confirm.ask(
            f"[yellow]{question}[/yellow]",
            default=default
        )
    
    def ask_number(self, question: str, default: Optional[int] = None) -> int:
        """Solicitar número del usuario"""
        return IntPrompt.ask(
            f"[cyan]{question}[/cyan]",
            default=default
        )

# Instancia global para usar en toda la aplicación
ui = GenesisUI()