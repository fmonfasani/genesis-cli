#!/usr/bin/env python3
"""
Script de desarrollo para Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO implementa lógica de generación
- NO coordina agentes directamente
- SÍ proporciona herramientas de desarrollo para CLI
- SÍ mejora la experiencia de desarrollo
- Solo herramientas para interfaz de usuario
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> int:
    """Ejecutar comando y retornar código de salida"""
    print(f"🔧 Ejecutando: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def setup_development():
    """Configurar entorno de desarrollo"""
    print("🚀 Configurando entorno de desarrollo...")
    
    # Instalar dependencias de desarrollo
    if run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"]) != 0:
        print("❌ Error instalando dependencias de desarrollo")
        return False
    
    # Instalar pre-commit hooks
    if run_command(["pre-commit", "install"]) != 0:
        print("❌ Error instalando pre-commit hooks")
        return False
    
    print("✅ Entorno de desarrollo configurado")
    return True


def run_tests(coverage: bool = True, verbose: bool = False):
    """Ejecutar tests"""
    print("🧪 Ejecutando tests...")
    
    cmd = ["pytest"]
    
    if coverage:
        cmd.extend([
            "--cov=genesis_cli",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-fail-under=80"
        ])
    
    if verbose:
        cmd.append("-v")
    
    return run_command(cmd) == 0


def run_linting():
    """Ejecutar linting"""
    print("🔍 Ejecutando linting...")
    
    # Black
    if run_command(["black", "--check", "--diff", "."]) != 0:
        print("❌ Error en formateo con black")
        return False
    
    # isort
    if run_command(["isort", "--check-only", "--diff", "."]) != 0:
        print("❌ Error en ordenamiento de imports")
        return False
    
    # flake8
    if run_command(["flake8", "."]) != 0:
        print("❌ Error en linting con flake8")
        return False
    
    # mypy
    if run_command(["mypy", "genesis_cli/"]) != 0:
        print("❌ Error en type checking")
        return False
    
    print("✅ Linting pasado")
    return True


def format_code():
    """Formatear código"""
    print("✨ Formateando código...")
    
    # Black
    if run_command(["black", "."]) != 0:
        print("❌ Error formateando con black")
        return False
    
    # isort
    if run_command(["isort", "."]) != 0:
        print("❌ Error ordenando imports")
        return False
    
    print("✅ Código formateado")
    return True


def run_security_checks():
    """Ejecutar verificaciones de seguridad"""
    print("🔒 Ejecutando verificaciones de seguridad...")
    
    # bandit
    if run_command(["bandit", "-r", "genesis_cli/"]) != 0:
        print("❌ Error en verificación de seguridad")
        return False
    
    # safety
    if run_command(["safety", "check"]) != 0:
        print("❌ Error en verificación de dependencias")
        return False
    
    print("✅ Verificaciones de seguridad pasadas")
    return True


def build_package():
    """Construir paquete"""
    print("📦 Construyendo paquete...")
    
    # Limpiar build anterior
    import shutil
    for dir_name in ["build", "dist", "*.egg-info"]:
        for path in Path(".").glob(dir_name):
            if path.is_dir():
                shutil.rmtree(path)
    
    # Construir paquete
    if run_command([sys.executable, "-m", "build"]) != 0:
        print("❌ Error construyendo paquete")
        return False
    
    # Verificar paquete
    if run_command(["twine", "check", "dist/*"]) != 0:
        print("❌ Error verificando paquete")
        return False
    
    print("✅ Paquete construido")
    return True


def serve_docs():
    """Servir documentación"""
    print("📚 Sirviendo documentación...")
    
    return run_command(["mkdocs", "serve"]) == 0


def build_docs():
    """Construir documentación"""
    print("📚 Construyendo documentación...")
    
    return run_command(["mkdocs", "build"]) == 0


def run_all_checks():
    """Ejecutar todas las verificaciones"""
    print("🔄 Ejecutando todas las verificaciones...")
    
    checks = [
        ("Linting", run_linting),
        ("Tests", lambda: run_tests(coverage=True)),
        ("Seguridad", run_security_checks),
        ("Construcción", build_package),
    ]
    
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        if not check_func():
            print(f"❌ {name} falló")
            return False
    
    print("\n✅ Todas las verificaciones pasaron")
    return True


def clean():
    """Limpiar archivos temporales"""
    print("🧹 Limpiando archivos temporales...")
    
    import shutil
    
    patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        ".mypy_cache",
        ".tox",
        "build",
        "dist",
        "*.egg-info",
    ]
    
    for pattern in patterns:
        for path in Path(".").rglob(pattern):
            if path.is_file():
                path.unlink()
                print(f"  Eliminado: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"  Eliminado: {path}")
    
    print("✅ Limpieza completada")


def install_dev_dependencies():
    """Instalar dependencias de desarrollo"""
    print("📦 Instalando dependencias de desarrollo...")
    
    dependencies = [
        "black",
        "isort",
        "flake8",
        "mypy",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "bandit",
        "safety",
        "build",
        "twine",
        "mkdocs",
        "mkdocs-material",
        "pre-commit",
    ]
    
    cmd = [sys.executable, "-m", "pip", "install"] + dependencies
    
    if run_command(cmd) != 0:
        print("❌ Error instalando dependencias")
        return False
    
    print("✅ Dependencias instaladas")
    return True


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Script de desarrollo para Genesis CLI"
    )
    
    parser.add_argument(
        "command",
        choices=[
            "setup",
            "test",
            "lint",
            "format",
            "security",
            "build",
            "docs",
            "serve-docs",
            "check-all",
            "clean",
            "install-deps",
        ],
        help="Comando a ejecutar"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Salida verbose"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Ejecutar tests sin coverage"
    )
    
    args = parser.parse_args()
    
    # Cambiar al directorio del proyecto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Ejecutar comando
    success = True
    
    if args.command == "setup":
        success = setup_development()
    elif args.command == "test":
        success = run_tests(coverage=not args.no_coverage, verbose=args.verbose)
    elif args.command == "lint":
        success = run_linting()
    elif args.command == "format":
        success = format_code()
    elif args.command == "security":
        success = run_security_checks()
    elif args.command == "build":
        success = build_package()
    elif args.command == "docs":
        success = build_docs()
    elif args.command == "serve-docs":
        success = serve_docs()
    elif args.command == "check-all":
        success = run_all_checks()
    elif args.command == "clean":
        clean()
    elif args.command == "install-deps":
        success = install_dev_dependencies()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()