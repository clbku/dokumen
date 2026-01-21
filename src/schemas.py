from enum import Enum
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime, timezone

# --- Core Primitives ---

class ComponentType(str, Enum):
    SERVICE = "Service"
    DATABASE = "Database"
    QUEUE = "Queue"
    CLIENT = "Client"
    EXTERNAL_API = "ExternalAPI"
    CACHE = "Cache"
    LOAD_BALANCER = "LoadBalancer"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class Protocol(str, Enum):
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    GRPC = "GRPC"
    WEBSOCKET = "WebSocket"
    AMQP = "AMQP"
    TCP = "TCP"

# --- Architecture & Design ---

class Interaction(BaseModel):
    source: str = Field(..., description="ID or name of the source component")
    target: str = Field(..., description="ID or name of the target component")
    protocol: Protocol = Field(..., description="Communication protocol used")
    description: str = Field(..., description="Brief description of the interaction")
    is_synchronous: bool = Field(True, description="Whether the interaction is synchronous")

class SystemComponent(BaseModel):
    id: str = Field(..., description="Unique identifier for the component")
    name: str = Field(..., description="Human-readable name")
    type: ComponentType = Field(..., description="Type of the component")
    description: str = Field(..., description="Purpose of the component")
    technologies: List[str] = Field(default_factory=list, description="List of technologies used (e.g., 'Python', 'PostgreSQL')")
    is_critical: bool = Field(False, description="Whether this component is critical for system operation")

class SystemArchitecture(BaseModel):
    components: List[SystemComponent] = Field(..., description="List of all components in the system")
    interactions: List[Interaction] = Field(..., description="List of interactions between components")

