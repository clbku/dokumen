"""
Schema Validation Tests for Deep-Spec AI

Tests to verify that agent outputs comply with Pydantic schemas.
This ensures agents return valid JSON/Class structures without parse errors.

Test Categories:
1. Định dạng JSON/Class: Agent trả về dữ liệu đúng cấu trúc schema
2. Required fields: Tất cả required fields đều có mặt
3. Data types: Kiểu dữ liệu đúng với schema definition
4. Validation rules: Tuân thủ các validation rules (min_length, min_edge_cases, etc.)
"""

import pytest
import json
from src.schemas import (
    HappyPath,
    FlowStep,
    SystemArchitecture,
    SystemComponent,
    Interaction,
    ComponentType,
    Protocol,
    EdgeCase,
    StressTestReport,
    MitigationStrategy,
    RiskLevel,
    AgentComment,
    AgentPerspective,
    ConsensusDecision,
    QualityGateReport,
    MaturityMetric,
    TechnicalDesignDocument,
)


class TestHappyPathSchema:
    """Test HappyPath schema validation."""

    def test_valid_happy_path(self, sample_architect_response, schema_validator):
        """Test that sample architect response is valid HappyPath."""
        result = schema_validator(sample_architect_response, HappyPath)
        assert result['valid'] is True, f"Schema validation failed: {result['errors']}"
        assert result['data']['feature_id'] == 'USER-REG-001'
        assert len(result['data']['steps']) == 6
        assert len(result['data']['post_conditions']) > 0

    def test_happy_path_required_fields(self):
        """Test that HappyPath requires all mandatory fields."""
        # Missing required fields
        invalid_data = {
            "feature_id": "TEST-001",
            # Missing feature_name
            "description": "Test",
            # Missing steps
            "post_conditions": [],
            "business_value": "Test value"
        }

        with pytest.raises(Exception) as exc_info:
            HappyPath(**invalid_data)
        assert "steps" in str(exc_info.value).lower() or "feature_name" in str(exc_info.value).lower()

    def test_flowstep_validation(self):
        """Test FlowStep validation rules."""
        # Invalid step_number (must be >= 1)
        with pytest.raises(Exception):
            FlowStep(
                step_number=0,  # Invalid: must be >= 1
                actor="User",
                action="Test",
                outcome="Success"
            )

    def test_flowstep_with_optional_fields(self):
        """Test FlowStep with error handling fields."""
        step = FlowStep(
            step_number=1,
            actor="System",
            action="Process payment",
            outcome="Payment completed",
            involved_components=["payment-service"],
            error_scenario="Payment gateway timeout",
            fallback_step=5,
            is_critical=True,
            retry_count=3
        )
        assert step.error_scenario == "Payment gateway timeout"
        assert step.fallback_step == 5
        assert step.is_critical is True
        assert step.retry_count == 3


class TestSystemArchitectureSchema:
    """Test SystemArchitecture schema validation."""

    def test_valid_system_architecture(self):
        """Test valid SystemArchitecture creation."""
        components = [
            SystemComponent(
                id="api-gateway",
                name="API Gateway",
                type=ComponentType.SERVICE,
                description="Entry point for all requests",
                technologies=["Kong", "Lua"],
                is_critical=True
            ),
            SystemComponent(
                id="postgres-db",
                name="PostgreSQL Database",
                type=ComponentType.DATABASE,
                description="Primary data store",
                technologies=["PostgreSQL", "14.0"],
                is_critical=True
            )
        ]

        interactions = [
            Interaction(
                source="api-gateway",
                target="postgres-db",
                protocol=Protocol.HTTPS,
                description="Query user data",
                is_synchronous=True
            )
        ]

        arch = SystemArchitecture(components=components, interactions=interactions)
        assert len(arch.components) == 2
        assert len(arch.interactions) == 1

    def test_component_type_validation(self):
        """Test ComponentType enum validation."""
        component = SystemComponent(
            id="test",
            name="Test Service",
            type=ComponentType.SERVICE,
            description="Test"
        )
        assert component.type == ComponentType.SERVICE
        assert component.type.value == "Service"


