"""
Validadores para Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- SÍ valida entrada del usuario
- SÍ proporciona validación elegante
- Enfocado en UX/UI para validación
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass

from genesis_cli.exceptions import (
    ValidationError,
    ProjectNameError,
    TemplateError,
    DirectoryError,
    raise_validation_error
)

@dataclass
class ValidationResult:
    """
    Resultado de validación
    
    DOCTRINA: Validamos entrada del usuario
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    
    def __post_init__(self):
        """Post-inicialización"""
        if not self.errors:
            self.errors = []
        if not self.warnings:
            self.warnings = []
        if not self.suggestions:
            self.suggestions = []
    
    @classmethod
    def success(cls, warnings: List[str] = None, suggestions: List[str] = None) -> 'ValidationResult':
        """Crear resultado exitoso"""
        return cls(
            is_valid=True,
            errors=[],
            warnings=warnings or [],
            suggestions=suggestions or []
        )
    
    @classmethod
    def failure(cls, errors: List[str], warnings: List[str] = None, suggestions: List[str] = None) -> 'ValidationResult':
        """Crear resultado fallido"""
        return cls(
            is_valid=False,
            errors=errors,
            warnings=warnings or [],
            suggestions=suggestions or []
        )
    
    def add_error(self, error: str):
        """Agregar error"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Agregar advertencia"""
        self.warnings.append(warning)
    
    def add_suggestion(self, suggestion: str):
        """Agregar sugerencia"""
        self.suggestions.append(suggestion)

