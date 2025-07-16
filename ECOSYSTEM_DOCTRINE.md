<!-- ECOSYSTEM_DOCTRINE: genesis-cli -->
# ⚡ Ecosystem Doctrine — Genesis-CLI (Interfaz de Línea de Comandos)

Este repositorio forma parte del ecosistema **Genesis Engine**.  
Su rol es el de **interfaz de usuario y punto de entrada del ecosistema**.

## 🧠 Rol Declarado

- Tipo: **Interfaz de Usuario**
- Nombre: `genesis-cli`
- Dominio: Experiencia de usuario
- Función: Proveer interfaz CLI elegante y funcional

## 🔒 Mandamientos del Proyecto

### 1. **No implementarás lógica de generación**
NO contiene lógica de creación de código.  
Solo coordina llamadas a genesis-core.

### 2. **No coordinarás agentes directamente**
NO llamas a MCPturbo directamente.  
Solo usas genesis-core como interfaz.

### 3. **No contendrás templates ni agentes**
Templates están en genesis-templates.  
Agentes están en repos especializados.

### 4. **Serás la única interfaz de usuario**
Única forma de interactuar con el ecosistema.  
Responsable de UX/UI elegante.

### 5. **Validarás entrada del usuario**
Validas argumentos y configuración antes de enviar a genesis-core.  
Proporcionas mensajes de error claros.

### 6. **Mostrarás progreso y estado**
Interfaz rica con progreso, logs y estado.  
Experiencia de usuario fluida y informativa.

### 7. **No conocerás MCPturbo directamente**
Todas las operaciones van a través de genesis-core.  
Solo conoces la interfaz pública de genesis-core.

---

## 🧩 Interfaz esperada por consumidores

Los usuarios finales usan:

- `genesis init <project-name> --template=<template>`
- `genesis generate <component> --type=<type>`
- `genesis deploy --target=<target>`
- `genesis doctor` (diagnóstico)

---

## 📦 Separación de capas (importante)

| Capa | Puede importar desde | No puede importar desde |
|------|----------------------|--------------------------|
| genesis-cli | genesis-core, typer, rich | mcpturbo, genesis-agents, genesis-templates |
| usuario | genesis-cli | genesis-core |

---

## 🤖 AI Agents, please read:

Este repositorio es la cara visible del ecosistema.

Si estás revisando código, escribiendo tests o generando lógica nueva:
- ❌ No implementes lógica de generación de código.
- ❌ No llames a MCPturbo directamente.
- ❌ No agregues templates o agentes.
- ✅ Enfócate en UX/UI excelente.
- ✅ Usa genesis-core como única interfaz.
- ✅ Valida entrada y proporciona feedback claro.

Toda excepción debe documentarse en `DOCTRINE_CHANGE_REQUEST.md`.

---

## 📎 Referencias

- Genesis Core → [https://github.com/fmonfasani/genesis-core](https://github.com/fmonfasani/genesis-core)
- Typer → [https://typer.tiangolo.com/](https://typer.tiangolo.com/)
- Rich → [https://rich.readthedocs.io/](https://rich.readthedocs.io/)