class TestEdgeCaseSchema:
    """Test EdgeCase schema validation."""

    def test_valid_edge_case(self):
        """Test valid EdgeCase creation."""
        edge_case = EdgeCase(
            scenario_id="EDGE-TEST-001",
            description="Test edge case",
            trigger_condition="Test trigger",
            expected_failure="System fails",
            severity=RiskLevel.HIGH,
            likelihood=RiskLevel.MEDIUM,
            detection_method="Monitor logs",
            related_components=["service-a"],
            related_step=1,
            mitigation=MitigationStrategy(
                description="Fix it",
                technical_implementation="Add retry logic",
                implementation_complexity=RiskLevel.LOW,
                estimated_effort="2 hours"
            )
        )
        assert edge_case.scenario_id == "EDGE-TEST-001"
        assert edge_case.severity == RiskLevel.HIGH

    def test_edge_case_scenario_id_validation(self):
        """Test that EdgeCase scenario_id must start with EDGE-."""
        with pytest.raises(Exception) as exc_info:
            EdgeCase(
                scenario_id="INVALID-ID",  # Must start with EDGE-
                description="Test",
                trigger_condition="Test",
                expected_failure="Fail",
                severity=RiskLevel.LOW,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Fix",
                    technical_implementation="Fix",
                    implementation_complexity=RiskLevel.LOW
                )
            )
        assert "EDGE-" in str(exc_info.value)

    def test_auditor_response_schema(self, sample_auditor_response, schema_validator):
        """Test that sample auditor response is valid StressTestReport."""
        result = schema_validator(sample_auditor_response, StressTestReport)
        assert result['valid'] is True, f"Schema validation failed: {result['errors']}"
        assert len(result['data']['edge_cases']) >= 5
        assert result['data']['resilience_score'] >= 0
        assert result['data']['resilience_score'] <= 100

    def test_stress_test_report_min_edge_cases(self):
        """Test that StressTestReport requires at least 5 edge cases."""
        # Only 3 edge cases - should fail validation
        with pytest.raises(Exception) as exc_info:
            StressTestReport(
                report_id="TEST-001",
                happy_path_id="HP-001",
                feature_name="Test Feature",
                edge_cases=[
                    EdgeCase(
                        scenario_id=f"EDGE-00{i}",
                        description=f"Edge case {i}",
                        trigger_condition="Test",
                        expected_failure="Fail",
                        severity=RiskLevel.LOW,
                        likelihood=RiskLevel.LOW,
                        mitigation=MitigationStrategy(
                            description="Fix",
                            technical_implementation="Fix",
                            implementation_complexity=RiskLevel.LOW
                        )
                    ) for i in range(1, 4)  # Only 3 edge cases
                ],
                resilience_score=50,
                coverage_score=50,
                review_summary="Test"
            )
        assert "5" in str(exc_info.value) or "edge" in str(exc_info.value).lower()


class TestAgentCommentSchema:
    """Test AgentComment schema validation."""

    def test_valid_agent_comment(self):
        """Test valid AgentComment creation."""
        comment = AgentComment(
            comment_id="COMMENT-001",
            agent_id=AgentPerspective.WHITE_HAT,
            target_id="FEATURE-001",
            focus_area="Performance",
            content="Consider using caching",
            suggestion="Add Redis cache",
            priority=4,
            confidence=0.85,
            references=["STEP-1"],
            tags=["performance", "optimization"]
        )
        assert comment.agent_id == AgentPerspective.WHITE_HAT
        assert comment.priority == 4
        assert comment.confidence == 0.85

    def test_agent_comment_priority_validation(self):
        """Test that priority must be between 1 and 5."""
        with pytest.raises(Exception):
            AgentComment(
                comment_id="COMMENT-001",
                agent_id=AgentPerspective.BLACK_HAT,
                target_id="TEST",
                focus_area="Security",
                content="Test",
                priority=6,  # Invalid: must be 1-5
                confidence=0.5
            )

    def test_agent_comment_confidence_validation(self):
        """Test that confidence must be between 0.0 and 1.0."""
        with pytest.raises(Exception):
            AgentComment(
                comment_id="COMMENT-001",
                agent_id=AgentPerspective.GREEN_HAT,
                target_id="TEST",
                focus_area="Decision",
                content="Test",
                priority=3,
                confidence=1.5  # Invalid: must be 0.0-1.0
            )