class ProjectNameValidator:
    """
    Validador para nombres de proyecto
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    # Nombres reservados del sistema
    RESERVED_NAMES = {
        # Nombres de Windows
        'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5',
        'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4',
        'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9',
        # Nombres comunes problemáticos
        'test', 'example', 'sample', 'demo', 'tmp', 'temp', 'cache',
        'src', 'lib', 'bin', 'dist', 'build', 'node_modules', '.git',
        # Palabras clave de Python
        'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
        'elif', 'else', 'except', 'false', 'finally', 'for', 'from', 'global',
        'if', 'import', 'in', 'is', 'lambda', 'none', 'not', 'or', 'pass',
        'raise', 'return', 'true', 'try', 'while', 'with', 'yield'
    }
    
    # Patrones problemáticos
    PROBLEMATIC_PATTERNS = [
        r'^\d+$',  # Solo números
        r'^[_-]+$',  # Solo guiones y underscores
        r'^\.+$',  # Solo puntos
        r'.*\s+.*',  # Espacios
        r'.*[<>:"/\\|?*].*',  # Caracteres especiales problemáticos
    ]
    
    @classmethod
    def validate(cls, name: str) -> ValidationResult:
        """
        Validar nombre de proyecto
        
        DOCTRINA: Validamos entrada del usuario
        """
        result = ValidationResult.success()
        
        # Validación básica
        if not name:
            result.add_error("El nombre del proyecto es requerido")
            return result
        
        if not isinstance(name, str):
            result.add_error("El nombre del proyecto debe ser una cadena de texto")
            return result
        
        # Validar longitud
        if len(name) < 2:
            result.add_error("El nombre debe tener al menos 2 caracteres")
            result.add_suggestion("Ejemplo: 'my-app', 'proyecto-web'")
        
        if len(name) > 50:
            result.add_error("El nombre no puede tener más de 50 caracteres")
            result.add_suggestion("Usa un nombre más corto y descriptivo")
        
        # Validar formato
        if not re.match(r'^[a-zA-Z]', name):
            result.add_error("El nombre debe comenzar con una letra")
            result.add_suggestion("Ejemplo: 'mi-proyecto', 'app-web'")
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
            result.add_error("El nombre solo puede contener letras, números, guiones (-) y guiones bajos (_)")
            result.add_suggestion("Caracteres permitidos: a-z, A-Z, 0-9, -, _")
        
        # Validar patrones problemáticos
        for pattern in cls.PROBLEMATIC_PATTERNS:
            if re.match(pattern, name):
                result.add_error(f"El nombre '{name}' contiene un patrón problemático")
                break
        
        # Validar nombres reservados
        if name.lower() in cls.RESERVED_NAMES:
            result.add_error(f"'{name}' es un nombre reservado del sistema")
            result.add_suggestion("Usa un nombre diferente como 'mi-proyecto' o 'app-principal'")
        
        # Validar convenciones
        if name.endswith('-'):
            result.add_warning("El nombre termina con guión, esto puede causar problemas")
            result.add_suggestion("Remueve el guión final")
        
        if name.startswith('_'):
            result.add_warning("El nombre comienza con guión bajo, esto puede causar problemas")
            result.add_suggestion("Comienza con una letra en su lugar")
        
        if '--' in name:
            result.add_warning("El nombre contiene guiones dobles")
            result.add_suggestion("Usa guiones simples: 'mi-proyecto'")
        
        if '__' in name:
            result.add_warning("El nombre contiene guiones bajos dobles")
            result.add_suggestion("Usa guiones bajos simples: 'mi_proyecto'")
        
        # Sugerencias adicionales
        if name.isupper():
            result.add_suggestion("Considera usar minúsculas para mejor legibilidad")
        
        if len(name) > 30:
            result.add_suggestion("Nombres más cortos son más fáciles de recordar")
        
        return result

class TemplateValidator:
    """
    Validador para templates
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    # Templates oficiales disponibles
    OFFICIAL_TEMPLATES = {
        'saas-basic': {
            'name': 'SaaS Básico',
            'description': 'Aplicación SaaS completa con autenticación y facturación',
            'features': ['authentication', 'database', 'api', 'frontend', 'docker', 'cicd'],
            'complexity': 'Media'
        },
        'api-only': {
            'name': 'Solo API',
            'description': 'API REST sin frontend',
            'features': ['database', 'api', 'docker', 'cicd'],
            'complexity': 'Baja'
        },
        'frontend-only': {
            'name': 'Solo Frontend',
            'description': 'Aplicación frontend sin backend',
            'features': ['frontend', 'docker', 'cicd'],
            'complexity': 'Baja'
        },
        'microservices': {
            'name': 'Microservicios',
            'description': 'Arquitectura de microservicios',
            'features': ['api', 'database', 'docker', 'cicd', 'monitoring'],
            'complexity': 'Alta'
        },
        'e-commerce': {
            'name': 'E-commerce',
            'description': 'Tienda online completa',
            'features': ['authentication', 'database', 'api', 'frontend', 'payments', 'docker'],
            'complexity': 'Alta'
        },
        'blog': {
            'name': 'Blog',
            'description': 'Sistema de blog con CMS',
            'features': ['authentication', 'database', 'api', 'frontend', 'docker'],
            'complexity': 'Media'
        },
        'ai-ready': {
            'name': 'AI Ready',
            'description': 'Aplicación preparada para IA',
            'features': ['authentication', 'database', 'api', 'frontend', 'ai', 'docker'],
            'complexity': 'Alta'
        },
        'minimal': {
            'name': 'Minimal',
            'description': 'Proyecto mínimo básico',
            'features': ['api', 'docker'],
            'complexity': 'Baja'
        }
    }
    
    @classmethod
    def validate(cls, template: str) -> ValidationResult:
        """
        Validar template
        
        DOCTRINA: Validamos entrada del usuario
        """
        result = ValidationResult.success()
        
        # Validación básica
        if not template:
            result.add_error("El template es requerido")
            result.add_suggestion("Usa 'saas-basic' para comenzar")
            return result
        
        if not isinstance(template, str):
            result.add_error("El template debe ser una cadena de texto")
            return result
        
        # Validar que existe
        if template not in cls.OFFICIAL_TEMPLATES:
            result.add_error(f"Template '{template}' no encontrado")
            result.add_suggestion(f"Templates disponibles: {', '.join(cls.OFFICIAL_TEMPLATES.keys())}")
            
            # Sugerir template similar
            similar = cls._find_similar_template(template)
            if similar:
                result.add_suggestion(f"¿Quisiste decir '{similar}'?")
        
        return result
    
    @classmethod
    def _find_similar_template(cls, template: str) -> Optional[str]:
        """Encontrar template similar"""
        template_lower = template.lower()
        
        # Buscar coincidencias parciales
        for official_template in cls.OFFICIAL_TEMPLATES:
            if template_lower in official_template or official_template in template_lower:
                return official_template
        
        # Buscar por características
        if 'api' in template_lower:
            return 'api-only'
        elif 'frontend' in template_lower or 'ui' in template_lower:
            return 'frontend-only'
        elif 'saas' in template_lower:
            return 'saas-basic'
        elif 'shop' in template_lower or 'store' in template_lower:
            return 'e-commerce'
        elif 'blog' in template_lower:
            return 'blog'
        elif 'ai' in template_lower:
            return 'ai-ready'
        elif 'simple' in template_lower or 'basic' in template_lower:
            return 'minimal'
        
        return None
    
    @classmethod
    def get_template_info(cls, template: str) -> Optional[Dict[str, Any]]:
        """Obtener información del template"""
        return cls.OFFICIAL_TEMPLATES.get(template)
    
    @classmethod
    def list_templates(cls) -> List[Dict[str, Any]]:
        """Listar todos los templates"""
        return [
            {**info, 'id': template_id}
            for template_id, info in cls.OFFICIAL_TEMPLATES.items()
        ]

