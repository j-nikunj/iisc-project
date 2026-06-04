# Operational Reasoning Pipeline

The reasoning pipeline is responsible for translating the mathematical Subgraph $G'$ into a serialized format that an autoregressive LLM (`Qwen2.5-14B`) can comprehend and analyze.

## Context Assembly (Graph-to-Text)
Large Language Models degrade in reasoning quality when fed raw JSON or massive edge lists. The `ContextAssembler` class translates the extracted subgraph into readable operational chains.

*Raw Graph Data:*
`('flood-ecospace', 'corr-orr', {'type': 'IMPACTS', 'weight': 0.95})`

*Serialized Payload representation:*
`[Vulnerability: EcoSpace Underpass] --(IMPACTS)--> [Corridor: Outer Ring Road Marathahalli]`

## The System Prompt Architecture
To enforce epistemic boundary control, the LLM is initialized with a highly restrictive system prompt:

> "You are an elite Urban Mobility Expert analyzing Bengaluru traffic cascades. You will be provided with deterministic 'Operational Chains' extracted from a transportation knowledge graph.
> 
> RULES:
> 1. You may ONLY analyze the nodes and relationships explicitly provided in the Operational Chains.
> 2. Do NOT invent, assume, or hallucinate traffic connections that are not mathematically present in the context.
> 3. If the provided chains do not form a complete logical path to answer the prompt, state that the graph lacks the topology to complete the analysis.
> 4. Focus your output on systemic causality (how A causes B to fail)."

## Output Generation
The LLM synthesizes these chains, generating a multi-paragraph operational report that traces the phy