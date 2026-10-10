"""Deterministic prompts; C and all steered conditions share identical text."""
from __future__ import annotations

from pathlib import Path
from .steering import canonical_json

OUTPUT_INSTRUCTION = '''Return exactly one JSON object with keys status, concept_status,
plan, explanation. status must be feasible, infeasible, prohibited, or unknown.
concept_status must be permitted, prohibited, or unknown. plan is an array of
action objects. Give a complete legal plan when feasible and [] otherwise.
Use exact operation, actor, and target identifiers from the task. explanation
must be a short explanation of your decision. Do not use Markdown fences.'''


def messages_for(case, baseline, ontology_text):
    if baseline not in ("A", "B", "C"):
        raise ValueError("Prompt baseline must be A, B, or C")
    system = "Solve the following fictional-world task.\n" + OUTPUT_INSTRUCTION
    if baseline == "B":
        system += "\n\nWorld description:\n" + ontology_text
    elif baseline == "C":
        system += ("\n\nApply the supplied version of the world specification. Check entity class, "
                   "resource cost, causal preconditions, and each step's resulting state. "
                   "Distinguish an explicitly prohibited operation from an undefined operation. "
                   "A permitted operation can still be infeasible in this initial state. "
                   "Check the requested concept separately from the task's feasibility.\n"
                   "<world_specification>\n" + ontology_text + "\n</world_specification>")
    task = {key: case[key] for key in ("question", "initial_state", "goal", "requested_concept")
            if key in case}
    if "distractor" in case:
        task["distractor"] = case["distractor"]
    return [{"role": "system", "content": system},
            {"role": "user", "content": canonical_json(task)}]


def ontology_for(version, root):
    if version not in ("v1", "v2"):
        raise ValueError("Ontology version must be v1 or v2")
    return (Path(root) / "experiment" / f"ontology-{version}.md").read_text()


def render_prompt(tokenizer, case, baseline, ontology_text):
    messages = messages_for(case, baseline, ontology_text)
    return messages, tokenizer.apply_chat_template(messages, tokenize=False,
                                                   add_generation_prompt=True)


def endpoint_text(tokenizer, case, ontology_text, response):
    # Append the answer without an end-of-turn marker: extract the final answer token,
    # not an EOS/template token. No compatibility label is exposed to the model.
    _, prompt = render_prompt(tokenizer, case, "C", ontology_text)
    return prompt + (response if isinstance(response, str) else canonical_json(response))
