# Guía de Contribución para Genesis CLI

¡Gracias por tu interés en contribuir a Genesis CLI! Este documento te guiará a través del proceso de contribución al proyecto.

## 🧠 Doctrina del Ecosistema

Genesis CLI sigue estrictamente la **Doctrina del Ecosistema Genesis**. Todas las contribuciones deben respetar estos principios:

### ❌ Lo que NO hace Genesis CLI
- **NO implementa lógica de generación de código**
- **NO coordina agentes directamente**
- **NO contiene templates ni agentes**
- **NO interactúa con MCPturbo directamente**

### ✅ Lo que SÍ hace Genesis CLI
- **SÍ es la única interfaz de usuario del ecosistema**
- **SÍ valida entrada del usuario de manera exhaustiva**
- **SÍ muestra progreso y estado de manera elegante**
- **SÍ usa genesis-core como única interfaz**
- **SÍ proporciona UX/UI excepcional**

## 🚀 Configuración del Entorno de Desarrollo

### Prerrequisitos

```bash
# Dependencias del sistema
python >= 3.8
git >= 2.0
node >= 18.0  # Para documentación
```

### Configuración Inicial

```bash
# 1. Fork y clonar el repositorio
git clone https://github.com/tu-usuario/genesis-cli.git
cd genesis-cli

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias de desarrollo
pip install -e ".[dev]"

# 4. Configurar pre-commit hooks
pre-commit install

# 5. Verificar instalación
python scripts/dev.py check-all
```

### Script de Desarrollo

Usa el script de desarrollo para tareas comunes:

```bash
# Configurar entorno
python scripts/dev.py setup

# Ejecutar tests
python scripts/dev.py test

# Formatear código
python scripts/dev.py format

# Linting
python scripts/dev.py lint

# Verificaciones de seguridad
python scripts/dev.py security

# Todas las verificaciones
python scripts/dev.py check-all

# Limpiar archivos temporales
python scripts/dev.py clean
```

## 📋 Tipos de Contribución

### 1. Mejoras de UX/UI
- Mejoras en mensajes de error
- Optimización de validación de entrada
- Mejoras en presentación visual
- Nuevas funcionalidades de CLI

### 2. Corrección de Bugs
- Bugs en validación
- Problemas de interfaz
- Errores en configuración
- Issues de compatibilidad

### 3. Documentación
- Mejoras en README
- Ejemplos de uso
- Documentación de API
- Guías de usuario

### 4. Tests
- Tests unitarios
- Tests de integración
- Tests de UI
- Mejoras en cobertura

### 5. Herramientas de Desarrollo
- Mejoras en scripts de desarrollo
- Configuración de CI/CD
- Herramientas de debugging
- Automatización

## 🔄 Proceso de Contribución

### 1. Planificación

1. **Revisar issues existentes** en GitHub
2. **Crear issue** si no existe uno relacionado
3. **Discutir propuesta** con maintainers
4. **Asignar issue** a ti mismo

### 2. Desarrollo

1. **Crear branch** desde `main`:
   ```bash
   git checkout -b feature/nombre-descriptivo
   ```

2. **Desarrollar cambios** siguiendo las guías de estilo

3. **Escribir tests** para nuevas funcionalidades

4. **Actualizar documentación** si es necesario

5. **Ejecutar verificaciones**:
   ```bash
   python scripts/dev.py check-all
   ```

### 3. Commit y Push

1. **Commits atómicos** con mensajes descriptivos:
   ```bash
   git commit -m "feat: add validation for project templates"
   ```

2. **Push a tu fork**:
   ```bash
   git push origin feature/nombre-descriptivo
   ```

### 4. Pull Request

1. **Crear PR** desde tu branch hacia `main`
2. **Llenar template** de PR completamente
3. **Linkear issue** relacionado
4. **Asignar reviewers** apropiados
5. **Responder a feedback** de manera constructiva

## 📏 Estándares de Código

### Formateo

