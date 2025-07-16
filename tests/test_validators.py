"""
Tests para validadores de Genesis CLI

DOCTRINA DEL ECOSISTEMA:
- NO testea lógica de generación
- NO testea agentes directamente
- SÍ testea validación de entrada del usuario
- SÍ testea mensajes de error elegantes
- Enfocado en UX/UI para validación
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from genesis_cli.validators import (
    ProjectNameValidator,
    TemplateValidator,
    DirectoryValidator,
    FeatureValidator,
    ValidationResult,
    validate_project_name,
    validate_template,
    validate_directory,
    validate_features,
    validate_project_config
)
from genesis_cli.exceptions import ValidationError, ProjectNameError, TemplateError


class TestValidationResult:
    """
    Tests para ValidationResult
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def test_validation_result_success(self):
        """Test resultado de validación exitoso"""
        result = ValidationResult.success()
        assert result.is_valid == True
        assert result.errors == []
        assert result.warnings == []
        assert result.suggestions == []
    
    def test_validation_result_success_with_warnings(self):
        """Test resultado exitoso con advertencias"""
        warnings = ["Warning 1", "Warning 2"]
        suggestions = ["Suggestion 1"]
        result = ValidationResult.success(warnings=warnings, suggestions=suggestions)
        
        assert result.is_valid == True
        assert result.errors == []
        assert result.warnings == warnings
        assert result.suggestions == suggestions
    
    def test_validation_result_failure(self):
        """Test resultado de validación fallido"""
        errors = ["Error 1", "Error 2"]
        result = ValidationResult.failure(errors)
        
        assert result.is_valid == False
        assert result.errors == errors
        assert result.warnings == []
        assert result.suggestions == []
    
    def test_validation_result_add_error(self):
        """Test agregar error a resultado"""
        result = ValidationResult.success()
        result.add_error("Test error")
        
        assert result.is_valid == False
        assert "Test error" in result.errors
    
    def test_validation_result_add_warning(self):
        """Test agregar advertencia a resultado"""
        result = ValidationResult.success()
        result.add_warning("Test warning")
        
        assert result.is_valid == True
        assert "Test warning" in result.warnings
    
    def test_validation_result_add_suggestion(self):
        """Test agregar sugerencia a resultado"""
        result = ValidationResult.success()
        result.add_suggestion("Test suggestion")
        
        assert result.is_valid == True
        assert "Test suggestion" in result.suggestions