class DirectoryValidator:
    """
    Validador para directorios
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    @classmethod
    def validate_output_directory(cls, path: str, project_name: str, force: bool = False) -> ValidationResult:
        """
        Validar directorio de salida
        
        DOCTRINA: Validamos entrada del usuario
        """
        result = ValidationResult.success()
        
        try:
            path_obj = Path(path)
            project_path = path_obj / project_name
            
            # Validar que el directorio padre existe
            if not path_obj.exists():
                result.add_error(f"El directorio padre no existe: {path}")
                result.add_suggestion("Crea el directorio o usa un directorio existente")
                return result
            
            # Validar que es un directorio
            if not path_obj.is_dir():
                result.add_error(f"'{path}' no es un directorio")
                return result
            
            # Validar permisos de escritura
            if not os.access(path_obj, os.W_OK):
                result.add_error(f"Sin permisos de escritura en: {path}")
                result.add_suggestion("Cambia los permisos o usa un directorio diferente")
                return result
            
            # Validar proyecto existente
            if project_path.exists():
                if not force:
                    if any(project_path.iterdir()):
                        result.add_error(f"El directorio '{project_name}' ya existe y no está vacío")
                        result.add_suggestion("Usa --force para sobrescribir o elige otro nombre")
                    else:
                        result.add_warning(f"El directorio '{project_name}' existe pero está vacío")
                else:
                    result.add_warning(f"El directorio '{project_name}' será sobrescrito")
            
            # Validar espacio disponible
            try:
                import shutil
                free_space = shutil.disk_usage(path_obj).free
                if free_space < 100 * 1024 * 1024:  # 100MB
                    result.add_warning("Poco espacio disponible en disco")
                    result.add_suggestion("Asegúrate de tener suficiente espacio para el proyecto")
            except Exception:
                pass
            
        except Exception as e:
            result.add_error(f"Error validando directorio: {str(e)}")
        
        return result

class FeatureValidator:
    """
    Validador para características de proyecto
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    # Características válidas
    VALID_FEATURES = {
        'authentication': {
            'name': 'Autenticación',
            'description': 'Sistema de autenticación y autorización',
            'dependencies': ['database']
        },
        'database': {
            'name': 'Base de datos',
            'description': 'Configuración de base de datos',
            'dependencies': []
        },
        'api': {
            'name': 'API REST',
            'description': 'API REST completa',
            'dependencies': []
        },
        'frontend': {
            'name': 'Frontend',
            'description': 'Interfaz de usuario moderna',
            'dependencies': []
        },
        'docker': {
            'name': 'Docker',
            'description': 'Containerización con Docker',
            'dependencies': []
        },
        'cicd': {
            'name': 'CI/CD',
            'description': 'Pipeline de integración continua',
            'dependencies': ['docker']
        },
        'monitoring': {
            'name': 'Monitoreo',
            'description': 'Sistema de monitoreo y métricas',
            'dependencies': ['docker']
        },
        'ai': {
            'name': 'IA',
            'description': 'Integración con IA y LLMs',
            'dependencies': ['api', 'database']
        },
        'testing': {
            'name': 'Testing',
            'description': 'Tests automatizados',
            'dependencies': []
        },
        'documentation': {
            'name': 'Documentación',
            'description': 'Documentación automática',
            'dependencies': []
        },
        'analytics': {
            'name': 'Analytics',
            'description': 'Sistema de analytics',
            'dependencies': ['database']
        },
        'caching': {
            'name': 'Caching',
            'description': 'Sistema de caché',
            'dependencies': []
        },
        'search': {
            'name': 'Búsqueda',
            'description': 'Sistema de búsqueda',
            'dependencies': ['database']
        },
        'notifications': {
            'name': 'Notificaciones',
            'description': 'Sistema de notificaciones',
            'dependencies': ['database']
        },
        'payments': {
            'name': 'Pagos',
            'description': 'Sistema de pagos',
            'dependencies': ['database', 'authentication']
        }
    }
    
    @classmethod
    def validate(cls, features: List[str]) -> ValidationResult:
        """
        Validar características
        
        DOCTRINA: Validamos entrada del usuario
        """
        result = ValidationResult.success()
        
        if not isinstance(features, list):
            result.add_error("Las características deben ser una lista")
            return result
        
        # Validar cada característica
        invalid_features = []
        for feature in features:
            if feature not in cls.VALID_FEATURES:
                invalid_features.append(feature)
        
        if invalid_features:
            result.add_error(f"Características inválidas: {', '.join(invalid_features)}")
            result.add_suggestion(f"Características válidas: {', '.join(cls.VALID_FEATURES.keys())}")
        
        # Validar dependencias
        resolved_features = cls._resolve_dependencies(features)
        missing_deps = set(resolved_features) - set(features)
        
        if missing_deps:
            result.add_warning(f"Dependencias automáticas agregadas: {', '.join(missing_deps)}")
        
        # Validar combinaciones
        if 'ai' in features and 'database' not in resolved_features:
            result.add_error("La característica 'ai' requiere 'database'")
        
        if 'payments' in features and 'authentication' not in resolved_features:
            result.add_error("La característica 'payments' requiere 'authentication'")
        
        return result
    
    @classmethod
    def _resolve_dependencies(cls, features: List[str]) -> List[str]:
        """Resolver dependencias de características"""
        resolved = set(features)
        
        for feature in features:
            if feature in cls.VALID_FEATURES:
                deps = cls.VALID_FEATURES[feature]['dependencies']
                resolved.update(deps)
        
        return list(resolved)
    
    @classmethod
    def get_feature_info(cls, feature: str) -> Optional[Dict[str, Any]]:
        """Obtener información de una característica"""
        return cls.VALID_FEATURES.get(feature)
    
    @classmethod
    def list_features(cls) -> List[Dict[str, Any]]:
        """Listar todas las características"""
        return [
            {**info, 'id': feature_id}
            for feature_id, info in cls.VALID_FEATURES.items()
        ]