```bash
# Black para formateo
black .

# isort para imports
isort .

# Verificar formateo
python scripts/dev.py format
```

### Linting

```bash
# flake8 para linting
flake8 .

# mypy para type checking
mypy genesis_cli/

# Verificar linting
python scripts/dev.py lint
```

### Convenciones de Código

#### Nombres de Variables
- `snake_case` para variables y funciones
- `PascalCase` para clases
- `UPPER_CASE` para constantes

#### Documentación
- Docstrings estilo Google
- Comentarios para lógica compleja
- Type hints obligatorios

#### Estructura de Archivos
```python
"""
Descripción del módulo

DOCTRINA DEL ECOSISTEMA:
- Declaración de qué hace y no hace el módulo
"""

import standard_library
import third_party
from genesis_cli import local_imports

# Constantes
CONSTANT_VALUE = "value"

# Código del módulo
```

## 🧪 Tests

### Estructura de Tests

```
tests/
├── conftest.py              # Configuración pytest
├── test_cli.py              # Tests de CLI principal
├── test_validators.py       # Tests de validación
├── test_config.py          # Tests de configuración
├── test_utils.py           # Tests de utilidades
└── test_exceptions.py      # Tests de excepciones
```

### Escribir Tests

```python
"""
Tests para [módulo]

DOCTRINA DEL ECOSISTEMA:
- NO testea lógica de generación
- SÍ testea validación de entrada del usuario
- SÍ testea interfaz de usuario
"""

import pytest
from genesis_cli.module import function_to_test

class TestFunctionality:
    """Tests para funcionalidad específica"""
    
    def test_valid_input(self):
        """Test con entrada válida"""
        result = function_to_test("valid_input")
        assert result.is_valid
    
    def test_invalid_input(self):
        """Test con entrada inválida"""
        result = function_to_test("invalid_input")
        assert not result.is_valid
        assert "error message" in str(result.errors)
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_validators.py

# Con coverage
pytest --cov=genesis_cli --cov-report=html

# Tests por categoría
pytest -m "unit"
pytest -m "integration"
pytest -m "cli"
```

## 📝 Documentación

### Estructura de Documentación

```
docs/
├── index.md                 # Página principal
├── getting-started/         # Guía de inicio
├── user-guide/             # Guía de usuario
├── examples/               # Ejemplos
├── api-reference/          # Referencia de API
└── development/            # Documentación de desarrollo
```

### Escribir Documentación

- **Markdown** para contenido
- **MkDocs** para generación
- **Ejemplos prácticos** siempre
- **Screenshots** cuando sea útil

### Servir Documentación

```bash
# Servir localmente
mkdocs serve

# Construir documentación
mkdocs build

# Usando script de desarrollo
python scripts/dev.py serve-docs
```

## 🔍 Revisión de Código

### Checklist para Reviewers

#### Funcionalidad
- [ ] ¿El código hace lo que promete?
- [ ] ¿Sigue la doctrina del ecosistema?
- [ ] ¿Maneja casos edge correctamente?
- [ ] ¿Tiene validación de entrada adecuada?

#### Calidad
- [ ] ¿Está bien documentado?
- [ ] ¿Tiene tests apropiados?
- [ ] ¿Sigue las convenciones de código?
- [ ] ¿No introduce vulnerabilidades?

#### UX/UI
- [ ] ¿Proporciona mensajes de error claros?
- [ ] ¿Tiene interfaz elegante?
- [ ] ¿Valida entrada del usuario?
- [ ] ¿Muestra progreso apropiado?

### Checklist para Contribuidores

#### Antes de Enviar PR
- [ ] Código formateado con black/isort
- [ ] Linting pasado (flake8, mypy)
- [ ] Tests escritos y pasando
- [ ] Documentación actualizada
- [ ] Verificaciones de seguridad pasadas

#### En el PR
- [ ] Descripción clara del cambio
- [ ] Issue relacionado linkeado
- [ ] Screenshots si es cambio visual
- [ ] Notas de breaking changes
- [ ] Instrucciones de testing

