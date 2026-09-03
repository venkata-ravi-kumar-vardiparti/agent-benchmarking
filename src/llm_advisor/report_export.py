"""Builds a PDF export of the LLM Capability Advisor report."""

from __future__ import annotations

from datetime import datetime

from fpdf import FPDF

from justification_agent.schema import JustificationResult
from llm_advisor.analyzer_schema import ScenarioEvaluationBlueprint
from model_qualification.schema import ModelQualificationResult
from scoring_agent.schema import ScoringResult


def _safe(text: object) -> str:
    """fpdf2's core fonts only support latin-1 -- drop characters they can't render."""
    return str(text).encode("latin-1", "replace").decode("latin-1")


class _ReportPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "LLM Capability Advisor Report", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(
            0, 6,
            _safe(datetime.now().strftime("Generated %Y-%m-%d %H:%M")),
            new_x="LMARGIN", new_y="NEXT",
        )
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def section_title(self, title: str) -> None:
        self.ln(4)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, _safe(title), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)


def _blueprint_rows(blueprint: ScenarioEvaluationBlueprint) -> list[tuple[str, str]]:
    ctx = blueprint.business_context
    workload = blueprint.workload_profile
    benchmark = blueprint.benchmark_plan
    governance = blueprint.governance_requirements
    financial = blueprint.financial_constraints

    capabilities = ", ".join(c.value for c in blueprint.required_capabilities) or "None specified"
    metrics = ", ".join(m.value for m in benchmark.evaluation_metrics) or "None specified"
    weights = ", ".join(f"{k}: {v}%" for k, v in benchmark.weights.items()) or "None specified"
    regulations = ", ".join(r.value for r in governance.regulations) or "None"
    allowed_regions = ", ".join(r.value for r in governance.allowed_regions) or "Any"

    return [
        ("Industry", ctx.industry.value),
        ("Use case", ctx.use_case),
        ("Volume of requests (per month)", str(ctx.monthly_request_volume)),
        ("Workload family", workload.workload_family.value),
        ("Task type", workload.task_type.value),
        ("Complexity", workload.complexity.value),
        ("Context window", workload.context_window),
        ("Required capabilities", capabilities),
        ("Evaluation metrics", metrics),
        ("Scoring weights", weights),
        ("Regulations", regulations),
        ("Allowed regions", allowed_regions),
        ("Monthly budget", f"${financial.monthly_budget_usd:,.2f}"),
        ("Sustainability weightage", blueprint.sustainability_weightage.value),
    ]


def build_pdf_report(
    blueprint: ScenarioEvaluationBlueprint,
    qualification: ModelQualificationResult,
    scoring_result: ScoringResult | None = None,
    justification_result: JustificationResult | None = None,
) -> bytes:
    """Render the full Capability Advisor report (blueprint, qualification, scores,
    and justifications -- whichever pipeline stages completed) as a PDF."""
    pdf = _ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.section_title("Scenario Evaluation Blueprint")
    with pdf.table(col_widths=(45, 145), text_align="LEFT") as table:
        for field, value in _blueprint_rows(blueprint):
            row = table.row()
            row.cell(_safe(field))
            row.cell(_safe(value))

    pdf.section_title("Model Qualification")
    with pdf.table(col_widths=(50, 30, 110), text_align="LEFT") as table:
        header = table.row()
        for heading in ("Model", "Status", "Reasons"):
            header.cell(heading)
        for qualified in qualification.qualified_models:
            row = table.row()
            row.cell(_safe(qualified.model_name))
            row.cell("Qualified")
            row.cell("-")
        for disqualified in qualification.disqualified_models:
            row = table.row()
            row.cell(_safe(disqualified.model_name))
            row.cell("Disqualified")
            row.cell(_safe("; ".join(disqualified.reasons)) or "-")

    if scoring_result and scoring_result.scorecards:
        pdf.section_title("Model Scoring")

        metric_names: list[str] = []
        seen: set[str] = set()
        for card in scoring_result.scorecards:
            for metric_score in card.metric_scores:
                if metric_score.metric not in seen:
                    seen.add(metric_score.metric)
                    metric_names.append(metric_score.metric)

        headings = ["Model", *metric_names, "Overall", "Carbon", "Energy", "Sustainability"]
        col_width = 190 / len(headings)
        with pdf.table(col_widths=tuple([col_width] * len(headings)), text_align="LEFT") as table:
            header = table.row()
            for heading in headings:
                header.cell(_safe(heading))
            for card in scoring_result.scorecards:
                scores_by_metric = {ms.metric: ms.score for ms in card.metric_scores}
                row = table.row()
                row.cell(_safe(card.model_name))
                for name in metric_names:
                    row.cell(f"{scores_by_metric[name]:.0f}" if name in scores_by_metric else "-")
                row.cell(f"{card.overall_score:.0f}")
                row.cell(f"{card.carbon_score:.2f}")
                row.cell(f"{card.energy_score:.2f}")
                row.cell(f"{card.sustainability_score:.0f}")

    if justification_result and justification_result.justifications:
        pdf.section_title("Score Justifications")
        for justification in justification_result.justifications:
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(
                0, 6,
                _safe(f"{justification.model_name} (Overall: {justification.overall_score:.0f}/100)"),
                new_x="LMARGIN", new_y="NEXT",
            )
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, _safe(justification.justification), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

    return bytes(pdf.output())
