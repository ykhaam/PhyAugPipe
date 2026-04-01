ELEMENT_PARSE_PROMPT = """Parse visible physical elements from caption and frames.
Return JSON keys: entities, materials, actions, forces, outcomes.
Caption: {caption}
"""

VISION_CHECK_PROMPT = """Given the previous parse and frames, remove hallucinations and add clearly visible missing interactions.
Return JSON with same keys.
Previous parse: {parse_json}
Caption: {caption}
"""

PHYSICS_REASON_PROMPT = """Write concise causal physical reasoning grounded in visible events only.
Parse: {parse_json}
Caption: {caption}
"""

PROMPT_EXTEND_PROMPT = """Generate two prompts:
1) cleaned_prompt: concise and generation-friendly.
2) extended_prompt: include causal physical details grounded in visible content.
Return JSON with cleaned_prompt, extended_prompt, notes.
Caption: {caption}
Checked parse: {parse_json}
Reasoning: {reasoning}
"""