## 🚨 Reportar Bugs

### Template de Bug Report

```markdown
**Descripción del Bug**
Descripción clara del problema.

**Pasos para Reproducir**
1. Ejecutar `genesis init project`
2. Usar template 'saas-basic'
3. Ver error

**Comportamiento Esperado**
Debería crear proyecto sin errores.

**Comportamiento Actual**
Error: [mensaje de error]

**Entorno**
- OS: [ej. Ubuntu 20.04]
- Python: [ej. 3.11.0]
- Genesis CLI: [ej. 1.0.0]

**Información Adicional**
Output de `genesis doctor`:
```
[output aquí]
```

### Información de Debug

```bash
# Información del entorno
genesis doctor

# Logs detallados
genesis init project --verbose

# Información del sistema
python -c "import sys; print(sys.version)"
pip show genesis-cli
```

## 💡 Solicitar Features

### Template de Feature Request

```markdown
**Funcionalidad Solicitada**
Descripción clara de la funcionalidad deseada.

**Problema que Resuelve**
¿Qué problema específico resuelve?

**Solución Propuesta**
Descripción de cómo debería funcionar.

**Alternativas Consideradas**
Otras soluciones que consideraste.

**Impacto en UX**
¿Cómo mejora la experiencia de usuario?

**Ejemplo de Uso**
```bash
genesis new-command --option value
```

**Compatibilidad**
¿Rompe compatibilidad existente?
```

## 🏆 Reconocimientos

### Contribuidores Destacados
- Contribuidores listados en README
- Reconocimiento en releases
- Invitación a team de maintainers

### Tipos de Contribución Reconocidas
- Código y bug fixes
- Documentación
- Reportes de bugs
- Sugerencias de features
- Revisión de código
- Promoción del proyecto

## 📞 Comunicación

### Canales de Comunicación
- **GitHub Issues**: Para bugs y features
- **GitHub Discussions**: Para preguntas generales
- **Discord**: Para chat en tiempo real
- **Email**: Para asuntos privados

### Código de Conducta
- Sé respetuoso y constructivo
- Mantén discusiones técnicas
- Ayuda a otros contribuidores
- Sigue las guías de la comunidad

## 🔄 Proceso de Release

### Versionado
- Seguimos [Semantic Versioning](https://semver.org/)
- `MAJOR.MINOR.PATCH` (ej. 1.2.3)
- Breaking changes incrementan MAJOR
- Features incrementan MINOR
- Bug fixes incrementan PATCH

### Changelog
- Mantener `CHANGELOG.md` actualizado
- Usar formato [Keep a Changelog](https://keepachangelog.com/)
- Categorizar cambios apropiadamente

## 🎯 Prioridades Actuales

### Alta Prioridad
1. Mejoras en validación de entrada
2. Mejor manejo de errores
3. Optimización de performance
4. Mejoras en documentación

### Media Prioridad
1. Nuevas funcionalidades de CLI
2. Mejoras en testing
3. Herramientas de desarrollo
4. Integración con ecosistema

### Baja Prioridad
1. Refactoring interno
2. Optimizaciones menores
3. Mejoras cosméticas
4. Documentación avanzada

## 📚 Recursos Adicionales

### Documentación
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Pytest Documentation](https://docs.pytest.org/)

### Herramientas
- [Black](https://black.readthedocs.io/)
- [isort](https://pycqa.github.io/isort/)
- [flake8](https://flake8.pycqa.org/)
- [mypy](https://mypy.readthedocs.io/)

### Ecosistema Genesis
- [Genesis Core](https://github.com/genesis-engine/genesis-core)
- [Genesis Templates](https://github.com/genesis-engine/genesis-templates)
- [Genesis Documentation](https://docs.genesis-engine.dev/)

---

¡Gracias por contribuir a Genesis CLI! Tu participación ayuda a hacer el desarrollo de software más accesible y eficiente para todos. 🚀