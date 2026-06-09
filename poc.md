# Economic Intelligence Platform — Proof of Concept
**Economic Intelligence Platform**
Version 0.1 · June 2026

---

## Purpose

This document describes what the EchnoMind POC must prove, why it exists, and how we will know it has succeeded.

A POC is not a product. It is a controlled experiment to answer a single question before committing to full development:

> *Can we collect financial news, run AI analysis on it, store it intelligently, and let a user get meaningful answers from it — all working together as one system?*

---

## Problem We Are Solving

Financial news is overwhelming. Every day, hundreds of articles cover RBI decisions, market movements, sector performance, and economic indicators. Most people — investors, analysts, students, professionals — do not have the time to read and make sense of all of it.

EchnoMind proposes to do that reading and thinking automatically, then surface just what matters: a health score, a sentiment summary, sector signals, and answers to direct questions.

The POC validates whether that pipeline is technically feasible with available tools and free-tier APIs.

---

## What the POC Will Demonstrate

By the end of the POC, the following should work together as a single, manually triggered run:

**1. News is fetched automatically**
The system pulls the latest Indian financial news from at least two sources and stores the raw articles locally.

**2. AI assigns a sentiment to each article**
Each article is labelled Positive, Negative, or Neutral by a financial-domain AI model (FinBERT), with a confidence score. The affected market sector is also identified.

**3. Articles are stored in a searchable knowledge base**
Processed articles are embedded and stored in a vector database so they can be retrieved by meaning, not just keywords.

**4. A chatbot answers questions using today's news**
A user can type a plain-English question. The system finds the most relevant articles and uses an LLM to generate a grounded, cited answer.

**5. A dashboard makes it all visible**
A single screen shows the Economic Health Score, market sentiment, sector signals, top stories, and the chatbot — all from the same day's data.

---

## What the POC Will NOT Do

To keep the scope achievable, the following are explicitly excluded:

- No user accounts, login, or authentication
- No automated or scheduled pipeline (runs are triggered manually)
- No full article text — free APIs return headlines and descriptions only
- No persistent chat history — each question is independent
- No production-grade infrastructure — everything runs locally
- No email reports or notifications
- No paid data sources

These are not oversights. They are deliberate trade-offs to reach a working end-to-end prototype as fast as possible.

---

## Inputs and Outputs

| Input | Output |
|---|---|
| Financial news headlines (NewsAPI, RSS) | Sentiment-labelled, categorised articles |
| Live market prices (yfinance) | Economic Health Score |
| User's plain-English question | Grounded AI answer with source citations |
| All of the above combined | A readable dashboard |

---

## How We Know the POC Has Succeeded

The POC is complete when all seven conditions below are met:

| # | Condition | Acceptable Result |
|---|---|---|
| 1 | News fetched | At least 30 articles per run, no errors |
| 2 | Sentiment accuracy | 80%+ correct on 20 manually reviewed articles |
| 3 | Categorisation | 90%+ of articles receive a correct category |
| 4 | Knowledge base query | 5 test queries return relevant articles |
| 5 | Chatbot answers | All 5 test questions answered with correct, cited responses |
| 6 | Health Score | Score matches general market mood on 3 separate test days |
| 7 | Dashboard usability | One non-technical person navigates it without guidance |

---

## Timeline

| Week | Focus |
|---|---|
| Week 1 | News ingestion + FinBERT sentiment working |
| Week 2 | Vector store + chatbot working end to end |
| Week 3 | Dashboard assembled, success criteria tested |

Total: 3 weeks, 1–2 developers.

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| NewsAPI free tier too limited | Medium | Use RSS feeds as backup sources |
| FinBERT too slow on CPU | Low | Process in batches; limit to 50 articles per run |
| LLM rate limits (Groq/Gemini) | Medium | Cache answers; limit to 10 chatbot queries per session |
| Low sentiment accuracy on Indian finance news | Medium | Manual review early; adjust confidence threshold |

---

## What Comes Next

If the POC succeeds, phase two will focus on:

- Replacing keyword categorisation with a trained classifier
- Enriching the Health Score with RBI, CPI, and GDP data
- Automating the pipeline to run daily at 7 AM IST
- Moving to a hosted vector database
- Building proper authentication and a production UI

---

*This document is a validation brief, not a technical specification.*
*For the technical breakdown, see SPEC-KIT.md.*
