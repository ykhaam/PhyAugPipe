ELEMENT_PARSE_PROMPT = """You are a vision-language parser for physics-rich real-world videos.
Given a caption and sampled frames, extract JSON keys:
entities, materials, actions, forces, outcomes.
Return compact valid JSON only.
"""

VISION_CHECK_PROMPT = """Validate the parsed JSON against the sampled frames.
Remove unsupported items and add clearly visible missing interactions/outcomes.
Return compact valid JSON only with same keys.
"""

PHYSICS_REASON_PROMPT = """Write concise, frame-grounded causal reasoning for visible physical events.
Avoid hidden causes. 2-4 short sentences.
"""

PROMPT_EXTEND_PROMPT = """Create two prompts grounded in visible frames:
1) cleaned_prompt: concise generation-ready prompt
2) extended_prompt: cleaned prompt + causal physical details.
No new unsupported entities. Return JSON.
"""
