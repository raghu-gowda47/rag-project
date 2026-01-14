"""
Prompt templates for RAG system.

This module centralizes all prompt templates to:
1. Enable easy modification and versioning
2. Support A/B testing different prompt strategies
3. Enforce consistent guardrails across queries
"""

# Guardrails to enforce safe and responsible AI behavior
GUARDRAILS = """
- Do not provide personal advice or medical/legal guidance
- Remain objective and avoid subjective opinions
- Only answer based on the provided context
- Do not make assumptions or use external knowledge
"""

RAG_PROMPT = """You are a helpful assistant answering questions based on provided context.

Instructions:
- Answer ONLY using information from the context below
- Be concise and direct
- If the context doesn't contain the answer, explicitly say "The information is not available in the provided context"
{guardrails}

Context:
{{context}}

Question:
{{question}}

Answer:""".format(guardrails=GUARDRAILS)

