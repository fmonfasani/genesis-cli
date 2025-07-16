"""
Excepciones específicas para Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- SÍ maneja errores específicos de CLI
- SÍ proporciona mensajes de error elegantes
- Enfocado en UX/UI para manejo de errores
"""

from typing import Optional, Dict, Any, List


class GenesisCliException(Exception):
    """
    Excepción base para Genesis CLI
    
    DOCTRINA: Solo maneja errores de interfaz de usuario
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        
    def __str__(self) -> str:
        return self.message
    
    def get_formatted_message(self) -> str:
        """Obtener mensaje formateado para mostrar al usuario"""
        return f"❌ {self.message}"


class ValidationError(GenesisCliException):
    """
    Error de validación de entrada del usuario
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def __init__(self, message: str, field: Optional[str] = None, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.field = field
        self.errors = errors or []
        
    def get_formatted_message(self) -> str:
        """Obtener mensaje formateado para mostrar al usuario"""
        if self.field:
            msg = f"❌ Error en '{self.field}': {self.message}"
        else:
            msg = f"❌ Error de validación: {self.message}"
        
        if self.errors:
            msg += "\n"
            for error in self.errors:
                msg += f"  • {error}\n"
        
        return msg.rstrip()


class ProjectNameError(ValidationError):
    """Error específico para nombres de proyecto inválidos"""
    
    def __init__(self, name: str, reason: str):
        super().__init__(f"Nombre de proyecto inválido: {name}", field="project_name")
        self.name = name
        self.reason = reason
        
    def get_formatted_message(self) -> str:
        return f"❌ Nombre de proyecto inválido: '{self.name}'\n  • {self.reason}"


class TemplateError(ValidationError):
    """Error específico para templates inválidos"""
    
    def __init__(self, template: str, available_templates: Optional[List[str]] = None):
        super().__init__(f"Template inválido: {template}", field="template")
        self.template = template
        self.available_templates = available_templates or []
        
    def get_formatted_message(self) -> str:
        msg = f"❌ Template inválido: '{self.template}'"
        if self.available_templates:
            msg += f"\n  💡 Templates disponibles: {', '.join(self.available_templates)}"
        return msg


class DirectoryError(GenesisCliException):
    """Error relacionado con directorios y archivos"""
    
    def __init__(self, message: str, path: str, operation: str = "access"):
        super().__init__(message)
        self.path = path
        self.operation = operation
        
    def get_formatted_message(self) -> str:
        return f"❌ Error de {self.operation} en '{self.path}': {self.message}"


class DependencyError(GenesisCliException):
    """Error relacionado con dependencias faltantes"""
    
    def __init__(self, message: str, missing_deps: Optional[List[str]] = None):
        super().__init__(message)
        self.missing_deps = missing_deps or []
        
    def get_formatted_message(self) -> str:
        msg = f"❌ Error de dependencias: {self.message}"
        if self.missing_deps:
            msg += "\n  🔧 Dependencias faltantes:"
            for dep in self.missing_deps:
                msg += f"\n    • {dep}"
        return msg


class ConfigurationError(GenesisCliException):
    """Error de configuración de CLI"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key
        
    def get_formatted_message(self) -> str:
        if self.config_key:
            return f"❌ Error de configuración en '{self.config_key}': {self.message}"
        else:
            return f"❌ Error de configuración: {self.message}"


class UserInterruptError(GenesisCliException):
    """Error cuando el usuario interrumpe la operación"""
    
    def __init__(self, operation: str = "operación"):
        super().__init__(f"Operación '{operation}' cancelada por el usuario")
        self.operation = operation
        
    def get_formatted_message(self) -> str:
        return f"⚠️ Operación '{self.operation}' cancelada por el usuario"


class NetworkError(GenesisCliException):
    """Error de conectividad o red"""
    
    def __init__(self, message: str, service: Optional[str] = None):
        super().__init__(message)
        self.service = service
        
    def get_formatted_message(self) -> str:
        if self.service:
            return f"❌ Error de red con '{self.service}': {self.message}"
        else:
            return f"❌ Error de red: {self.message}"


class GenesisCoreCommunicationError(GenesisCliException):
    """
    Error de comunicación con Genesis Core
    
    DOCTRINA: Solo usamos genesis-core como interfaz
    """
    
    def __init__(self, message: str, operation: str = "communication"):
        super().__init__(message)
        self.operation = operation
        
    def get_formatted_message(self) -> str:
        return f"❌ Error comunicando con Genesis Core ({self.operation}): {self.message}"


class CommandError(GenesisCliException):
    """Error específico de comandos CLI"""
    
    def __init__(self, message: str, command: str, suggestion: Optional[str] = None):
        super().__init__(message)
        self.command = command
        self.suggestion = suggestion
        
    def get_formatted_message(self) -> str:
        msg = f"❌ Error en comando '{self.command}': {self.message}"
        if self.suggestion:
            msg += f"\n  💡 Sugerencia: {self.suggestion}"
        return msg


class ProjectNotFoundError(GenesisCliException):
    """Error cuando no se encuentra un proyecto Genesis"""
    
    def __init__(self, path: str = "."):
        super().__init__(f"No se encontró un proyecto Genesis en '{path}'")
        self.path = path
        
    def get_formatted_message(self) -> str:
        return (f"❌ No se encontró un proyecto Genesis en '{self.path}'\n"
                f"  💡 Ejecuta 'genesis init <nombre>' para crear un proyecto")


class IncompatibleVersionError(GenesisCliException):
    """Error de versión incompatible"""
    
    def __init__(self, component: str, current: str, required: str):
        super().__init__(f"Versión incompatible de {component}")
        self.component = component
        self.current = current
        self.required = required
        
    def get_formatted_message(self) -> str:
        return (f"❌ Versión incompatible de {self.component}:\n"
                f"  • Actual: {self.current}\n"
                f"  • Requerida: {self.required}")


# Funciones de conveniencia para lanzar excepciones comunes
def raise_validation_error(message: str, field: Optional[str] = None, errors: Optional[List[str]] = None):
    """Lanzar error de validación"""
    raise ValidationError(message, field, errors)

def raise_project_name_error(name: str, reason: str):
    """Lanzar error de nombre de proyecto"""
    raise ProjectNameError(name, reason)

def raise_template_error(template: str, available_templates: Optional[List[str]] = None):
    """Lanzar error de template"""
    raise TemplateError(template, available_templates)

def raise_directory_error(message: str, path: str, operation: str = "access"):
    """Lanzar error de directorio"""
    raise DirectoryError(message, path, operation)

def raise_dependency_error(message: str, missing_deps: Optional[List[str]] = None):
    """Lanzar error de dependencias"""
    raise DependencyError(message, missing_deps)

def raise_configuration_error(message: str, config_key: Optional[str] = None):
    """Lanzar error de configuración"""
    raise ConfigurationError(message, config_key)

def raise_user_interrupt_error(operation: str = "operación"):
    """Lanzar error de interrupción del usuario"""
    raise UserInterruptError(operation)

def raise_network_error(message: str, service: Optional[str] = None):
    """Lanzar error de red"""
    raise NetworkError(message, service)

def raise_genesis_core_error(message: str, operation: str = "communication"):
    """Lanzar error de comunicación con Genesis Core"""
    raise GenesisCoreCommunicationError(message, operation)

def raise_command_error(message: str, command: str, suggestion: Optional[str] = None):
    """Lanzar error de comando"""
    raise CommandError(message, command, suggestion)

def raise_project_not_found_error(path: str = "."):
    """Lanzar error de proyecto no encontrado"""
    raise ProjectNotFoundError(path)

def raise_incompatible_version_error(component: str, current: str, required: str):
    """Lanzar error de versión incompatible"""
    raise IncompatibleVersionError(component, current, required)


# Función utilitaria para manejar excepciones de manera elegante
def handle_cli_exception(exception: Exception, console=None) -> int:
    """
    Manejar excepciones de CLI de manera elegante
    
    DOCTRINA: Mostramos errores de manera elegante
    
    Returns:
        int: Código de salida apropiado
    """
    if console is None:
        from rich.console import Console
        console = Console()
    
    if isinstance(exception, GenesisCliException):
        # Mostrar mensaje formateado de manera elegante
        console.print(exception.get_formatted_message())
        return 1
    elif isinstance(exception, KeyboardInterrupt):
        console.print("\n[yellow]⚠️ Operación cancelada por el usuario[/yellow]")
        return 1
    elif isinstance(exception, FileNotFoundError):
        console.print(f"[red]❌ Archivo no encontrado: {exception.filename}[/red]")
        return 1
    elif isinstance(exception, PermissionError):
        console.print(f"[red]❌ Sin permisos para acceder: {exception.filename}[/red]")
        return 1
    else:
        # Error inesperado
        console.print(f"[red]❌ Error inesperado: {str(exception)}[/red]")
        return 1