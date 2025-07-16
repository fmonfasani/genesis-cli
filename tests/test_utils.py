"""
Tests para utilidades de Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO testea lógica de generación
- NO testea agentes directamente
- SÍ testea utilities de UX/UI
- SÍ testea validación de entrada del usuario
- Enfocado en funcionalidades de interfaz
"""

import pytest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock, mock_open

from genesis_cli.utils import (
    get_terminal_size,
    is_interactive_terminal,
    get_user_confirmation,
    get_user_input,
    validate_project_name,
    validate_template_name,
    validate_project_directory,
    validate_features,
    detect_project_type,
    get_project_metadata,
    format_file_size,
    get_directory_size,
    clean_ansi_codes,
    create_backup_name,
    safe_remove_directory,
    safe_copy_file,
    get_available_port,
    format_duration,
    truncate_text,
    get_env_info
)


class TestTerminalUtilities:
    """
    Tests para utilidades de terminal
    
    DOCTRINA: Enfocado en UX/UI
    """
    
    def test_get_terminal_size_success(self):
        """Test obtener tamaño de terminal exitoso"""
        with patch('shutil.get_terminal_size') as mock_get_size:
            mock_get_size.return_value = Mock(columns=80, lines=24)
            
            width, height = get_terminal_size()
            assert width == 80
            assert height == 24
    
    def test_get_terminal_size_fallback(self):
        """Test fallback cuando no se puede obtener tamaño"""
        with patch('shutil.get_terminal_size') as mock_get_size:
            mock_get_size.side_effect = Exception("Terminal size not available")
            
            width, height = get_terminal_size()
            assert width == 80  # Fallback
            assert height == 24  # Fallback
    
    def test_is_interactive_terminal_true(self):
        """Test terminal interactivo"""
        with patch('sys.stdin.isatty') as mock_stdin, \
             patch('sys.stdout.isatty') as mock_stdout:
            mock_stdin.return_value = True
            mock_stdout.return_value = True
            
            assert is_interactive_terminal() == True
    
    def test_is_interactive_terminal_false(self):
        """Test terminal no interactivo"""
        with patch('sys.stdin.isatty') as mock_stdin, \
             patch('sys.stdout.isatty') as mock_stdout:
            mock_stdin.return_value = False
            mock_stdout.return_value = True
            
            assert is_interactive_terminal() == False
    
    def test_get_user_confirmation_interactive_yes(self):
        """Test confirmación del usuario - sí"""
        with patch('genesis_cli.utils.is_interactive_terminal') as mock_interactive, \
             patch('genesis_cli.utils.Confirm.ask') as mock_ask:
            mock_interactive.return_value = True
            mock_ask.return_value = True
            
            result = get_user_confirmation("Test question?")
            assert result == True
            mock_ask.assert_called_once_with("[yellow]Test question?[/yellow]", default=False)
    
    def test_get_user_confirmation_interactive_no(self):
        """Test confirmación del usuario - no"""
        with patch('genesis_cli.utils.is_interactive_terminal') as mock_interactive, \
             patch('genesis_cli.utils.Confirm.ask') as mock_ask:
            mock_interactive.return_value = True
            mock_ask.return_value = False
            
            result = get_user_confirmation("Test question?")
            assert result == False
    
    def test_get_user_confirmation_non_interactive(self):
        """Test confirmación en terminal no interactivo"""
        with patch('genesis_cli.utils.is_interactive_terminal') as mock_interactive:
            mock_interactive.return_value = False
            
            result = get_user_confirmation("Test question?", default=True)
            assert result == True
    
    def test_get_user_input_interactive(self):
        """Test entrada del usuario en terminal interactivo"""
        with patch('genesis_cli.utils.is_interactive_terminal') as mock_interactive, \
             patch('genesis_cli.utils.Prompt.ask') as mock_ask:
            mock_interactive.return_value = True
            mock_ask.return_value = "test input"
            
            result = get_user_input("Enter something:", default="default")
            assert result == "test input"
            mock_ask.assert_called_once_with("[cyan]Enter something:[/cyan]", default="default")
    
    def test_get_user_input_with_choices(self):
        """Test entrada del usuario con opciones"""
        with patch('genesis_cli.utils.is_interactive_terminal') as mock_interactive, \
             patch('genesis_cli.utils.Prompt.ask') as mock_ask:
            mock_interactive.return_value = True
            mock_ask.return_value = "option1"
            
            result = get_user_input("Choose option:", choices=["option1", "option2"])
            assert result == "option1"
            mock_ask.assert_called_once_with(
                "[cyan]Choose option:[/cyan]", 
                choices=["option1", "option2"], 
                default=None
            )
    
    def test_get_user_input_non_interactive(self):
        """Test entrada del usuario en terminal no interactivo"""
        with patch('genesis_cli.utils.is_interactive_terminal') as mock_interactive:
            mock_interactive.return_value = False
            
            result = get_user_input("Enter something:", default="default")
            assert result == "default"


