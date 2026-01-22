"""
Tests for Hierarchical Validator

Tests the validation logic for hierarchical workflow results following TDD approach.
"""

from src.schemas import HappyPath, StressTestReport, FlowStep, EdgeCase, MitigationStrategy, RiskLevel


class TestHierarchicalValidator:
    """Test suite for HierarchicalValidator."""

    def test_validate_hierarchical_result_pass(self):
        """
        Test that validation passes with valid input.

        This test creates valid HappyPath and StressTestReport objects
        that meet all minimum requirements and expects validation to pass.
        """
        # Create valid happy path with minimum 3 steps
        happy_path = HappyPath(
            feature_id="FEATURE-001",
            feature_name="User Registration",
            description="Allow users to register for an account",
            steps=[
                FlowStep(
                    step_number=1,
                    actor="User",
                    action="Submit registration form",
                    outcome="Form data is validated",
                    involved_components=["api-gateway", "auth-service"],
                ),
                FlowStep(
                    step_number=2,
                    actor="System",
                    action="Validate email uniqueness",
                    outcome="Email is confirmed unique",
                    involved_components=["auth-service", "database"],
                ),
                FlowStep(
                    step_number=3,
                    actor="System",
                    action="Create user account",
                    outcome="Account is created successfully",
                    involved_components=["database"],
                ),
            ],
            post_conditions=["User account exists in database", "User is logged in"],
            business_value="Enables user access to platform features",
        )

        # Create valid stress test report with minimum 5 edge cases
        # Use business-focused edge cases without technical keywords
        business_edge_cases = [
            EdgeCase(
                scenario_id="EDGE-001-1",
                description="Email already registered",
                trigger_condition="User submits existing email address",
                expected_failure="Registration rejected with error",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.HIGH,
                mitigation=MitigationStrategy(
                    description="Show clear error message with login link",
                    technical_implementation="Check uniqueness and return error",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-001-2",
                description="Invalid email format",
                trigger_condition="User submits malformed email address",
                expected_failure="Form validation fails",
                severity=RiskLevel.LOW,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Validate email format on client and server",
                    technical_implementation="Use email validation library",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-001-3",
                description="Weak password provided",
                trigger_condition="User enters simple password",
                expected_failure="Password rejected",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Show password requirements and strength meter",
                    technical_implementation="Enforce complexity rules",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-001-4",
                description="User under minimum age",
                trigger_condition="Birthdate indicates user is too young",
                expected_failure="Registration blocked",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Show age requirement notice",
                    technical_implementation="Validate age during registration",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-001-5",
                description="Terms and conditions not accepted",
                trigger_condition="User forgets to check agreement box",
                expected_failure="Submit button disabled or error shown",
                severity=RiskLevel.LOW,
                likelihood=RiskLevel.HIGH,
                mitigation=MitigationStrategy(
                    description="Make terms checkbox required",
                    technical_implementation="Form validation before submit",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
        ]

        business_exceptions = StressTestReport(
            report_id="REPORT-001-BUSINESS",
            happy_path_id="FEATURE-001",
            feature_name="User Registration",
            edge_cases=business_edge_cases,  # Business edge cases
            resilience_score=85,
            coverage_score=90,
            review_summary="Good coverage of business edge cases",
        )

        # Create 5 additional edge cases for technical
        technical_edge_cases_list = [
            EdgeCase(
                scenario_id="EDGE-001-6",
                description="Memory leak in session handling",
                trigger_condition="Long-running sessions",
                expected_failure="Server out of memory",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Implement session cleanup",
                    technical_implementation="Scheduled session expiration",
                    implementation_complexity=RiskLevel.MEDIUM,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-001-7",
                description="SSL certificate expired",
                trigger_condition="Certificate not renewed",
                expected_failure="Connection refused",
                severity=RiskLevel.CRITICAL,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Automated renewal",
                    technical_implementation="Let's Encrypt integration",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-001-8",
                description="DNS resolution failure",
                trigger_condition="DNS server unavailable",
                expected_failure="Service unreachable",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="DNS caching and fallback",
                    technical_implementation="Multiple DNS servers",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-001-9",
                description="File system full",
                trigger_condition="Log files grow too large",
                expected_failure="Service crash",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Log rotation",
                    technical_implementation="Automated log cleanup",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-001-10",
                description="Cache stampede",
                trigger_condition="Cache expires under high load",
                expected_failure="Database overload",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Cache locking",
                    technical_implementation="Implement cache stampede protection",
                    implementation_complexity=RiskLevel.MEDIUM,
                ),
            ),
        ]

        technical_edge_cases = StressTestReport(
            report_id="REPORT-001-TECHNICAL",
            happy_path_id="FEATURE-001",
            feature_name="User Registration",
            edge_cases=technical_edge_cases_list,  # Technical edge cases
            resilience_score=80,
            coverage_score=85,
            review_summary="Good coverage of technical edge cases",
        )

        # Import validator here to follow TDD
        from src.validation.hierarchical_validator import HierarchicalValidator

        validator = HierarchicalValidator()
        result = validator.validate_hierarchical_result(
            happy_path=happy_path,
            business_exceptions=business_exceptions,
            technical_edge_cases=technical_edge_cases,
        )

        # Assert validation passes
        assert result["passed"] is True
        assert result["happy_path_valid"] is True
        assert result["business_exceptions_valid"] is True
        assert result["technical_edge_cases_valid"] is True
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_validate_hierarchical_result_fail_not_enough_steps(self):
        """
        Test that validation fails with insufficient happy path steps.

        This test creates a HappyPath with fewer than 3 steps
        and expects validation to fail with appropriate error.
        """
        # Create invalid happy path with only 2 steps (less than minimum 3)
        happy_path = HappyPath(
            feature_id="FEATURE-002",
            feature_name="Simple Login",
            description="Allow users to login",
            steps=[
                FlowStep(
                    step_number=1,
                    actor="User",
                    action="Submit credentials",
                    outcome="Credentials validated",
                ),
                FlowStep(
                    step_number=2,
                    actor="System",
                    action="Create session",
                    outcome="User logged in",
                ),
            ],
            post_conditions=["User is authenticated"],
            business_value="Provides access to user account",
        )

        # Create valid stress test reports with business edge cases (no technical keywords)
        business_edge_cases = [
            EdgeCase(
                scenario_id="EDGE-002-1",
                description="Invalid credentials submitted",
                trigger_condition="User enters wrong username or password",
                expected_failure="Login denied with error message",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.HIGH,
                mitigation=MitigationStrategy(
                    description="Show generic error for security",
                    technical_implementation="Check credentials and return error",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-002-2",
                description="Account temporarily locked",
                trigger_condition="Too many failed login attempts",
                expected_failure="Login blocked with lock notice",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Show lock duration and reset option",
                    technical_implementation="Track failed attempts and enforce lockout",
                    implementation_complexity=RiskLevel.MEDIUM,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-002-3",
                description="Account not verified",
                trigger_condition="User hasn't verified email",
                expected_failure="Login blocked with resend option",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Prompt to resend verification email",
                    technical_implementation="Check verification status",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-002-4",
                description="Account disabled by admin",
                trigger_condition="Admin disabled user account",
                expected_failure="Login blocked with contact info",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Show support contact information",
                    technical_implementation="Check account status",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-002-5",
                description="Password expired",
                trigger_condition="User password too old",
                expected_failure="Login blocked with reset prompt",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Require password reset",
                    technical_implementation="Check password age",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
        ]

        business_exceptions = StressTestReport(
            report_id="REPORT-002-BUSINESS",
            happy_path_id="FEATURE-002",
            feature_name="Simple Login",
            edge_cases=business_edge_cases,  # All 5 edge cases
            resilience_score=75,
            coverage_score=80,
            review_summary="Business edge cases covered",
        )

        # Create 5 additional technical edge cases
        technical_edge_cases_list = [
            EdgeCase(
                scenario_id="EDGE-002-6",
                description="Session token too large",
                trigger_condition="Too much data in token",
                expected_failure="Cookie size exceeded",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Use reference tokens",
                    technical_implementation="Store session data server-side",
                    implementation_complexity=RiskLevel.MEDIUM,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-002-7",
                description="Connection pool exhausted",
                trigger_condition="High concurrent requests",
                expected_failure="Request timeout",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Increase pool size",
                    technical_implementation="Configure connection pool",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-002-8",
                description="Message queue backlog",
                trigger_condition="Slow message processing",
                expected_failure="Delayed login",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Scale workers",
                    technical_implementation="Auto-scaling consumer group",
                    implementation_complexity=RiskLevel.MEDIUM,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-002-9",
                description="Cache server failure",
                trigger_condition="Redis server down",
                expected_failure="Degraded performance",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Cache fallback",
                    technical_implementation="Direct database query on cache miss",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-002-10",
                description="Load balancer misconfiguration",
                trigger_condition="Invalid routing rules",
                expected_failure="Requests to wrong server",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Configuration validation",
                    technical_implementation="Automated config testing",
                    implementation_complexity=RiskLevel.MEDIUM,
                ),
            ),
        ]

        technical_edge_cases = StressTestReport(
            report_id="REPORT-002-TECHNICAL",
            happy_path_id="FEATURE-002",
            feature_name="Simple Login",
            edge_cases=technical_edge_cases_list,
            resilience_score=70,
            coverage_score=75,
            review_summary="Technical edge cases covered",
        )

        # Import validator
        from src.validation.hierarchical_validator import HierarchicalValidator

        validator = HierarchicalValidator()
        result = validator.validate_hierarchical_result(
            happy_path=happy_path,
            business_exceptions=business_exceptions,
            technical_edge_cases=technical_edge_cases,
        )

        # Assert validation fails
        assert result["passed"] is False
        assert result["happy_path_valid"] is False
        assert "at least 3 steps" in result["errors"][0].lower()

    def test_validate_hierarchical_result_fail_low_scores(self):
        """
        Test that validation fails with low quality scores.

        This test creates reports with scores below 70 threshold
        and expects validation to fail.
        """
        # Create valid happy path
        happy_path = HappyPath(
            feature_id="FEATURE-003",
            feature_name="Feature X",
            description="Test feature",
            steps=[
                FlowStep(step_number=1, actor="User", action="Action 1", outcome="Result 1"),
                FlowStep(step_number=2, actor="System", action="Action 2", outcome="Result 2"),
                FlowStep(step_number=3, actor="User", action="Action 3", outcome="Result 3"),
            ],
            post_conditions=["Condition met"],
            business_value="Provides value",
        )

        # Create edge cases for business (5 minimum)
        business_edge_cases = [
            EdgeCase(
                scenario_id=f"EDGE-003-BUS-{i}",
                description=f"Business edge case {i}",
                trigger_condition=f"Business trigger {i}",
                expected_failure=f"Business failure {i}",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Mitigation",
                    technical_implementation="Implementation",
                    implementation_complexity=RiskLevel.LOW,
                ),
            )
            for i in range(1, 6)
        ]

        # Create edge cases for technical (5 minimum)
        technical_edge_cases_list = [
            EdgeCase(
                scenario_id=f"EDGE-003-TECH-{i}",
                description=f"Technical edge case {i}",
                trigger_condition=f"Technical trigger {i}",
                expected_failure=f"Technical failure {i}",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Mitigation",
                    technical_implementation="Implementation",
                    implementation_complexity=RiskLevel.LOW,
                ),
            )
            for i in range(1, 6)
        ]

        # Create reports with low scores (below 70)
        business_exceptions = StressTestReport(
            report_id="REPORT-003-BUSINESS",
            happy_path_id="FEATURE-003",
            feature_name="Feature X",
            edge_cases=business_edge_cases,
            resilience_score=65,  # Below 70 threshold
            coverage_score=68,    # Below 70 threshold
            review_summary="Low quality report",
        )

        technical_edge_cases = StressTestReport(
            report_id="REPORT-003-TECHNICAL",
            happy_path_id="FEATURE-003",
            feature_name="Feature X",
            edge_cases=technical_edge_cases_list,
            resilience_score=60,  # Below 70 threshold
            coverage_score=55,    # Below 70 threshold
            review_summary="Low quality technical report",
        )

        # Import validator
        from src.validation.hierarchical_validator import HierarchicalValidator

        validator = HierarchicalValidator()
        result = validator.validate_hierarchical_result(
            happy_path=happy_path,
            business_exceptions=business_exceptions,
            technical_edge_cases=technical_edge_cases,
        )

        # Assert validation fails due to low scores
        assert result["passed"] is False
        assert result["business_exceptions_valid"] is False
        assert result["technical_edge_cases_valid"] is False
        assert any("score" in error.lower() for error in result["errors"])

    def test_validate_technical_keywords_in_business(self):
        """
        Test detection of technical keywords in business edge cases.

        This test creates business edge cases with technical keywords
        and expects warnings to be generated.
        """
        # Create valid happy path
        happy_path = HappyPath(
            feature_id="FEATURE-004",
            feature_name="Payment Processing",
            description="Process payments",
            steps=[
                FlowStep(step_number=1, actor="User", action="Pay", outcome="Payment initiated"),
                FlowStep(step_number=2, actor="System", action="Process", outcome="Payment processed"),
                FlowStep(step_number=3, actor="System", action="Confirm", outcome="Payment confirmed"),
            ],
            post_conditions=["Payment complete"],
            business_value="Enables transactions",
        )

        # Create business edge cases with technical keywords (should generate warning)
        # Need 5 edge cases minimum for Pydantic
        business_edge_cases = [
            EdgeCase(
                scenario_id="EDGE-004-1",
                description="Database connection fails during payment",
                trigger_condition="Network timeout to database",
                expected_failure="Payment processing fails",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Retry connection",
                    technical_implementation="Connection pool with retry",
                    implementation_complexity=RiskLevel.MEDIUM,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-004-2",
                description="Concurrency issue with payment ledger",
                trigger_condition="Race condition in concurrent updates",
                expected_failure="Ledger inconsistency",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.LOW,
                mitigation=MitigationStrategy(
                    description="Use transactions",
                    technical_implementation="Database transaction isolation",
                    implementation_complexity=RiskLevel.MEDIUM,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-004-3",
                description="Payment gateway API timeout",
                trigger_condition="External API slow response",
                expected_failure="Payment gateway unavailable",
                severity=RiskLevel.HIGH,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Implement circuit breaker",
                    technical_implementation="Circuit breaker pattern",
                    implementation_complexity=RiskLevel.MEDIUM,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-004-4",
                description="Insufficient funds",  # Pure business case
                trigger_condition="User balance too low",
                expected_failure="Payment declined",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.HIGH,
                mitigation=MitigationStrategy(
                    description="Show clear error",
                    technical_implementation="Check balance before payment",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
            EdgeCase(
                scenario_id="EDGE-004-5",
                description="Payment method expired",  # Pure business case
                trigger_condition="Card expired",
                expected_failure="Payment rejected",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Prompt for update",
                    technical_implementation="Validate card expiry",
                    implementation_complexity=RiskLevel.LOW,
                ),
            ),
        ]

        # Create technical edge cases (should be separate)
        technical_edge_cases_list = [
            EdgeCase(
                scenario_id=f"EDGE-004-{i}",
                description=f"Technical issue {i}",
                trigger_condition=f"Technical trigger {i}",
                expected_failure=f"Technical failure {i}",
                severity=RiskLevel.MEDIUM,
                likelihood=RiskLevel.MEDIUM,
                mitigation=MitigationStrategy(
                    description="Fix",
                    technical_implementation="Technical fix",
                    implementation_complexity=RiskLevel.LOW,
                ),
            )
            for i in range(6, 11)
        ]

        business_exceptions = StressTestReport(
            report_id="REPORT-004-BUSINESS",
            happy_path_id="FEATURE-004",
            feature_name="Payment Processing",
            edge_cases=business_edge_cases,
            resilience_score=85,
            coverage_score=90,
            review_summary="Good coverage",
        )

        technical_edge_cases = StressTestReport(
            report_id="REPORT-004-TECHNICAL",
            happy_path_id="FEATURE-004",
            feature_name="Payment Processing",
            edge_cases=technical_edge_cases_list,
            resilience_score=85,
            coverage_score=90,
            review_summary="Good technical coverage",
        )

        # Import validator
        from src.validation.hierarchical_validator import HierarchicalValidator

        validator = HierarchicalValidator()
        result = validator.validate_hierarchical_result(
            happy_path=happy_path,
            business_exceptions=business_exceptions,
            technical_edge_cases=technical_edge_cases,
        )

        # Should pass but have warnings about technical keywords in business
        assert result["passed"] is True  # Overall passes
        assert len(result["warnings"]) > 0
        assert any("technical" in warning.lower() for warning in result["warnings"])
