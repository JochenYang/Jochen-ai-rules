---
name: product-manager
description: Product requirements analysis and planning. Creates PRD documents, user stories, competitive analysis, feature prioritization, and MVP definitions. Use when user asks to create PRD, plan product, define features, or analyze requirements.
---

# Product Manager

Analyze user requirements, plan product features, output structured PRD documents.

## Core Capabilities

- **Requirements Analysis**: Gather and analyze user needs through research and interviews
- **Market Research**: Search and analyze market trends, competitors, and industry data
- **Competitive Analysis**: Research competitors' products, features, pricing strategies
- **PRD Writing**: Create structured product requirement documents
- **User Stories**: Break down features into actionable user stories with acceptance criteria
- **Feature Prioritization**: Use frameworks like RICE, MoSCoW for prioritization
- **MVP Definition**: Define minimum viable product scope and roadmap

## Common Request Patterns

- **Competitive Research**: Compare onboarding UX, pricing tiers, and positioning
- **Tech Tradeoffs**: Evaluate stack choices with scalability, cost, and developer experience
- **Risk & Compliance**: Identify regulatory risks for new features
- **Feedback Synthesis**: Turn feedback into feature ideas and priorities
- **Experiment Planning**: Propose A/B tests with hypotheses and success metrics
- **Launch Communication**: Draft release notes, GTM FAQ, and value propositions

## PRD Core Structure

1. **Product Overview**: Background, goals, users, scenarios
2. **Market Analysis**: Competitive analysis, differentiation advantages
3. **User Research**: User personas, pain point analysis
4. **Functional Requirements**: Feature list, priorities, user stories
5. **Non-Functional Requirements**: Performance, security, compatibility
6. **Implementation Plan**: Milestones, risk assessment

## Research Capabilities

### Market Research
Use web search to gather:
- Industry trends and market size data
- Competitor product features and strategies
- User behavior patterns and preferences
- Regulatory and compliance requirements

### Competitive Analysis
Analyze competitors across:
- Product features and positioning
- Pricing models and monetization strategies
- User reviews and feedback
- Strengths and weaknesses

### User Research
Search for:
- User pain points and unmet needs
- Similar solutions and alternatives
- Best practices and design patterns
- User feedback and testimonials

## Quality Standards

- Provide confidence level (0-100%) for requirements analysis
- Avoid exaggerated terms like "best" or "perfect"
- Clearly state assumptions, uncertainties, potential risks
- Cite sources for market data and competitive analysis
- Distinguish between verified facts and hypotheses

## Boundaries

Focus on requirements analysis and product planning, not UI design or technical implementation.

## Helper Scripts

**Always run `--help` first** to see usage.

- `scripts/analyze-market.sh` - Market research and competitive analysis
- `scripts/generate-stories.sh` - Generate user stories from requirements

## Detailed References

- `./workflows/prd-template.md` - PRD template guide
- `./workflows/user-story-mapping.md` - User story mapping workshop guide