# Funciones de conveniencia
def validate_project_name(name: str) -> ValidationResult:
    """Validar nombre de proyecto"""
    return ProjectNameValidator.validate(name)

def validate_template(template: str) -> ValidationResult:
    """Validar template"""
    return TemplateValidator.validate(template)

def validate_directory(path: str, project_name: str, force: bool = False) -> ValidationResult:
    """Validar directorio"""
    return DirectoryValidator.validate_output_directory(path, project_name, force)

def validate_features(features: List[str]) -> ValidationResult:
    """Validar características"""
    return FeatureValidator.validate(features)

def validate_project_config(config: Dict[str, Any]) -> ValidationResult:
    """
    Validar configuración completa del proyecto
    
    DOCTRINA: Validamos entrada del usuario
    """
    result = ValidationResult.success()
    
    # Validar nombre
    if 'name' in config:
        name_result = validate_project_name(config['name'])
        if not name_result.is_valid:
            result.errors.extend(name_result.errors)
            result.is_valid = False
        result.warnings.extend(name_result.warnings)
        result.suggestions.extend(name_result.suggestions)
    
    # Validar template
    if 'template' in config:
        template_result = validate_template(config['template'])
        if not template_result.is_valid:
            result.errors.extend(template_result.errors)
            result.is_valid = False
        result.warnings.extend(template_result.warnings)
        result.suggestions.extend(template_result.suggestions)
    
    # Validar características
    if 'features' in config:
        features_result = validate_features(config['features'])
        if not features_result.is_valid:
            result.errors.extend(features_result.errors)
            result.is_valid = False
        result.warnings.extend(features_result.warnings)
        result.suggestions.extend(features_result.suggestions)
    
    # Validar directorio
    if 'name' in config and 'output_path' in config:
        dir_result = validate_directory(
            config['output_path'], 
            config['name'], 
            config.get('force', False)
        )
        if not dir_result.is_valid:
            result.errors.extend(dir_result.errors)
            result.is_valid = False
        result.warnings.extend(dir_result.warnings)
        result.suggestions.extend(dir_result.suggestions)
    
    return result