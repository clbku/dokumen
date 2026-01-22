"""
Export function cho Phase 4 với Quality Gate enforcement.

Xuất bản SDD với Quality Gate validation, auto-retry, và badge injection.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Literal

from src.quality import QualityGateReport


class QualityGateError(Exception):
    """Raised khi document fails Quality Gate."""
    pass


def export_sdd(
    aggregated_data: Dict[str, Any],
    template: str,
    output_path: str = "./output",
    format: Literal["md", "json"] = "md",
    enforce_quality_gate: bool = True,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """
    Xuất bản System Design Document với Quality Gate validation.

    Args:
        aggregated_data: Dữ liệu từ Phase 3
        template: Markdown template
        output_path: Đường dẫn output
        format: "md" hoặc "json"
        enforce_quality_gate: ⚠️ CRITICAL - PHẢI pass QG mới xuất
        max_retries: Số lần retry khi fail QG

    Returns:
        dict: {"file_path": str, "quality_report": QualityGateReport, "passed": bool}

    Raises:
        QualityGateError: Khi fail QG sau max_retries
    """
    # Validate input
    if not aggregated_data.get("feature_name"):
        raise ValueError("Missing required field: feature_name")

    # Mock content - thực tế sẽ từ Debate Orchestrator
    mock_content = template.format(**aggregated_data)

    # Quality Gate Check
    for retry in range(max_retries):
        # Mock extracted data
        extracted = {
            "happy_path": aggregated_data.get("happy_path", []),
            "edge_cases": aggregated_data.get("edge_cases", []),
            "tech_stack": aggregated_data.get("tech_stack", {}),
        }

        # TODO: Replace with actual validate_quality_gate call
        from src.quality import validate_quality_gate
        quality_report = validate_quality_gate(mock_content, extracted)

        if quality_report.passed_quality_gate:
            break
        elif not enforce_quality_gate:
            print(f"⚠️ WARNING: Document FAILED Quality Gate but export enforced")
            print(f"Failures: {quality_report.failure_reasons}")
            break
        else:
            print(f"❌ Quality Gate FAILED (attempt {retry + 1}/{max_retries})")
            print(f"Failures: {quality_report.failure_reasons}")

            if retry < max_retries - 1:
                # TODO: Run Black Hat fix cycle
                pass
            else:
                raise QualityGateError(
                    f"Document failed Quality Gate after {max_retries} attempts.\n"
                    f"Final Score: {quality_report.maturity_score}/10\n"
                    f"Failures: {quality_report.failure_reasons}"
                )

    # Inject Quality Gate badge
    final_content = inject_quality_gate_badge(mock_content, quality_report)

    # Write to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    status = "PASSED" if quality_report.passed_quality_gate else "FAILED"
    filename = f"{aggregated_data['feature_name'].replace(' ', '_')}_{status}_{timestamp}.{format}"
    full_path = Path(output_path) / filename

    full_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    # Save quality report JSON
    report_path = Path(output_path) / f"{full_path.stem}_quality_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(quality_report.model_dump(), f, indent=2)

    return {
        "file_path": str(full_path),
        "quality_report": quality_report,
        "passed": quality_report.passed_quality_gate,
    }


def inject_quality_gate_badge(content: str, report: QualityGateReport) -> str:
    """Inject Quality Gate report badge vào document."""
    badge = f"""

> **Quality Gate Report**
> - **Maturity Score**: {report.maturity_score}/10
> - **Depth Score**: {report.depth_score}/10
> - **Edge Cases**: {report.edge_case_coverage} scenarios
> - **Technical Feasibility**: {report.technical_feasibility}%
> - **Status**: {'✅ PASSED' if report.passed_quality_gate else '❌ FAILED'}

---

"""

    # Insert after first heading
    lines = content.split('\n')
    insert_idx = 1

    for i, line in enumerate(lines):
        if line.startswith('# '):
            insert_idx = i + 1
            break

    lines.insert(insert_idx, badge)
    return '\n'.join(lines)
