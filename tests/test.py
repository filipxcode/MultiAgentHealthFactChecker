import os
from dotenv import load_dotenv
from langsmith import evaluate
from langsmith.schemas import Run, Example # <-- Tego brakowało
from langsmith.evaluation import EvaluationResult
from src.graph.workflow import Workflow
from src.settings.config import get_llm
from pydantic import BaseModel, Field
from typing import Union
load_dotenv()

workflow = Workflow()
graph = workflow.main_graph
judge_llm = get_llm("smart") 

class EvalOutput(BaseModel):
    score: Union[int, str] = Field(description="Score 0 or 1")
    reasoning: str = Field(description="Short justification (up to 20 words)")


def predict_graph(inputs: dict) -> dict:
    nested = inputs.get("input")
    url = nested.get("video_url")
    initial_state = {
        "video_url": url,
    }
    return graph.invoke(initial_state)

def evaluate_report_quality(run: Run, example: Example) -> EvaluationResult:
    raw_outputs = run.outputs if run.outputs else {}
    raw_example_out = example.outputs if example.outputs else {}

    if "output" in raw_example_out and isinstance(raw_example_out["output"], dict):
        example_out = raw_example_out["output"]
    else:
        example_out = raw_example_out

    if "output" in raw_outputs and isinstance(raw_outputs["output"], dict):
        outputs = raw_outputs["output"]
    else:
        outputs = raw_outputs

    def normalize_get(d, keys):
        for k in keys:
            if k in d: return d[k]
        # Spróbuj lowercase
        d_lower = {k.lower(): v for k, v in d.items()}
        for k in keys:
            if k.lower() in d_lower: return d_lower[k.lower()]
        return None

    expected_behavior = normalize_get(example_out, ["expected_behavior", "Expected Behavior"])
    gk_verdict_ref = normalize_get(example_out, ["gatekeeper_verdict", "Gatekeeper Verdict"])
    sys_error_ref = normalize_get(example_out, ["system_should_error", "System Should Error"])
    
    should_be_rejected = False

    if gk_verdict_ref and str(gk_verdict_ref).lower() in ["end", "reject"]:
        should_be_rejected = True
        
    if sys_error_ref and str(sys_error_ref).lower() == "true":
        should_be_rejected = True

    if expected_behavior and "too long" in str(expected_behavior).lower():
        should_be_rejected = True
        


    
    if outputs.get("errors"):
        error_msg = outputs.get("errors")
        if should_be_rejected:
            return EvaluationResult(key="logic_check", score=1, comment=f"Correctly blocked (Error): {error_msg}")
        else:
            return EvaluationResult(key="system_error", score=0, comment=f"Unexpected Error: {error_msg}")


    final_report = outputs.get("final_report", "NO REPORT GENERATED")
    gatekeeper_verdict = outputs.get("gatekeeper_verdict")

    if should_be_rejected:
        if gatekeeper_verdict in ["end", "reject"] or final_report == "NO REPORT GENERATED":
            return EvaluationResult(key="logic_check", score=1, comment="Gatekeeper correctly blocked content.")
        else:
            return EvaluationResult(key="logic_check", score=0, comment=f"Gatekeeper FAILED. Expected reject, got pass.")

    if (gatekeeper_verdict in ["end", "reject"]) and not should_be_rejected:
        return EvaluationResult(key="report_quality", score=0, comment="Gatekeeper incorrectly blocked valid content.")
    
    must_contain_list = normalize_get(example_out, ["must_contain_topics", "Must Contain Topics"])
    if isinstance(must_contain_list, list) and len(must_contain_list) > 0:
        topics_str = "\n".join([f"- {t}" for t in must_contain_list])
    else:
        topics_str = "Refer to Expected Behavior description."
        
    eval_prompt = f"""
    You are a QA Auditor. Compare the AI System's Final Report with the Expected Behavior.

    --- EXPECTED BEHAVIOR (Ground Truth) ---
    {expected_behavior}
    
    --- MUST CONTAIN TOPICS (Check these specifically) ---
    {topics_str}
    
    --- SYSTEM FINAL REPORT ---
    {final_report}

    --- CRITERIA ---
    1. Are must-have claims in report? Claims can be same meaning but in different words.
    2. Are medical facts accurate?
    3. Is the tone correct (e.g. nuanced)?
    4. Strict Match is NOT required.- If Expected is "Nuanced" but System says "Unverified" (due to lack of evidence) -> This is ACCEPTABLE (Score 1).
    5. If Expected is "False/Nuanced" and System says "True" WITHOUT evidence -> Score 0.
    6. If System says "Unverified" but there is obvious well-known evidence it missed -> Score 0.
    """
    
    structured_llm = judge_llm.with_structured_output(EvalOutput)
    res = structured_llm.invoke(eval_prompt)
    
    return EvaluationResult(
        key="report_quality",
        score=int(res.score),
        comment=res.reasoning
    )

dataset_name = "ds-extraneous-bondsman-31" 

results = evaluate(
    predict_graph, 
    data=dataset_name,
    evaluators=[
        evaluate_report_quality, 
    ],
    experiment_prefix="Test-Custom-Evaluator",
)