class TestProjectNameValidator:
    """
    Tests para ProjectNameValidator
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def test_validate_valid_names(self):
        """Test nombres válidos"""
        valid_names = [
            "mi-proyecto",
            "web-app",
            "user_dashboard",
            "project123",
            "app_v2",
            "backend-api",
            "frontend-ui",
            "MyProject",
            "webApp"
        ]
        
        for name in valid_names:
            result = ProjectNameValidator.validate(name)
            assert result.is_valid, f"'{name}' should be valid but got errors: {result.errors}"
    
    def test_validate_empty_name(self):
        """Test nombre vacío"""
        result = ProjectNameValidator.validate("")
        assert not result.is_valid
        assert "requerido" in str(result.errors)
    
    def test_validate_none_name(self):
        """Test nombre None"""
        result = ProjectNameValidator.validate(None)
        assert not result.is_valid
        assert "requerido" in str(result.errors)
    
    def test_validate_non_string_name(self):
        """Test nombre que no es string"""
        result = ProjectNameValidator.validate(123)
        assert not result.is_valid
        assert "cadena de texto" in str(result.errors)
    
    def test_validate_too_short_name(self):
        """Test nombre muy corto"""
        result = ProjectNameValidator.validate("a")
        assert not result.is_valid
        assert "al menos 2 caracteres" in str(result.errors)
        assert "Ejemplo:" in str(result.suggestions)
    
    def test_validate_too_long_name(self):
        """Test nombre muy largo"""
        long_name = "a" * 51
        result = ProjectNameValidator.validate(long_name)
        assert not result.is_valid
        assert "más de 50 caracteres" in str(result.errors)
        assert "más corto" in str(result.suggestions)
    
    def test_validate_starts_with_number(self):
        """Test nombre que comienza con número"""
        result = ProjectNameValidator.validate("123-project")
        assert not result.is_valid
        assert "debe comenzar con una letra" in str(result.errors)
        assert "Ejemplo:" in str(result.suggestions)
    
    def test_validate_invalid_characters(self):
        """Test nombre con caracteres inválidos"""
        invalid_names = [
            "project with spaces",
            "project@domain",
            "project#hash",
            "project$money",
            "project%percent",
            "project&and",
            "project*star",
            "project(paren",
            "project)paren",
            "project+plus",
            "project=equals",
            "project[bracket",
            "project]bracket",
            "project{brace",
            "project}brace",
            "project|pipe",
            "project\\backslash",
            "project:colon",
            "project;semicolon",
            "project\"quote",
            "project'apostrophe",
            "project<less",
            "project>greater",
            "project,comma",
            "project.dot",
            "project?question",
            "project/slash"
        ]
        
        for name in invalid_names:
            result = ProjectNameValidator.validate(name)
            assert not result.is_valid, f"'{name}' should be invalid"
            assert "solo puede contener" in str(result.errors)
    
    def test_validate_reserved_names(self):
        """Test nombres reservados"""
        reserved_names = [
            "con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", "com5",
            "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
            "lpt5", "lpt6", "lpt7", "lpt8", "lpt9", "test", "example", "sample",
            "demo", "tmp", "temp", "cache", "and", "or", "not", "if", "else",
            "for", "while", "def", "class", "import", "from", "as", "try",
            "except", "finally", "with", "lambda", "yield", "return", "pass",
            "break", "continue", "global", "nonlocal", "assert", "del", "in",
            "is", "raise", "true", "false", "none"
        ]
        
        for name in reserved_names:
            result = ProjectNameValidator.validate(name)
            assert not result.is_valid, f"'{name}' should be reserved"
            assert "reservado" in str(result.errors)
    
    def test_validate_warnings(self):
        """Test advertencias en validación"""
        # Nombre que termina con guión
        result = ProjectNameValidator.validate("project-")
        assert result.is_valid
        assert "termina con guión" in str(result.warnings)
        
        # Nombre que comienza con underscore
        result = ProjectNameValidator.validate("_project")
        assert result.is_valid
        assert "comienza con guión bajo" in str(result.warnings)
        
        # Nombre con doble guión
        result = ProjectNameValidator.validate("project--name")
        assert result.is_valid
        assert "guiones dobles" in str(result.warnings)
        
        # Nombre con doble underscore
        result = ProjectNameValidator.validate("project__name")
        assert result.is_valid
        assert "guiones bajos dobles" in str(result.warnings)
    
    def test_validate_suggestions(self):
        """Test sugerencias en validación"""
        # Nombre todo en mayúsculas
        result = ProjectNameValidator.validate("PROJECT")
        assert result.is_valid
        assert "minúsculas" in str(result.suggestions)
        
        # Nombre muy largo
        result = ProjectNameValidator.validate("a" * 40)
        assert result.is_valid
        assert "más cortos" in str(result.suggestions)


class TestTemplateValidator:
    """
    Tests para TemplateValidator
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def test_validate_valid_templates(self):
        """Test templates válidos"""
        valid_templates = [
            "saas-basic",
            "api-only",
            "frontend-only",
            "microservices",
            "e-commerce",
            "blog",
            "ai-ready",
            "minimal"
        ]
        
        for template in valid_templates:
            result = TemplateValidator.validate(template)
            assert result.is_valid, f"'{template}' should be valid but got errors: {result.errors}"
    
    def test_validate_empty_template(self):
        """Test template vacío"""
        result = TemplateValidator.validate("")
        assert not result.is_valid
        assert "requerido" in str(result.errors)
        assert "saas-basic" in str(result.suggestions)
    
    def test_validate_none_template(self):
        """Test template None"""
        result = TemplateValidator.validate(None)
        assert not result.is_valid
        assert "requerido" in str(result.errors)
    
    def test_validate_non_string_template(self):
        """Test template que no es string"""
        result = TemplateValidator.validate(123)
        assert not result.is_valid
        assert "cadena de texto" in str(result.errors)
    
    def test_validate_invalid_template(self):
        """Test template inválido"""
        result = TemplateValidator.validate("invalid-template")
        assert not result.is_valid
        assert "no encontrado" in str(result.errors)
        assert "Templates disponibles:" in str(result.suggestions)
    
    def test_find_similar_template(self):
        """Test búsqueda de template similar"""
        # Test con nombres similares
        similar_tests = [
            ("saas", "saas-basic"),
            ("api", "api-only"),
            ("frontend", "frontend-only"),
            ("ui", "frontend-only"),
            ("shop", "e-commerce"),
            ("store", "e-commerce"),
            ("blog", "blog"),
            ("ai", "ai-ready"),
            ("simple", "minimal"),
            ("basic", "minimal")
        ]
        
        for input_template, expected_similar in similar_tests:
            similar = TemplateValidator._find_similar_template(input_template)
            assert similar == expected_similar, f"'{input_template}' should suggest '{expected_similar}' but got '{similar}'"
    
    def test_find_similar_template_none(self):
        """Test búsqueda de template similar sin coincidencia"""
        similar = TemplateValidator._find_similar_template("completely-unknown")
        assert similar is None
    
    def test_get_template_info(self):
        """Test obtener información del template"""
        info = TemplateValidator.get_template_info("saas-basic")
        assert info is not None
        assert info["name"] == "SaaS Básico"
        assert "authentication" in info["features"]
        assert info["complexity"] == "Media"
    
    def test_get_template_info_invalid(self):
        """Test obtener información de template inválido"""
        info = TemplateValidator.get_template_info("invalid-template")
        assert info is None
    
    def test_list_templates(self):
        """Test listar todos los templates"""
        templates = TemplateValidator.list_templates()
        assert len(templates) == 8  # Número de templates oficiales
        
        # Verificar que todos tienen la estructura correcta
        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "description" in template
            assert "features" in template
            assert "complexity" in template
        
        # Verificar que incluye templates esperados
        template_ids = [t["id"] for t in templates]
        assert "saas-basic" in template_ids
        assert "api-only" in template_ids
        assert "ai-ready" in template_ids