class SystemDiagram(BaseModel):
    """Schema cho Mermaid.js diagrams - Interactive System Diagram feature"""
    diagram_type: Literal["sequence", "flowchart", "state", "er"] = Field(
        ..., description="Type of Mermaid diagram"
    )
    mermaid_code: str = Field(..., description="Valid Mermaid.js syntax code")
    title: str = Field(..., description="Human-readable title for the diagram")
    description: str = Field(..., description="What this diagram represents")
    related_feature: Optional[str] = Field(None, description="Feature ID this diagram illustrates")
    related_components: List[str] = Field(default_factory=list, description="Component IDs shown in diagram")

    @field_validator('mermaid_code')
    @classmethod
    def validate_mermaid_syntax(cls, v: str) -> str:
        """Basic validation to ensure Mermaid code starts correctly"""
        valid_prefixes = ['sequenceDiagram', 'flowchart', 'stateDiagram', 'erDiagram']
        if not any(v.strip().startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(f"Mermaid code must start with one of: {valid_prefixes}")
        return v

# --- Business Logic & Flows ---

class FlowStep(BaseModel):
    step_number: int = Field(..., description="Sequence number of the step", ge=1)
    actor: str = Field(..., description="Who is performing the action (User, System, External)")
    action: str = Field(..., description="The action being performed")
    outcome: str = Field(..., description="The expected result of the action")
    involved_components: List[str] = Field(default_factory=list, description="IDs of components involved in this step")

    # Error handling fields
    error_scenario: Optional[str] = Field(None, description="What happens if this step fails")
    fallback_step: Optional[int] = Field(None, description="Step number to execute on failure", ge=1)
    is_critical: bool = Field(False, description="Whether this step is critical for success")
    retry_count: Optional[int] = Field(None, description="Number of retries before giving up", ge=0)

class HappyPath(BaseModel):
    feature_id: str = Field(..., description="Unique identifier for this feature")
    feature_name: str = Field(..., description="Name of the feature")
    description: str = Field(..., description="Brief description of what this feature does")
    steps: List[FlowStep] = Field(..., description="Sequence of steps in the happy path")
    pre_conditions: List[str] = Field(default_factory=list, description="Required state before execution")
    post_conditions: List[str] = Field(..., description="State of the system after success")
    business_value: str = Field(..., description="Business value this feature provides")

# --- Stress Testing & Edge Cases ---

class MitigationStrategy(BaseModel):
    description: str = Field(..., description="How to mitigate this risk")
    technical_implementation: str = Field(..., description="Specific technical details (e.g., 'Use idempotency keys')")
    implementation_complexity: RiskLevel = Field(..., description="How complex to implement")
    estimated_effort: Optional[str] = Field(None, description="Estimated effort (e.g., '2 days', '1 sprint')")

class EdgeCase(BaseModel):
    scenario_id: str = Field(..., description="Unique ID for the edge case")
    description: str = Field(..., description="Description of the failure scenario")
    trigger_condition: str = Field(..., description="What triggers this edge case (e.g., 'Network timeout after 5s')")
    expected_failure: str = Field(..., description="How the system would fail without mitigation")

    # Impact assessment
    severity: RiskLevel = Field(..., description="Impact of this failure")
    likelihood: RiskLevel = Field(..., description="How likely this is to occur")

    # Detection and mitigation
    detection_method: Optional[str] = Field(None, description="How to detect this edge case in testing/production")
    related_components: List[str] = Field(default_factory=list, description="Component IDs affected by this edge case")
    related_step: Optional[int] = Field(None, description="Flow step number this edge case relates to", ge=1)

    mitigation: MitigationStrategy = Field(..., description="Strategy to handle this edge case")

    @field_validator('scenario_id')
    @classmethod
    def validate_scenario_id(cls, v: str) -> str:
        """Ensure scenario ID follows pattern: EDGE-{feature_id}-{number}"""
        if not v.startswith('EDGE-'):
            raise ValueError("Scenario ID must start with 'EDGE-'")
        return v

class StressTestReport(BaseModel):
    report_id: str = Field(..., description="Unique identifier for this report")
    happy_path_id: str = Field(..., description="ID of the happy path being tested")
    feature_name: str = Field(..., description="Name of the feature being tested")

    # Edge cases analysis
    edge_cases: List[EdgeCase] = Field(..., description="List of identified edge cases", min_length=5)

    # Quality metrics
    resilience_score: int = Field(..., ge=0, le=100, description="Estimated resilience score (0-100)")
    coverage_score: int = Field(..., ge=0, le=100, description="Edge case coverage percentage")

    # Assessment
    review_summary: str = Field(..., description="Overall assessment of the design's robustness")
    critical_findings: List[str] = Field(default_factory=list, description="Critical issues that must be addressed")
    recommendations: List[str] = Field(default_factory=list, description="General recommendations")

    @field_validator('edge_cases')
    @classmethod
    def validate_min_edge_cases(cls, v: List[EdgeCase]) -> List[EdgeCase]:
        """Ensure at least 5 edge cases are identified per feature"""
        if len(v) < 5:
            raise ValueError("At least 5 edge cases must be identified for each feature")
        return v

# --- Multi-Agent Debate ---

class AgentPerspective(str, Enum):
    WHITE_HAT = "WhiteHat"  # Architect/Builder - Optimistic, focuses on building
    BLACK_HAT = "BlackHat"  # Saboteur/Hacker - Pessimistic, focuses on breaking
    GREEN_HAT = "GreenHat"  # Creative/Improver - Innovative, focuses on alternatives

class AgentComment(BaseModel):
    comment_id: str = Field(..., description="Unique identifier for this comment")
    agent_id: AgentPerspective = Field(..., description="Role of the agent giving feedback")
    target_id: str = Field(..., description="ID of the element being commented on (feature, component, etc.)")

    # Content
    focus_area: str = Field(..., description="Topic of the comment (e.g., 'Security', 'Scalability', 'Performance')")
    content: str = Field(..., description="The feedback content - must be specific and actionable")
    suggestion: Optional[str] = Field(None, description="Proposed improvement or alternative")

    # Priority and confidence
    priority: int = Field(..., ge=1, le=5, description="Priority level (1=low, 5=critical)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Agent's confidence in this comment")

    # References
    references: List[str] = Field(default_factory=list, description="Related edge case IDs, component IDs, or step numbers")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization (e.g., 'security', 'performance')")

class ConsensusDecision(BaseModel):
    decision_id: str = Field(..., description="Unique identifier for this decision")
    topic: str = Field(..., description="What was debated")
    target_id: Optional[str] = Field(None, description="ID of the element this decision relates to")

    # Decision details
    decision: str = Field(..., description="Final decision made")
    reasoning: str = Field(..., description="Why this decision was reached")

    # Debate process
    dissenting_opinions: List[str] = Field(default_factory=list, description="Key points that were overruled")
    participating_agents: List[AgentPerspective] = Field(..., description="Agents involved in this debate")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in this decision")

    # Impact
    impact_area: List[str] = Field(default_factory=list, description="Areas this decision affects")

# --- Quality Gates ---

class MaturityMetric(BaseModel):
    metric_name: str = Field(..., description="Name of the metric")
    score: int = Field(..., ge=0, le=100, description="Score for this metric")
    description: str = Field(..., description="What this metric measures")
    threshold: int = Field(..., ge=0, le=100, description="Minimum score to pass")
    passed: bool = Field(..., description="Whether this metric passed the threshold")
    notes: Optional[str] = Field(None, description="Additional notes on this metric")

class QualityGateReport(BaseModel):
    report_id: str = Field(..., description="Unique identifier for this quality gate report")
    target_id: str = Field(..., description="ID of the element being evaluated (feature or document)")

    # Overall scores
    overall_maturity_score: int = Field(..., ge=0, le=100, description="Overall document quality score")
    depth_score: int = Field(..., ge=0, le=100, description="Depth of technical detail")
    completeness_score: int = Field(..., ge=0, le=100, description="Coverage of all scenarios")

    # Individual metrics
    metrics: List[MaturityMetric] = Field(..., description="Detailed breakdown of scores")

    # Final verdict
    passed: bool = Field(..., description="Whether the document passed quality gates")
    required_improvements: List[str] = Field(default_factory=list, description="Must-fix issues before publication")
    suggested_improvements: List[str] = Field(default_factory=list, description="Nice-to-have improvements")

    @field_validator('overall_maturity_score')
    @classmethod
    def validate_maturity_threshold(cls, v: int) -> int:
        """Ensure minimum maturity score threshold"""
        if v < 70:
            raise ValueError("Overall maturity score must be at least 70 to pass quality gate")
        return v

# --- Root Document ---

class TechnicalDesignDocument(BaseModel):
    """
    Root schema for the entire technical design document.
    This is the main output structure that combines all other schemas.
    """
    # Metadata
    project_name: str = Field(..., description="Name of the project")
    project_description: str = Field(..., description="Brief description of the project")
    version: str = Field(default="1.0", description="Document version")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO timestamp of creation")
    author: str = Field(..., description="Author or team responsible for this document")

    # Architecture
    system_architecture: SystemArchitecture = Field(..., description="High-level system design")
    system_diagrams: List[SystemDiagram] = Field(default_factory=list, description="Interactive system diagrams")

    # Business Logic
    happy_paths: List[HappyPath] = Field(..., description="All happy path flows", min_length=1)

    # Stress Testing
    stress_test_reports: List[StressTestReport] = Field(..., description="Stress test for each feature", min_length=1)

    # Agent Debates
    agent_comments: List[AgentComment] = Field(..., description="Feedback from multi-agent debate")
    consensus_decisions: List[ConsensusDecision] = Field(default_factory=list, description="Final decisions from debates")

    # Quality Gates
    quality_gate_report: QualityGateReport = Field(..., description="Final quality assessment")

    @field_validator('happy_paths')
    @classmethod
    def validate_happy_paths(cls, v: List[HappyPath]) -> List[HappyPath]:
        """Ensure at least one happy path is defined"""
        if not v:
            raise ValueError("At least one happy path must be defined")
        return v

    @field_validator('stress_test_reports')
    @classmethod
    def validate_stress_test_coverage(cls, v: List[StressTestReport]) -> List[StressTestReport]:
        """Ensure stress test reports cover all happy paths"""
        if not v:
            raise ValueError("At least one stress test report must be provided")
        return v


# --- Helper Functions for Documentation ---

def get_schema_example(schema_class: type) -> Dict:
    """
    Returns a JSON-serializable example for documentation purposes.
    Useful for showing AI agents the expected output format.
    """
    if schema_class == TechnicalDesignDocument:
        return {
            "project_name": "E-commerce Platform",
            "project_description": "A scalable e-commerce platform with payment processing",
            "version": "1.0",
            "author": "Deep-Spec AI",
            "system_architecture": {
                "components": [
                    {
                        "id": "api-gateway",
                        "name": "API Gateway",
                        "type": "Service",
                        "description": "Entry point for all client requests",
                        "technologies": ["Kong", "Lua"],
                        "is_critical": True
                    }
                ],
                "interactions": []
            },
            "happy_paths": [],
            "stress_test_reports": [],
            "agent_comments": [],
            "quality_gate_report": {}
        }
    return {}