class TestQualityGateSchema:
    """Test QualityGateReport schema validation."""

    def test_valid_quality_gate_report(self):
        """Test valid QualityGateReport creation."""
        report = QualityGateReport(
            report_id="QG-001",
            target_id="DOC-001",
            overall_maturity_score=85,
            depth_score=80,
            completeness_score=90,
            metrics=[
                MaturityMetric(
                    metric_name="Completeness",
                    score=90,
                    description="Coverage of required sections",
                    threshold=70,
                    passed=True
                ),
                MaturityMetric(
                    metric_name="Depth",
                    score=80,
                    description="Technical detail depth",
                    threshold=65,
                    passed=True
                )
            ],
            passed=True,
            required_improvements=[],
            suggested_improvements=["Add more examples"]
        )
        assert report.overall_maturity_score == 85
        assert report.passed is True
        assert len(report.metrics) == 2

    def test_quality_gate_maturity_threshold(self):
        """Test that overall_maturity_score must be at least 70."""
        with pytest.raises(Exception) as exc_info:
            QualityGateReport(
                report_id="QG-001",
                target_id="DOC-001",
                overall_maturity_score=65,  # Invalid: must be >= 70
                depth_score=70,
                completeness_score=70,
                metrics=[],
                passed=False,
                required_improvements=["Improve completeness"],
                suggested_improvements=[]
            )
        assert "70" in str(exc_info.value) or "maturity" in str(exc_info.value).lower()


class TestConsensusDecisionSchema:
    """Test ConsensusDecision schema validation."""

    def test_valid_consensus_decision(self, sample_cto_response, schema_validator):
        """Test that sample CTO response is valid ConsensusDecision."""
        result = schema_validator(sample_cto_response, ConsensusDecision)
        assert result['valid'] is True, f"Schema validation failed: {result['errors']}"
        assert result['data']['decision_id'] == 'DECISION-001'
        assert len(result['data']['participating_agents']) == 3
        assert 0.0 <= result['data']['confidence_score'] <= 1.0

    def test_consensus_decision_confidence_validation(self):
        """Test that confidence_score must be between 0.0 and 1.0."""
        with pytest.raises(Exception):
            ConsensusDecision(
                decision_id="DEC-001",
                topic="Test decision",
                decision="Test",
                reasoning="Test reasoning",
                participating_agents=[AgentPerspective.WHITE_HAT],
                confidence_score=1.5  # Invalid: must be 0.0-1.0
            )