class TestValidationUtilities:
    """
    Tests para utilidades de validación
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def test_validate_project_name_valid(self):
        """Test validación de nombre de proyecto válido"""
        result = validate_project_name("valid-project")
        assert result["valid"] == True
        assert len(result["errors"]) == 0
    
    def test_validate_project_name_invalid(self):
        """Test validación de nombre de proyecto inválido"""
        result = validate_project_name("123-invalid")
        assert result["valid"] == False
        assert len(result["errors"]) > 0
        assert "debe comenzar con letra" in str(result["errors"])
    
    def test_validate_project_name_empty(self):
        """Test validación de nombre vacío"""
        result = validate_project_name("")
        assert result["valid"] == False
        assert "requerido" in str(result["errors"])
    
    def test_validate_project_name_too_long(self):
        """Test validación de nombre muy largo"""
        long_name = "a" * 51
        result = validate_project_name(long_name)
        assert result["valid"] == False
        assert "50 caracteres" in str(result["errors"])
    
    def test_validate_project_name_reserved(self):
        """Test validación de nombre reservado"""
        result = validate_project_name("con")
        assert result["valid"] == False
        assert "reservado" in str(result["errors"])
    
    def test_validate_template_name_valid(self):
        """Test validación de template válido"""
        result = validate_template_name("saas-basic")
        assert result["valid"] == True
        assert len(result["errors"]) == 0
    
    def test_validate_template_name_invalid(self):
        """Test validación de template inválido"""
        result = validate_template_name("invalid-template")
        assert result["valid"] == False
        assert "inválido" in str(result["errors"])
    
    def test_validate_project_directory_valid(self):
        """Test validación de directorio válido"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validate_project_directory(temp_dir, force=False)
            assert result["valid"] == True
            assert len(result["errors"]) == 0
    
    def test_validate_project_directory_nonexistent(self):
        """Test validación de directorio inexistente"""
        result = validate_project_directory("/nonexistent/path", force=False)
        assert result["valid"] == False
        assert "no existe" in str(result["errors"])
    
    def test_validate_project_directory_no_permissions(self):
        """Test validación de directorio sin permisos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cambiar permisos
            os.chmod(temp_dir, 0o444)
            
            try:
                result = validate_project_directory(temp_dir, force=False)
                if not result["valid"]:
                    assert "permisos" in str(result["errors"])
            finally:
                # Restaurar permisos
                os.chmod(temp_dir, 0o755)
    
    def test_validate_features_valid(self):
        """Test validación de características válidas"""
        result = validate_features(["authentication", "database", "api"])
        assert result["valid"] == True
        assert len(result["errors"]) == 0
    
    def test_validate_features_invalid(self):
        """Test validación de características inválidas"""
        result = validate_features(["invalid-feature"])
        assert result["valid"] == False
        assert "inválida" in str(result["errors"])
    
    def test_validate_features_empty(self):
        """Test validación de características vacías"""
        result = validate_features([])
        assert result["valid"] == True
        assert len(result["errors"]) == 0


class TestProjectUtilities:
    """
    Tests para utilidades de proyecto
    
    DOCTRINA: Utility para mejorar UX
    """
    
    def test_detect_project_type_genesis(self):
        """Test detectar proyecto Genesis"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear genesis.json
            genesis_file = Path(temp_dir) / "genesis.json"
            genesis_file.write_text('{"name": "test-project"}')
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                project_type = detect_project_type()
                assert project_type == "genesis"
            finally:
                os.chdir(original_cwd)
    
    def test_detect_project_type_nodejs(self):
        """Test detectar proyecto Node.js"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear package.json
            package_file = Path(temp_dir) / "package.json"
            package_file.write_text('{"name": "test-project"}')
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                project_type = detect_project_type()
                assert project_type == "nodejs"
            finally:
                os.chdir(original_cwd)
    
    def test_detect_project_type_python(self):
        """Test detectar proyecto Python"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear requirements.txt
            requirements_file = Path(temp_dir) / "requirements.txt"
            requirements_file.write_text("flask==2.0.0")
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                project_type = detect_project_type()
                assert project_type == "python"
            finally:
                os.chdir(original_cwd)
    
    def test_detect_project_type_none(self):
        """Test no detectar tipo de proyecto"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                project_type = detect_project_type()
                assert project_type is None
            finally:
                os.chdir(original_cwd)
    
    def test_get_project_metadata_valid(self):
        """Test obtener metadata de proyecto válido"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear genesis.json
            genesis_file = Path(temp_dir) / "genesis.json"
            project_data = {
                "name": "test-project",
                "template": "saas-basic",
                "version": "1.0.0"
            }
            genesis_file.write_text(json.dumps(project_data))
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                metadata = get_project_metadata()
                assert metadata is not None
                assert metadata["name"] == "test-project"
                assert metadata["template"] == "saas-basic"
                assert metadata["version"] == "1.0.0"
            finally:
                os.chdir(original_cwd)
    
    def test_get_project_metadata_no_file(self):
        """Test obtener metadata sin archivo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                metadata = get_project_metadata()
                assert metadata is None
            finally:
                os.chdir(original_cwd)
    
    def test_get_project_metadata_invalid_json(self):
        """Test obtener metadata con JSON inválido"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear genesis.json con contenido inválido
            genesis_file = Path(temp_dir) / "genesis.json"
            genesis_file.write_text("invalid json content")
            
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                metadata = get_project_metadata()
                assert metadata is None
            finally:
                os.chdir(original_cwd)


