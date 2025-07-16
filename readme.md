# 🚀 Genesis CLI

**Interfaz de línea de comandos elegante para Genesis Engine**

Genesis CLI es la interfaz de usuario principal del ecosistema Genesis Engine. Proporciona comandos intuitivos y una experiencia de usuario excepcional para crear, gestionar y desplegar aplicaciones full-stack modernas usando agentes IA especializados.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Genesis Engine](https://img.shields.io/badge/Genesis-Engine-cyan.svg)](https://github.com/genesis-engine/genesis-core)

## 🎯 Doctrina del Ecosistema

Genesis CLI sigue estrictamente la **Doctrina del Ecosistema Genesis**:

- ❌ **NO implementa lógica de generación** - Solo coordina llamadas a genesis-core
- ❌ **NO coordina agentes directamente** - Solo usa genesis-core como interfaz
- ❌ **NO contiene templates ni agentes** - Están en repositorios especializados
- ✅ **SÍ es la única interfaz de usuario** - Punto de entrada principal del ecosistema
- ✅ **SÍ valida entrada del usuario** - Validación robusta y mensajes claros
- ✅ **SÍ muestra progreso y estado** - Interfaz rica y elegante
- ✅ **Solo usa genesis-core** - Nunca interactúa con MCPturbo directamente

## ✨ Características Principales

### 🎨 Interfaz Elegante
- **Rich UI**: Interfaz de línea de comandos con colores, tablas y progress bars
- **Mensajes Claros**: Errores, advertencias y sugerencias útiles
- **Validación Robusta**: Validación exhaustiva de entrada del usuario
- **Experiencia Fluida**: Comandos intuitivos y bien documentados

### 🔧 Comandos Disponibles
- `genesis init` - Crear nuevo proyecto
- `genesis deploy` - Desplegar aplicación
- `genesis generate` - Generar componentes
- `genesis status` - Ver estado del proyecto
- `genesis doctor` - Diagnosticar entorno

### 📋 Validaciones Inteligentes
- **Nombres de Proyecto**: Validación de nombres con sugerencias
- **Templates**: Verificación de templates disponibles
- **Directorios**: Validación de permisos y estructura
- **Características**: Validación de features y dependencias

## 🚀 Instalación

### Prerrequisitos

```bash
# Dependencias del sistema
python >= 3.8
node >= 18.0
git >= 2.0
docker >= 20.0  # Opcional pero recomendado
```

### Instalación desde PyPI

```bash
pip install genesis-cli
```

### Instalación desde Código Fuente

```bash
git clone https://github.com/genesis-engine/genesis-cli.git
cd genesis-cli
pip install -e .
```

### Verificación de Instalación

```bash
genesis --version
genesis doctor
```

## 🎯 Uso Básico

### Crear Nuevo Proyecto

```bash
# Proyecto básico SaaS
genesis init mi-proyecto

# Con template específico
genesis init mi-proyecto --template=api-only

# Modo no interactivo
genesis init mi-proyecto --template=saas-basic --no-interactive

# En directorio específico
genesis init mi-proyecto --output=/path/to/projects
```

### Desplegar Aplicación

```bash
# Despliegue local
genesis deploy --env=local

# Despliegue en staging
genesis deploy --env=staging

# Despliegue en producción (con confirmación)
genesis deploy --env=production
```

### Generar Componentes

```bash
# Generar modelo
genesis generate model User

# Generar endpoint
genesis generate endpoint /api/users

# Generar página
genesis generate page UserProfile

# Generar componente
genesis generate component UserCard
```

### Verificar Estado

```bash
# Estado del proyecto
genesis status

# Diagnóstico del entorno
genesis doctor
```

## 📁 Estructura del Proyecto

```
genesis-cli/
├── genesis_cli/
│   ├── __init__.py           # Inicialización del módulo
│   ├── main.py              # Entry point principal
│   ├── config.py            # Configuración CLI
│   ├── exceptions.py        # Excepciones específicas
│   ├── logging.py           # Sistema de logging
│   ├── utils.py             # Utilidades generales
│   ├── validators.py        # Validadores de entrada
│   ├── commands/            # Funciones de comandos
│   │   ├── __init__.py
│   │   └── utils.py
│   └── ui/                  # Interfaz de usuario
│       ├── __init__.py
│       └── console.py
├── tests/                   # Tests unitarios
├── docs/                    # Documentación
├── pyproject.toml          # Configuración del proyecto
└── README.md               # Este archivo
```

## 🔧 Configuración

### Configuración por Defecto

Genesis CLI crea automáticamente la configuración en `~/.genesis-cli/config.json`:

```json
{
  "ui": {
    "theme": "default",
    "show_banner": true,
    "color_output": true
  },
  "behavior": {
    "interactive_mode": true,
    "verbose_output": false
  },
  "templates": {
    "default_template": "saas-basic"
  },
  "project": {
    "create_git_repo": true,
    "init_commit": true
  }
}
```

### Variables de Entorno

```bash
# Configuración de comportamiento
export GENESIS_CLI_NO_BANNER=1          # Ocultar banner
export GENESIS_CLI_NO_INTERACTIVE=1     # Modo no interactivo
export GENESIS_CLI_VERBOSE=1            # Modo verbose
export GENESIS_CLI_DEBUG=1              # Modo debug
export GENESIS_CLI_SKIP_DEPS=1          # Omitir verificación de dependencias
export GENESIS_CLI_DEFAULT_TEMPLATE=api-only  # Template por defecto
```

## 🎨 Templates Disponibles

| Template | Descripción | Características | Complejidad |
|----------|-------------|----------------|-------------|
| `saas-basic` | Aplicación SaaS completa | Auth, DB, API, Frontend, Docker | Media |
| `api-only` | Solo API REST | DB, API, Docker | Baja |
| `frontend-only` | Solo Frontend | Frontend, Docker | Baja |
| `microservices` | Arquitectura microservicios | API, DB, Docker, Monitoring | Alta |
| `e-commerce` | Tienda online | Auth, DB, API, Frontend, Payments | Alta |
| `blog` | Sistema de blog | Auth, DB, API, Frontend | Media |
| `ai-ready` | Aplicación con IA | Auth, DB, API, Frontend, AI | Alta |
| `minimal` | Proyecto mínimo | API, Docker | Baja |

## 🔍 Validaciones

### Nombres de Proyecto

```bash
# ✅ Válidos
genesis init mi-proyecto
genesis init web-app-2024
genesis init user_dashboard

# ❌ Inválidos
genesis init 123-project      # No puede comenzar con número
genesis init my project       # No puede contener espacios
genesis init con              # Nombre reservado
```

### Templates

```bash
# ✅ Válidos
genesis init app --template=saas-basic
genesis init api --template=api-only

# ❌ Inválidos
genesis init app --template=invalid-template
# Error: Template 'invalid-template' no encontrado
# Templates disponibles: saas-basic, api-only, frontend-only...
```

### Directorios

```bash
# ✅ Válidos
genesis init project --output=./projects
genesis init app --output=/home/user/apps

# ❌ Inválidos
genesis init project --output=/root/restricted  # Sin permisos
genesis init project --output=/nonexistent/path # Directorio no existe
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=genesis_cli

# Tests específicos
pytest tests/test_validators.py
pytest tests/test_cli.py -v

# Tests por categoría
pytest -m "unit"          # Tests unitarios
pytest -m "integration"   # Tests de integración
pytest -m "cli"           # Tests de CLI
```

### Estructura de Tests

```
tests/
├── test_cli.py              # Tests de CLI principal
├── test_validators.py       # Tests de validadores
├── test_config.py          # Tests de configuración
├── test_utils.py           # Tests de utilidades
├── test_ui.py              # Tests de interfaz
└── conftest.py             # Configuración de pytest
```

## 🐛 Debugging

### Modo Debug

```bash
# Activar modo debug
export GENESIS_CLI_DEBUG=1
genesis init my-project

# O usar flag
genesis init my-project --verbose
```

### Logs

```bash
# Ver logs recientes
tail -f ~/.genesis-cli/logs/genesis-cli.log

# Limpiar logs
rm ~/.genesis-cli/logs/genesis-cli.log
```

## 📊 Métricas y Monitoring

Genesis CLI incluye métricas básicas para mejorar la experiencia:

- **Tiempo de Ejecución**: Métricas de rendimiento de comandos
- **Tasa de Éxito**: Porcentaje de comandos exitosos
- **Errores Comunes**: Tracking de errores frecuentes
- **Uso de Features**: Estadísticas de características utilizadas

## 🤝 Contribuir

### Configuración de Desarrollo

```bash
# Clonar repositorio
git clone https://github.com/genesis-engine/genesis-cli.git
cd genesis-cli

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Instalar pre-commit hooks
pre-commit install
```

### Ejecutar Linting

```bash
# Formatear código
black .
isort .

# Verificar código
flake8 .
mypy genesis_cli/

# Verificar seguridad
bandit -r genesis_cli/
```

### Guías de Contribución

1. **Seguir la Doctrina**: Todo código debe seguir la Doctrina del Ecosistema
2. **Tests**: Todos los cambios deben incluir tests
3. **Documentación**: Actualizar documentación cuando sea necesario
4. **Validación**: Enfocarse en mejorar la validación de entrada del usuario
5. **UX/UI**: Priorizar la experiencia de usuario elegante

## 🐛 Troubleshooting

### Problemas Comunes

**Error: `genesis command not found`**
```bash
# Verificar instalación
pip list | grep genesis-cli

# Reinstalar
pip uninstall genesis-cli
pip install genesis-cli
```

**Error: `No se puede conectar con Genesis Core`**
```bash
# Verificar instalación de genesis-core
pip list | grep genesis-core

# Instalar genesis-core
pip install genesis-core
```

**Error: `Dependencias faltantes`**
```bash
# Ejecutar diagnóstico
genesis doctor

# Instalar dependencias manualmente
# Seguir las instrucciones mostradas
```

### Reportar Bugs

1. Ejecutar `genesis doctor` y incluir output
2. Usar `genesis --verbose` para más detalles
3. Incluir logs de `~/.genesis-cli/logs/genesis-cli.log`
4. Reportar en [GitHub Issues](https://github.com/genesis-engine/genesis-cli/issues)

## 🔗 Enlaces Útiles

- **[Genesis Core](https://github.com/genesis-engine/genesis-core)** - Motor principal del ecosistema
- **[Genesis Templates](https://github.com/genesis-engine/genesis-templates)** - Colección de templates
- **[Documentación](https://docs.genesis-engine.dev/cli)** - Documentación completa
- **[Ejemplos](https://github.com/genesis-engine/examples)** - Proyectos de ejemplo

## 📄 Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).

## 🙏 Agradecimientos

Genesis CLI está construido sobre tecnologías excepcionales:

- **[Typer](https://typer.tiangolo.com/)** - Framework CLI moderno
- **[Rich](https://rich.readthedocs.io/)** - Rich text y beautiful formatting
- **[Click](https://click.palletsprojects.com/)** - Utilities para CLI
- **[Pytest](https://pytest.org/)** - Testing framework

---

<div align="center">

**[🏠 Genesis Engine](https://github.com/genesis-engine/genesis-core)** • 
**[📖 Documentación](https://docs.genesis-engine.dev)** • 
**[🚀 Ejemplos](https://github.com/genesis-engine/examples)**

Creado con ❤️ por el equipo de Genesis Engine

</div>