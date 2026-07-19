# Llama Guard paper

Course-provided reading from section 5 (critical asset protection).

`llama_guard_paper.pdf` is "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations" (Inan et al., Meta GenAI, 2023). The paper introduces a safety classifier built on Llama 2 that screens both prompts (input classification) and model responses (output classification) against a safety risk taxonomy.

Relevance for the section: guardrail models like Llama Guard are one of the concrete controls for protecting an LLM deployed as a critical asset, sitting at the input/output boundary rather than inside the model itself.