class TestFileUtilities:
    """
    Tests para utilidades de archivo
    
    DOCTRINA: Utility para mejorar UX
    """
    
    def test_format_file_size_bytes(self):
        """Test formatear tamaño en bytes"""
        assert format_file_size(0) == "0 B"
        assert format_file_size(512) == "512 B"
        assert format_file_size(1023) == "1023 B"
    
    def test_format_file_size_kb(self):
        """Test formatear tamaño en KB"""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(2048) == "2.0 KB"
    
    def test_format_file_size_mb(self):
        """Test formatear tamaño en MB"""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1536 * 1024) == "1.5 MB"
        assert format_file_size(2048 * 1024) == "2.0 MB"
    
    def test_format_file_size_gb(self):
        """Test formatear tamaño en GB"""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(1536 * 1024 * 1024) == "1.5 GB"
    
    def test_get_directory_size_empty(self):
        """Test obtener tamaño de directorio vacío"""
        with tempfile.TemporaryDirectory() as temp_dir:
            size = get_directory_size(Path(temp_dir))
            assert size == 0
    
    def test_get_directory_size_with_files(self):
        """Test obtener tamaño de directorio con archivos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivos
            file1 = Path(temp_dir) / "file1.txt"
            file1.write_text("Hello World")  # 11 bytes
            
            file2 = Path(temp_dir) / "file2.txt"
            file2.write_text("Test Content")  # 12 bytes
            
            size = get_directory_size(Path(temp_dir))
            assert size >= 23  # Al menos 23 bytes
    
    def test_get_directory_size_nested(self):
        """Test obtener tamaño de directorio anidado"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear directorio anidado
            nested_dir = Path(temp_dir) / "nested"
            nested_dir.mkdir()
            
            # Crear archivos en diferentes niveles
            file1 = Path(temp_dir) / "file1.txt"
            file1.write_text("Content 1")
            
            file2 = nested_dir / "file2.txt"
            file2.write_text("Content 2")
            
            size = get_directory_size(Path(temp_dir))
            assert size >= 18  # Al menos contenido de ambos archivos
    
    def test_get_directory_size_nonexistent(self):
        """Test obtener tamaño de directorio inexistente"""
        size = get_directory_size(Path("/nonexistent/path"))
        assert size == 0
    
    def test_safe_copy_file_success(self):
        """Test copia segura de archivo exitosa"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo fuente
            src_file = Path(temp_dir) / "source.txt"
            src_file.write_text("Test content")
            
            # Copiar archivo
            dst_file = Path(temp_dir) / "destination.txt"
            result = safe_copy_file(src_file, dst_file)
            
            assert result == True
            assert dst_file.exists()
            assert dst_file.read_text() == "Test content"
    
    def test_safe_copy_file_create_directories(self):
        """Test copia segura creando directorios"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo fuente
            src_file = Path(temp_dir) / "source.txt"
            src_file.write_text("Test content")
            
            # Copiar a directorio que no existe
            dst_file = Path(temp_dir) / "nested" / "dir" / "destination.txt"
            result = safe_copy_file(src_file, dst_file)
            
            assert result == True
            assert dst_file.exists()
            assert dst_file.read_text() == "Test content"
    
    def test_safe_copy_file_failure(self):
        """Test copia segura con fallo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Archivo fuente que no existe
            src_file = Path(temp_dir) / "nonexistent.txt"
            dst_file = Path(temp_dir) / "destination.txt"
            
            result = safe_copy_file(src_file, dst_file)
            assert result == False
    
    def test_safe_remove_directory_success(self):
        """Test eliminación segura de directorio exitosa"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear directorio para eliminar
            dir_to_remove = Path(temp_dir) / "to_remove"
            dir_to_remove.mkdir()
            
            # Crear archivo dentro
            (dir_to_remove / "file.txt").write_text("content")
            
            # Eliminar directorio
            result = safe_remove_directory(dir_to_remove)
            assert result == True
            assert not dir_to_remove.exists()
    
    def test_safe_remove_directory_failure(self):
        """Test eliminación segura con fallo"""
        # Directorio que no existe
        nonexistent_dir = Path("/nonexistent/path")
        result = safe_remove_directory(nonexistent_dir)
        assert result == False


class TestStringUtilities:
    """
    Tests para utilidades de cadenas
    
    DOCTRINA: Utility para mejorar UX
    """
    
    def test_clean_ansi_codes_no_codes(self):
        """Test limpia