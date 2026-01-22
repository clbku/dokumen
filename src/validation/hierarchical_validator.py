"""
Hierarchical Validator for Workflow Results

Validates the output from hierarchical workflow to ensure quality standards are met.
Implements validation rules for:
- Minimum happy path steps
- Minimum edge cases
- Quality score thresholds
- Detection of technical keywords in business edge cases
- No overlap between business and technical edge cases
"""

from typing import Dict, List, Any, Tuple
from src.schemas import HappyPath, StressTestReport


class HierarchicalValidator:
    """
    Validator for hierarchical workflow results.

    Ensures that workflow outputs meet quality standards:
    - Happy paths have at least 3 steps
    - Stress test reports have at least 5 edge cases total
    - Quality scores are at least 70
    - Technical keywords don't appear in business edge cases
    - No overlap between business and technical edge cases
    """

    # Technical keywords that should NOT appear in business edge cases
    TECHNICAL_KEYWORDS = [
        "database",
        "network",
        "concurrency",
        "timeout",
        "connection",
        "api",
        "race condition",
        "transaction",
        "circuit breaker",
        "pool",
        "latency",
        "throughput",
        "scalability",
        "availability",
        "consistency",
        "replication",
        "sharding",
        "caching",
        "load balancer",
        "microservice",
        "container",
        "deployment",
        "monitoring",
        "logging",
        "authentication",
        "authorization",
        "encryption",
        "ssl",
        "tls",
        "http",
        "https",
        "grpc",
        "websocket",
        "queue",
        "message",
        "event",
        "async",
        "synchronous",
        "blocking",
        "non-blocking",
    ]

    # Minimum thresholds
    MIN_HAPPY_PATH_STEPS = 3
    MIN_EDGE_CASES_PER_REPORT = 5
    MIN_QUALITY_SCORE = 70

    def validate_hierarchical_result(
        self,
        result: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Validate the complete hierarchical workflow result.

        Args:
            result: Dict containing:
                - happy_path: HappyPath object from workflow
                - business_exceptions: StressTestReport for business edge cases
                - technical_edge_cases: StressTestReport for technical edge cases

        Returns:
            Tuple[bool, List[str]]: (is_valid, list of error messages)
                - is_valid: True if all validations pass (warnings don't fail)
                - errors: List of all issues (both errors and warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Extract components from result dict
        happy_path = result["happy_path"]
        business_exceptions = result["business_exceptions"]
        technical_edge_cases = result["technical_edge_cases"]

        # Validate happy path
        happy_path_valid, happy_path_errors = self._validate_happy_path(happy_path)
        errors.extend(happy_path_errors)

        # Validate business exceptions
        business_valid, business_errors, business_warnings = self._validate_stress_report(
            business_exceptions, report_type="business"
        )
        errors.extend(business_errors)
        warnings.extend(business_warnings)

        # Validate technical edge cases
        technical_valid, technical_errors, technical_warnings = self._validate_stress_report(
            technical_edge_cases, report_type="technical"
        )
        errors.extend(technical_errors)
        warnings.extend(technical_warnings)

        # Check for overlap between business and technical
        overlap_warnings = self._validate_no_overlap(
            business_exceptions.edge_cases, technical_edge_cases.edge_cases
        )
        warnings.extend(overlap_warnings)

        # Combine errors and warnings for the return value
        # The spec expects all issues in the errors list
        all_issues = errors + warnings

        # Overall validation passes if all components pass
        # Warnings don't cause validation to fail
        is_valid = happy_path_valid and business_valid and technical_valid

        return (is_valid, all_issues)

    def _validate_happy_path(self, happy_path: HappyPath) -> Tuple[bool, List[str]]:
        """
        Validate happy path meets minimum requirements.

        Args:
            happy_path: HappyPath object to validate

        Returns:
            Tuple[bool, List[str]]: (is_valid, list of errors)
        """
        errors: List[str] = []

        # Check minimum steps
        if len(happy_path.steps) < self.MIN_HAPPY_PATH_STEPS:
            errors.append(
                f"Happy path must have at least {self.MIN_HAPPY_PATH_STEPS} steps, "
                f"got {len(happy_path.steps)}"
            )

        return (len(errors) == 0, errors)

    def _validate_stress_report(
        self, report: StressTestReport, report_type: str = "general"
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate stress test report meets minimum requirements.

        Args:
            report: StressTestReport object to validate
            report_type: Type of report ("business" or "technical")

        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Check minimum edge cases (note: Pydantic already validates min 5)
        if len(report.edge_cases) < self.MIN_EDGE_CASES_PER_REPORT:
            errors.append(
                f"{report_type.capitalize()} report must have at least "
                f"{self.MIN_EDGE_CASES_PER_REPORT} edge cases, got {len(report.edge_cases)}"
            )

        # Check quality scores
        if report.resilience_score < self.MIN_QUALITY_SCORE:
            errors.append(
                f"{report_type.capitalize()} report resilience score "
                f"({report.resilience_score}) is below minimum threshold "
                f"({self.MIN_QUALITY_SCORE})"
            )

        if report.coverage_score < self.MIN_QUALITY_SCORE:
            errors.append(
                f"{report_type.capitalize()} report coverage score "
                f"({report.coverage_score}) is below minimum threshold "
                f"({self.MIN_QUALITY_SCORE})"
            )

        # Check for technical keywords in business edge cases
        if report_type == "business":
            technical_keywords_found = self._check_technical_keywords(report.edge_cases)
            if technical_keywords_found:
                warnings.append(
                    f"Business edge cases contain technical keywords: "
                    f"{', '.join(technical_keywords_found)}. "
                    f"These should be in technical edge cases instead."
                )

        return (len(errors) == 0, errors, warnings)

    def _check_technical_keywords(self, edge_cases: List) -> List[str]:
        """
        Check if edge cases contain technical keywords.

        Args:
            edge_cases: List of EdgeCase objects

        Returns:
            List[str]: List of technical keywords found
        """
        keywords_found: List[str] = []

        for edge_case in edge_cases:
            # Check description and trigger condition for technical keywords
            text_to_check = (
                edge_case.description.lower() + " " + edge_case.trigger_condition.lower()
            )

            for keyword in self.TECHNICAL_KEYWORDS:
                if keyword.lower() in text_to_check and keyword not in keywords_found:
                    keywords_found.append(keyword)

        return keywords_found

    def _validate_no_overlap(
        self, business_cases: List, technical_cases: List
    ) -> List[str]:
        """
        Check for overlap between business and technical edge cases.

        Overlap is detected when similar scenarios appear in both lists.
        This is a simple heuristic check based on description similarity.

        Args:
            business_cases: List of business EdgeCase objects
            technical_cases: List of technical EdgeCase objects

        Returns:
            List[str]: List of warnings about overlaps
        """
        warnings: List[str] = []

        # Extract descriptions from business cases
        business_descriptions = [case.description.lower() for case in business_cases]

        # Check each technical case against business cases
        for tech_case in technical_cases:
            tech_desc = tech_case.description.lower()

            # Simple overlap detection: check if any significant words match
            tech_words = set(tech_desc.split())
            for biz_desc in business_descriptions:
                biz_words = set(biz_desc.split())

                # Calculate overlap (intersection of words)
                overlap = tech_words & biz_words

                # If more than 3 words overlap, flag it
                if len(overlap) > 3:
                    warnings.append(
                        f"Possible overlap detected: Technical case '{tech_case.description}' "
                        f"shares significant words with business case '{biz_desc}'. "
                        f"Consider consolidating or clarifying the distinction."
                    )
                    break  # Only warn once per technical case

        return warnings


__all__ = ["HierarchicalValidator"]
