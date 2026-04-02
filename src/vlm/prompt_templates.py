ELEMENT_PARSE_PROMPT = """You are following Algorithm 1 (Step 1: Element Parsing).
Input original prompt p and video frames V.
Extract entities, actions, forces, and outcomes from (p, V).
Ensure all agents are included and avoid unsupported/speculative items.

Return strict JSON:
{{
  "original": "{caption}",
  "parse": {{
    "entities": [],
    "materials": [],
    "actions": [],
    "forces": [],
    "outcomes": []
  }}
}}

Original prompt p: {caption}
Frame hints V: {frame_hints}
"""

VISION_CHECK_PROMPT = """You are following Algorithm 1 (Step 2: Vision Checking).
Compare parse with video frames and original prompt.
Remove hallucinated elements and add missing visible entities/interactions.

Return strict JSON:
{{"parse": {{"entities": [], "materials": [], "actions": [], "forces": [], "outcomes": []}}}}

Original prompt p: {caption}
Previous parse: {parse_json}
Frame hints V: {frame_hints}
"""

PHYSICS_REASON_PROMPT = """You are following Algorithm 1 (Step 3: Physics Reasoning).
Write concise causal explanation of how parsed entities interact through physical forces and produce outcomes.

Return strict JSON:
{{"reason": "..."}}

Original prompt p: {caption}
Checked parse: {parse_json}
Frame hints V: {frame_hints}
"""

PROMPT_EXTEND_PROMPT = """You are following Algorithm 1 (Step 5: Prompt Extending).
Extend original prompt using causal details from reason.
Do not add new entities/forces/sensory descriptions.
Keep extension <= 100 words.

Return strict JSON:
{{
  "cleaned_prompt": "...",
  "extended": "...",
  "notes": "..."
}}

Original prompt p: {caption}
Checked parse: {parse_json}
Reason: {reasoning}
"""
