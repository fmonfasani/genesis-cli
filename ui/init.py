"""
Genesis CLI UI Module

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- SÍ proporciona UI elegante y funcional
- SÍ maneja progreso y estado visual
- Enfocado en UX/UI excelente
"""

from .console import genesis_console, GenesisUI, ui

__all__ = [
    "genesis_console",
    "GenesisUI", 
    "ui"
]