class TestDirectoryValidator:
    """
    Tests para DirectoryValidator
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def test_validate_valid_directory(self):
        """Test directorio válido"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DirectoryValidator.validate_output_directory(temp_dir, "new-project")
            assert result.is_valid, f"Valid directory should pass but got errors: {result.errors}"
    
    def test_validate_nonexistent_parent(self):
        """Test directorio padre que no existe"""
        result = DirectoryValidator.validate_output_directory("/nonexistent/path", "project")
        assert not result.is_valid
        assert "no existe" in str(result.errors)
    
    def test_validate_not_directory(self):
        """Test path que no es directorio"""
        with tempfile.NamedTemporaryFile() as temp_file:
            result = DirectoryValidator.validate_output_directory(temp_file.name, "project")
            assert not result.is_valid
            assert "no es un directorio" in str(result.errors)
    
    def test_validate_no_write_permission(self):
        """Test directorio sin permisos de escritura"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Cambiar permisos para solo lectura
            import os
            os.chmod(temp_dir, 0o444)
            
            try:
                result = DirectoryValidator.validate_output_directory(temp_dir, "project")
                # En algunos sistemas esto puede fallar, en otros no
                if not result.is_valid:
                    assert "permisos de escritura" in str(result.errors)
            finally:
                # Restaurar permisos
                os.chmod(temp_dir, 0o755)
    
    def test_validate_existing_empty_directory(self):
        """Test directorio existente vacío"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear directorio vacío
            project_dir = Path(temp_dir) / "existing-project"
            project_dir.mkdir()
            
            result = DirectoryValidator.validate_output_directory(temp_dir, "existing-project")
            assert result.is_valid
            assert "existe pero está vacío" in str(result.warnings)
    
    def test_validate_existing_non_empty_directory(self):
        """Test directorio existente no vacío"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear directorio con archivo
            project_dir = Path(temp_dir) / "existing-project"
            project_dir.mkdir()
            (project_dir / "existing_file.txt").write_text("content")
            
            result = DirectoryValidator.validate_output_directory(temp_dir, "existing-project")
            assert not result.is_valid
            assert "no está vacío" in str(result.errors)
            assert "--force" in str(result.suggestions)
    
    def test_validate_existing_directory_with_force(self):
        """Test directorio existente con force"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear directorio con archivo
            project_dir = Path(temp_dir) / "existing-project"
            project_dir.mkdir()
            (project_dir / "existing_file.txt").write_text("content")
            
            result = DirectoryValidator.validate_output_directory(temp_dir, "existing-project", force=True)
            assert result.is_valid
            assert "será sobrescrito" in str(result.warnings)
    
    @patch('shutil.disk_usage')
    def test_validate_low_disk_space(self, mock_disk_usage):
        """Test espacio en disco bajo"""
        # Mock para simular poco espacio (50MB)
        mock_disk_usage.return_value = Mock(free=50 * 1024 * 1024)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = DirectoryValidator.validate_output_directory(temp_dir, "project")
            assert result.is_valid  # Debe ser válido pero con advertencia
            assert "espacio disponible" in str(result.warnings)