class TestTechnicalDesignDocumentSchema:
    """Test root TechnicalDesignDocument schema validation."""

    def test_minimal_valid_document(self):
        """Test minimal valid TechnicalDesignDocument."""
        doc = TechnicalDesignDocument(
            project_name="Test Project",
            project_description="Test Description",
            author="Test Author",
            system_architecture=SystemArchitecture(
                components=[
                    SystemComponent(
                        id="test",
                        name="Test",
                        type=ComponentType.SERVICE,
                        description="Test"
                    )
                ],
                interactions=[]
            ),
            happy_paths=[
                HappyPath(
                    feature_id="TEST-001",
                    feature_name="Test Feature",
                    description="Test",
                    steps=[
                        FlowStep(
                            step_number=1,
                            actor="User",
                            action="Test",
                            outcome="Success"
                        )
                    ],
                    post_conditions=["Done"],
                    business_value="Test value"
                )
            ],
            stress_test_reports=[
                StressTestReport(
                    report_id="STRESS-001",
                    happy_path_id="TEST-001",
                    feature_name="Test Feature",
                    edge_cases=[
                        EdgeCase(
                            scenario_id=f"EDGE-00{i}",
                            description=f"Edge {i}",
                            trigger_condition="Test",
                            expected_failure="Fail",
                            severity=RiskLevel.LOW,
                            likelihood=RiskLevel.LOW,
                            mitigation=MitigationStrategy(
                                description="Fix",
                                technical_implementation="Fix",
                                implementation_complexity=RiskLevel.LOW
                            )
                        ) for i in range(1, 6)  # 5 edge cases
                    ],
                    resilience_score=70,
                    coverage_score=70,
                    review_summary="Test review"
                )
            ],
            agent_comments=[
                AgentComment(
                    comment_id="COMMENT-001",
                    agent_id=AgentPerspective.WHITE_HAT,
                    target_id="TEST-001",
                    focus_area="Test",
                    content="Test comment",
                    priority=3,
                    confidence=0.8
                )
            ],
            quality_gate_report=QualityGateReport(
                report_id="QG-001",
                target_id="DOC-001",
                overall_maturity_score=75,
                depth_score=75,
                completeness_score=75,
                metrics=[
                    MaturityMetric(
                        metric_name="Test",
                        score=75,
                        description="Test",
                        threshold=70,
                        passed=True
                    )
                ],
                passed=True
            )
        )
        assert doc.project_name == "Test Project"
        assert len(doc.happy_paths) >= 1
        assert len(doc.stress_test_reports) >= 1

    def test_document_requires_happy_paths(self):
        """Test that document requires at least one happy path."""
        with pytest.raises(Exception) as exc_info:
            TechnicalDesignDocument(
                project_name="Test",
                project_description="Test",
                author="Test",
                system_architecture=SystemArchitecture(components=[], interactions=[]),
                happy_paths=[],  # Invalid: must have at least 1
                post_conditions=[],  # This is in wrong place
                stress_test_reports=[
                    StressTestReport(
                        report_id="STRESS-001",
                        happy_path_id="TEST-001",
                        feature_name="Test",
                        edge_cases=[
                            EdgeCase(
                                scenario_id=f"EDGE-00{i}",
                                description=f"Edge {i}",
                                trigger_condition="Test",
                                expected_failure="Fail",
                                severity=RiskLevel.LOW,
                                likelihood=RiskLevel.LOW,
                                mitigation=MitigationStrategy(
                                    description="Fix",
                                    technical_implementation="Fix",
                                    implementation_complexity=RiskLevel.LOW
                                )
                            ) for i in range(1, 6)
                        ],
                        resilience_score=70,
                        coverage_score=70,
                        review_summary="Test"
                    )
                ],
                agent_comments=[],
                consensus_decisions=[],
                quality_gate_report=QualityGateReport(
                    report_id="QG-001",
                    target_id="DOC-001",
                    overall_maturity_score=75,
                    depth_score=75,
                    completeness_score=75,
                    metrics=[],
                    passed=True
                )
            )
        # Should fail validation
        assert "happy" in str(exc_info.value).lower() or "path" in str(exc_info.value).lower()


class TestSchemaComplianceHelper:
    """Test the schema_validator helper function."""

    def test_valid_json_with_schema(self, sample_architect_response, schema_validator):
        """Test schema_validator with valid input."""
        result = schema_validator(sample_architect_response, HappyPath)
        assert result['valid'] is True
        assert result['data'] is not None
        assert len(result['errors']) == 0

    def test_invalid_json(self, schema_validator):
        """Test schema_validator with invalid JSON."""
        result = schema_validator("not a json", HappyPath)
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert "json" in result['errors'][0].lower()

    def test_valid_json_invalid_schema(self, schema_validator):
        """Test schema_validator with valid JSON but invalid schema data."""
        invalid_schema_data = json.dumps({
            "feature_id": "TEST-001",
            # Missing required fields
        })
        result = schema_validator(invalid_schema_data, HappyPath)
        assert result['valid'] is False
        assert len(result['errors']) > 0
