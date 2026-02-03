from ..models.agent_state import AgentState
import logging

logger = logging.getLogger(__name__)

def reporter_node(state: AgentState):
    """
    Taking all sub-state judge summarization and concating it in one big report
    """
    verdicts = [res for res in state.final_verdicts if res is not None]
    logger.info(f"Generating final report based on {len(verdicts)} verdicts")
    
    report = "# Fact-Check Report\n\n"
    
    total = len(verdicts)
    fake_count = sum(1 for v in verdicts if v.verdict.lower() == "false")
    report += f"Analyzed claims: **{total}**. Debunked: **{fake_count}**.\n\n"
    report += "---\n\n"
    
    for i, v in enumerate(verdicts):
        icon = "✅" if v.verdict.lower() == "true" else "❌"
        report += f"### {i+1}. {icon} Verdict: {v.verdict}\n"
        report += f"**Claim:** {v.claim.statement}\n"
        report += f"**Explanation:** {v.explanation}\n"
        if v.sources:
            report += "**Sources:**\n"
            for src in v.sources:
                report += f"- {src}\n"
        
        report += "\n---\n"
    return {"final_report": report}