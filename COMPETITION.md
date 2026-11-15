# Competition Brief

## Theme: The Final Frontier

- Space has captured imaginations for generations, and the recent launch of Artemis II has ignited curiosity and awe once again.
- Engineers have long been at the forefront of innovation in the space sector, expanding humanity's horizons.
- MEC turns 20 this year. We celebrate by imagining the next 20 years: distant galaxies, new worlds, emerging technologies and a brighter future.

## Problem Statement

Design an application that supports some aspect of space travel. Address any mission phase:

- Pre-launch
- Launch and ascent
- In-transit
- Orbital or surface operations
- Re-entry and recovery
- Crew wellbeing and long-duration support

Any form you choose. Be creative, but keep it technically sound and well-structured.

### Things to consider

| Area | Examples |
|---|---|
| **User Interaction** | Dashboards, alerts, checklists, voice interfaces for high-workload settings |
| **Data Processing** | Real-time or near real-time telemetry, sensor and orbital tracking data |
| **Error Handling & Reliability** | Incomplete, delayed or corrupted data; comms dropouts; light delay |
| **Scalability & Performance** | High demand: satellite constellations, simultaneous missions |
| **Integration** | APIs, databases, public spaceflight data, orbital mechanics libraries |
| **Security & Privacy** | How mission data is stored, transmitted and protected |

### Scope

- Focus on a technically complete, functional system, not a predetermined feature set.
- Clearly state your **target audience**, **scope**, **intended impact**, and the **mission phase or use case**.
- Examples: crew health and life-support monitoring for a long-duration Mars transit, or collision-avoidance and debris tracking for LEO satellite operators.
- Ground your scenario in a real or realistically near-future context: an actual or plausible mission, agency, or public dataset, not pure sci-fi.
- **Anything outside your stated audience and scope will not be considered by judges.**

## Deliverables

Required: code, report and 10-minute presentation, plus a 3-minute pitch (+2 min Q&A) after the Day 1 deadline.

### Code

- Public GitHub repo with your full solution
- Must compile and be readable; errors hurt your score
- Claimed features must be in the code
- Cite any code written before the competition
- Be ready to explain snippets in judging
- Commit regularly: history verifies your work

### Presentation

- 10-minute presentation
- What it does, how it works, and a live demo
- Target user, scope, and what you would change with more time
- Only Day 2 teams present, but every team submits slides
- Keep it visual; do not read off slides

### Pitch

- End of Day 1, every team
- 3-minute pitch + 2-minute Q&A
- What it does, who it is for, and why it matters
- **Hard cutoff at 3 minutes**

## Rubric

### Code (/60)

| Criteria | What judges look for | Score |
|---|---|---|
| Functionality & Completeness | Works end to end; core features implemented, not mocked up or hardcoded | /15 |
| Technical Soundness & Architecture | Logical structure, intentional design, sensible architectural decisions | /10 |
| Data Processing | Handles real-time or near real-time data | /10 |
| Error Handling & Reliability | Handles incomplete, delayed, corrupted or missing data; has fallbacks | /10 |
| Scalability & Performance | Considers load: multiple satellites, missions or concurrent users | /5 |
| Integration | Uses real or realistic APIs, databases or libraries | /5 |

### Presentation (/40)

| Criteria | What judges look for | Score |
|---|---|---|
| Problem Definition & Scope | Target audience, mission phase and scope clearly and specifically stated | /5 |
| Solution Explanation | How the system works and the reasoning behind design choices | /15 |
| Demo / Evidence of Functionality | The system actually working, not just described in slides | /10 |
| Delivery & Communication | Clear, well paced, within 3 minutes; presents confidently without reading slides | /10 |

### Penalties

| Penalty | Points |
|---|---|
| Late submission | −25 |
| Syntax or compilation error | −25 |

**Total: /100**