class TestFeatureValidator:
    """
    Tests para FeatureValidator
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def test_validate_valid_features(self):
        """Test características válidas"""
        valid_features = [
            ["authentication", "database", "api"],
            ["frontend", "docker", "cicd"],
            ["monitoring", "ai", "testing"],
            ["documentation", "analytics", "caching"],
            ["search", "notifications", "payments"]
        ]
        
        for features in valid_features:
            result = FeatureValidator.validate(features)
            assert result.is_valid, f"'{features}' should be valid but got errors: {result.errors}"
    
    def test_validate_empty_features(self):
        """Test lista vacía de características"""
        result = FeatureValidator.validate([])
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_non_list_features(self):
        """Test características que no son lista"""
        result = FeatureValidator.validate("authentication")
        assert not result.is_valid
        assert "lista" in str(result.errors)
    
    def test_validate_invalid_features(self):
        """Test características inválidas"""
        result = FeatureValidator.validate(["invalid-feature", "another-invalid"])
        assert not result.is_valid
        assert "inválidas" in str(result.errors)
        assert "invalid-feature" in str(result.errors)
        assert "another-invalid" in str(result.errors)
    
    def test_validate_mixed_features(self):
        """Test mezcla de características válidas e inválidas"""
        result = FeatureValidator.validate(["authentication", "invalid-feature", "database"])
        assert not result.is_valid
        assert "invalid-feature" in str(result.errors)
        assert "authentication" not in str(result.errors)
        assert "database" not in str(result.errors)
    
    def test_validate_dependencies_auto_added(self):
        """Test dependencias agregadas automáticamente"""
        result = FeatureValidator.validate(["ai"])
        assert result.is_valid
        assert "agregadas" in str(result.warnings)
        # AI requiere api y database
        assert "api" in str(result.warnings) or "database" in str(result.warnings)
    
    def test_validate_payment_requires_auth(self):
        """Test que payments requiere authentication"""
        result = FeatureValidator.validate(["payments"])
        assert not result.is_valid
        assert "payments" in str(result.errors)
        assert "authentication" in str(result.errors)
    
    def test_validate_ai_requires_database(self):
        """Test que ai requiere database"""
        result = FeatureValidator.validate(["ai"])
        # Debería ser válido porque las dependencias se resuelven automáticamente
        assert result.is_valid
        assert "agregadas" in str(result.warnings)
    
    def test_resolve_dependencies(self):
        """Test resolución de dependencias"""
        # Test con ai que requiere api y database
        resolved = FeatureValidator._resolve_dependencies(["ai"])
        assert "ai" in resolved
        assert "api" in resolved
        assert "database" in resolved
        
        # Test con payments que requiere database y authentication
        resolved = FeatureValidator._resolve_dependencies(["payments"])
        assert "payments" in resolved
        assert "database" in resolved
        assert "authentication" in resolved
        
        # Test con cicd que requiere docker
        resolved = FeatureValidator._resolve_dependencies(["cicd"])
        assert "cicd" in resolved
        assert "docker" in resolved
    
    def test_get_feature_info(self):
        """Test obtener información de característica"""
        info = FeatureValidator.get_feature_info("authentication")
        assert info is not None
        assert info["name"] == "Autenticación"
        assert "autenticación" in info["description"].lower()
        assert "database" in info["dependencies"]
    
    def test_get_feature_info_invalid(self):
        """Test obtener información de característica inválida"""
        info = FeatureValidator.get_feature_info("invalid-feature")
        assert info is None
    
    def test_list_features(self):
        """Test listar todas las características"""
        features = FeatureValidator.list_features()
        assert len(features) == 15  # Número de características válidas
        
        # Verificar que todas tienen la estructura correcta
        for feature in features:
            assert "id" in feature
            assert "name" in feature
            assert "description" in feature
            assert "dependencies" in feature
        
        # Verificar que incluye características esperadas
        feature_ids = [f["id"] for f in features]
        assert "authentication" in feature_ids
        assert "database" in feature_ids
        assert "ai" in feature_ids
        assert "payments" in feature_ids


class TestConvenienceFunctions:
    """
    Tests para funciones de conveniencia
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def test_validate_project_name_function(self):
        """Test función validate_project_name"""
        result = validate_project_name("valid-project")
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        
        result = validate_project_name("123-invalid")
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
    
    def test_validate_template_function(self):
        """Test función validate_template"""
        result = validate_template("saas-basic")
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        
        result = validate_template("invalid-template")
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
    
    def test_validate_directory_function(self):
        """Test función validate_directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validate_directory(temp_dir, "project")
            assert isinstance(result, ValidationResult)
            assert result.is_valid
        
        result = validate_directory("/nonexistent", "project")
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
    
    def test_validate_features_function(self):
        """Test función validate_features"""
        result = validate_features(["authentication", "database"])
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        
        result = validate_features(["invalid-feature"])
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
    
    def test_validate_project_config_function(self):
        """Test función validate_project_config"""
        valid_config = {
            "name": "test-project",
            "template": "saas-basic",
            "features": ["authentication", "database"],
            "output_path": "/tmp",
            "force": False
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            valid_config["output_path"] = temp_dir
            result = validate_project_config(valid_config)
            assert isinstance(result, ValidationResult)
            # Puede tener warnings pero debería ser válido
            assert result.is_valid or len(result.errors) == 0
        
        # Test con configuración inválida
        invalid_config = {
            "name": "123-invalid",
            "template": "invalid-template",
            "features": ["invalid-feature"],
            "output_path": "/nonexistent",
            "force": False
        }
        
        result = validate_project_config(invalid_config)
        assert isinstance(result, ValidationResult)
        assert not result.is_valid
        assert len(result.errors) > 0


class TestValidationEdgeCases:
    """
    Tests para casos edge en validación
    
    DOCTRINA: Validamos entrada del usuario
    """
    
    def test_unicode_project_names(self):
        """Test nombres de proyecto con unicode"""
        unicode_names = [
            "proyecto-ñ",
            "app-café",
            "système-é",
            "проект-тест",
            "项目-测试",
            "プロジェクト-テスト"
        ]
        
        for name in unicode_names:
            result = validate_project_name(name)
            # Actualmente no soportamos unicode, debería fallar
            assert not result.is_valid
    
    def test_very_long_template_name(self):
        """Test template con nombre muy largo"""
        long_template = "a" * 1000
        result = validate_template(long_template)
        assert not result.is_valid
    
    def test_features_with_duplicates(self):
        """Test características con duplicados"""
        result = validate_features(["authentication", "database", "authentication"])
        assert result.is_valid  # Debería ser válido, duplicados son ignorados
    
    def test_nested_directory_validation(self):
        """Test validación con directorios anidados"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "level1" / "level2" / "level3"
            nested_path.mkdir(parents=True)
            
            result = validate_directory(str(nested_path), "project")
            assert result.is_valid
    
    def test_symlink_directory_validation(self):
        """Test validación con enlaces simbólicos"""
        with tempfile.TemporaryDirectory() as temp_dir:
            real_dir = Path(temp_dir) / "real"
            real_dir.mkdir()
            
            symlink_dir = Path(temp_dir) / "symlink"
            try:
                symlink_dir.symlink_to(real_dir)
                result = validate_directory(str(symlink_dir), "project")
                assert result.is_valid
            except OSError:
                # Si no se pueden crear symlinks, skip test
                pytest.skip("Cannot create symlinks on this system")


# Marcadores para tests
pytestmark = [
    pytest.mark.unit,
    pytest.mark.validators
]