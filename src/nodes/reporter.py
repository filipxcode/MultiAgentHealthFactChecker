from ..models.agent_state import AgentState

def reporter_node(state: AgentState):
    """
    """
    verdicts = state.final_verdicts
    
    report = "# 🕵️‍♂️ Raport Weryfikacji Faktów\n\n"
    
    total = len(verdicts)
    fake_count = sum(1 for v in verdicts if v.verdict.lower() == "fałsz")
    report += f"Przeanalizowano tez: **{total}**. Znaleziono nieprawdziwych: **{fake_count}**.\n\n"
    report += "---\n\n"
    
    for i, v in enumerate(verdicts):
        icon = "✅" if v.verdict.lower() == "prawda" else "❌"
        report += f"### {i+1}. {icon} Werdykt: {v.verdict}\n"
        report += f"**Wyjaśnienie:** {v.explanation_pl}\n"
        
        if v.sources:
            report += "**Źródła:**\n"
            for src in v.sources:
                report += f"- {src}\n"
        
        report += "\n---\n"
    return {"final_report": report}