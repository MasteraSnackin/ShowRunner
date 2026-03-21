# Encode ShowRunner Pitch Talk Track

## Slide 1 - Title

We built Encode ShowRunner around a simple belief: events fail in the gaps between platforms. Communication happens in one place, ticketing in another, payouts somewhere else, and trust is often handled manually. ShowRunner is our answer to that fragmentation.

## Slide 2 - Problem

The problem is not that teams lack tools. It is that they have too many disconnected tools. Organisers coordinate in chat, manage ticketing elsewhere, and then handle approvals manually. Every handoff adds delay, confusion, and operational risk.

## Slide 3 - Why These Platforms

We chose these platforms deliberately. Luffa is where communities already coordinate, so event actions should start there. Endless gives us the transactional backbone for ticketing, settlement, and payout. Civic gives us the trust layer, so AI can assist operations without bypassing policy.

## Slide 4 - How It Works

ShowRunner is the orchestration layer that connects those worlds. A dashboard action or webhook event enters the same FastAPI application. Shared workflows then coordinate enrichment, guardrail checks, settlement logic, and persistence. That keeps the experience consistent whether the workflow begins in the browser or in Luffa.

## Slide 5 - What We Built

This is already a working prototype. We built the dashboard, webhook handling, lifecycle flows, persistence, structured API errors, and automated tests. The product can already create events, simulate sales, settle revenue, and approve payouts in one flow.

## Slide 6 - Closing

The core message is simple: ShowRunner turns fragmented event operations into one trusted, AI-assisted workflow. Luffa handles communication, Endless handles transaction flow, Civic handles trust, and ShowRunner brings them together into a product teams can actually operate.
