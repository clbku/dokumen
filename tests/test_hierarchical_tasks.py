"""
Tests for hierarchical task definitions.

This test suite verifies the task definitions for the hierarchical workflow,
ensuring proper output_pydantic schemas and context linking between tasks.

Note: These tests focus on task definition logic without requiring Task creation,
which would need actual Agent instances with API keys.
"""

import pytest
from src.schemas import HappyPath, StressTestReport
from src.tasks import (
    get_task_for_phase,
    HappyPathTaskDefinition,
    BusinessExceptionsTaskDefinition,
    TechnicalEdgeCasesTaskDefinition,
)


class TestTaskDefinitionClasses:
    """Test suite for individual task definition classes."""

    def test_happy_path_task_definition_class(self):
        """Test HappyPathTaskDefinition class instantiation and methods."""
        task_def = HappyPathTaskDefinition()

        assert hasattr(task_def, 'create_task')
        assert callable(task_def.create_task)

    def test_business_exceptions_task_definition_class(self):
        """Test BusinessExceptionsTaskDefinition class instantiation and methods."""
        task_def = BusinessExceptionsTaskDefinition()

        assert hasattr(task_def, 'create_task')
        assert callable(task_def.create_task)

    def test_technical_edge_cases_task_definition_class(self):
        """Test TechnicalEdgeCasesTaskDefinition class instantiation and methods."""
        task_def = TechnicalEdgeCasesTaskDefinition()

        assert hasattr(task_def, 'create_task')
        assert callable(task_def.create_task)


class TestHappyPathTaskOutputPydantic:
    """Test suite for HappyPathTaskDefinition output_pydantic configuration."""

    def test_happy_path_task_returns_correct_schema(self):
        """Test that HappyPathTaskDefinition uses HappyPath schema."""
        task_definition = HappyPathTaskDefinition()

        # The create_task method should set output_pydantic to HappyPath
        # We can verify this by checking the code structure
        from inspect import getsource
        source = getsource(task_definition.create_task)

        assert "output_pydantic=HappyPath" in source
        assert "HappyPath" in source

    def test_happy_path_task_description_structure(self):
        """Test that HappyPath task description has proper structure."""
        task_definition = HappyPathTaskDefinition()

        # Check that description template includes key elements
        from inspect import getsource
        source = getsource(task_definition.create_task)

        assert "happy path" in source.lower()
        assert "steps" in source.lower()
        assert "pre_conditions" in source.lower()
        assert "post_conditions" in source.lower()


class TestBusinessExceptionsTaskContext:
    """Test suite for BusinessExceptionsTaskDefinition context linking."""

    def test_business_exceptions_task_accepts_context(self):
        """Test that BusinessExceptionsTaskDefinition accepts context parameter."""
        task_def = BusinessExceptionsTaskDefinition()

        # Check that create_task method accepts context parameter
        from inspect import signature
        sig = signature(task_def.create_task)

        assert 'context' in sig.parameters
        # The default value should be None (which is correct - optional parameter)


class TestTechnicalEdgeCasesTaskContext:
    """Test suite for TechnicalEdgeCasesTaskDefinition context linking."""

    def test_technical_edge_cases_task_returns_correct_schema(self):
        """Test that TechnicalEdgeCasesTaskDefinition uses StressTestReport schema."""
        task_definition = TechnicalEdgeCasesTaskDefinition()

        # The create_task method should set output_pydantic to StressTestReport
        from inspect import getsource
        source = getsource(task_definition.create_task)

        assert "output_pydantic=StressTestReport" in source
        assert "StressTestReport" in source

    def test_technical_edge_cases_task_accepts_context(self):
        """Test that TechnicalEdgeCasesTaskDefinition accepts context parameter."""
        task_def = TechnicalEdgeCasesTaskDefinition()

        # Check that create_task method accepts context parameter
        from inspect import signature
        sig = signature(task_def.create_task)

        assert 'context' in sig.parameters
        # The default value should be None (which is correct - optional parameter)


class TestGetTaskForPhase:
    """Test suite for get_task_for_phase helper function."""

    def test_get_task_for_phase_invalid_phase_raises_error(self):
        """Test that invalid phase raises ValueError."""
        with pytest.raises(ValueError, match="Invalid phase"):
            get_task_for_phase(
                phase="invalid_phase",
                user_requirement="Test requirement",
                agent=None,  # We won't actually create the task
            )

    def test_get_task_for_phase_is_callable(self):
        """Test that get_task_for_phase is a callable function."""
        assert callable(get_task_for_phase)


class TestTaskDefinitionsStructure:
    """Test suite for verifying task definitions structure."""

    def test_happy_path_task_definition_structure(self):
        """Test that HappyPathTaskDefinition has proper method signature."""
        task_def = HappyPathTaskDefinition()
        from inspect import signature

        sig = signature(task_def.create_task)
        params = list(sig.parameters.keys())

        assert 'user_requirement' in params
        assert 'agent' in params
        assert 'context' not in params  # Happy path doesn't use context

    def test_business_exceptions_task_definition_structure(self):
        """Test that BusinessExceptionsTaskDefinition has proper method signature."""
        task_def = BusinessExceptionsTaskDefinition()
        from inspect import signature

        sig = signature(task_def.create_task)
        params = list(sig.parameters.keys())

        assert 'user_requirement' in params
        assert 'agent' in params
        assert 'context' in params  # Business exceptions uses context

    def test_technical_edge_cases_task_definition_structure(self):
        """Test that TechnicalEdgeCasesTaskDefinition has proper method signature."""
        task_def = TechnicalEdgeCasesTaskDefinition()
        from inspect import signature

        sig = signature(task_def.create_task)
        params = list(sig.parameters.keys())

        assert 'user_requirement' in params
        assert 'agent' in params
        assert 'context' in params  # Technical edge cases uses context
