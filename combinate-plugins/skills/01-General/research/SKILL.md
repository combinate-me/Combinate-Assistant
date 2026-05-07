---
name: research
description: Deep research skill for Shane at Combinate. Use this skill whenever Shane wants to research a topic, competitor, technology, pricing strategy, market trend, or anything requiring synthesised external knowledge. Trigger on phrases like "research X", "what do we know about X", "look into X", "find out what agencies charge for X", "I want to understand X before deciding", or any question that requires pulling together multiple sources into a coherent briefing. This goes deeper than a quick web search - it uses the Perplexity API to run multi-step research tailored to Combinate's business context. v1.0.0
metadata:
  version: 1.0.0
  intranet_url: https://intranet.combinate.me/presentation/skill-research
model: claude-opus-4-6
---

# Skill: Research

## Overview

Use this skill when Shane asks to research a topic, competitor, technology, market trend, pricing strategy, or anything requiring synthesised external knowledge. This goes deeper than a quick web search - it is multi-step research tailored to Combinate's business context.

## When to Use
- "Research [topic] for me"
- "What do we know about [competitor/technology/market]?"
- "I want to understand [subject] before making a decision"
- "Find out what agencies are charging for [service]"
- Any question that requires pulling together multiple sources into a coherent briefing

## Steps

### 1. Load Business Context
Before calling the API, read the following files to build the context injection:
- `context/me.md`
- `context/work.md`
- `context/current-priorities.md`
- Any relevant files in `projects/` if the research relates to a specific active project

### 2. Clarify the Brief (if needed)
If the research request is broad or ambiguous, ask ONE focused question to sharpen scope before proceeding. Do not ask multiple questions. Examples:
- "Are you looking at this from a sales angle or a delivery/operations angle?"
- "Is this for a specific client or pitch, or general business intelligence?"

### 3. Read the API Key
Read the `.env` file in the project root and extract `PERPLEXITY_API_KEY`.

### 4. Build the Request
Construct a curl request to the Perplexity API with:
- **Endpoint:** `https://api.perplexity.ai/chat/completions`
- **Model:** `sonar-deep-research`
- **System prompt:** Inject business context (see template below)
- **User message:** The research query, refined from Shane's request

**System prompt template:**
```
You are a research analyst working for Shane McGeorge, CEO of Combinate - a premium digital agency based in Australia that builds web applications, websites, mobile apps, and handles workflow automation and AI consultation. The team is fully remote, primarily based in the Philippines.

Current business priorities:
- Securing new projects via bark.com leads
- Delivering active large projects on time and on budget
- Driving AI adoption across the team
- Maintaining strong client relationships

When conducting research, tailor your findings to be relevant and actionable for a premium digital agency competing in the Australian and international market. Focus on practical insights that can inform sales, delivery, or strategic decisions.

Provide your response with:
1. Key findings (concise bullets)
2. What this means specifically for Combinate
3. Recommended next actions
4. Sources
```

### 5. Execute the API Call
```bash
source .env && curl -s https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-deep-research",
    "messages": [
      {"role": "system", "content": "<SYSTEM_PROMPT>"},
      {"role": "user", "content": "<RESEARCH_QUERY>"}
    ]
  }'
```

Note: `sonar-deep-research` runs multiple search and reasoning steps. It may take 30-60 seconds to return. This is expected.

### 6. Present the Results
Parse the API response and present findings in this structure:

---
**Research Brief:** [topic]
**Date:** [today's date]

**Key Findings**
- [bullet points]

**What This Means for Combinate**
- [tailored implications]

**Recommended Actions**
- [specific next steps]

**Sources**
- [citations from the response]
---

If the response includes inline citations (e.g. [1], [2]), preserve them alongside the sources list.

## Notes
- The `.env` file is gitignored - the API key never gets committed
- `sonar-deep-research` is the best model for complex, multi-faceted research. For simpler factual lookups, `sonar` or `sonar-pro` can be used instead and will respond faster
- If the API key is missing or invalid, prompt Shane to add/update `PERPLEXITY_API_KEY` in the `.env` file
