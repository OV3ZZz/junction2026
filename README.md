# Junction 2026 — Personal Task Agent (Exa-powered)

This repository is initialized for a Junction 2026 hackathon project focused on building a **personal agent** that takes tedious real-life tasks off users’ hands.

## Challenge focus

Build an agent that can:
- Find relevant, current information across the web using **Exa**
- Compare options and reason about next steps
- Bring a task as close to done as possible, leaving final approval to the user when needed
- Show clear sources for every important claim

## Real-user task areas

Example domains for the demo:
- Daily living and errands
- Benefits eligibility and paperwork research
- Housing/rent checks
- Special occasion planning (e.g., vegan anniversary dinner ideas)
- Business info and travel disruption handling

## Judging alignment

This project should demonstrate:
1. Strong use of Exa for information that is not just model pretraining knowledge
2. Practical usefulness for a clearly defined user group
3. Transparent source attribution
4. Originality
5. A working live demo, including judge-provided queries

## Starter plan for this repo

- Define the target user segment and 2–3 high-value workflows
- Implement Exa-backed search/retrieval and normalized source handling
- Add task orchestration logic (plan -> gather -> compare -> suggest action)
- Build a demo flow that supports live prompts and auditable answers

## Next steps for contributors

1. Choose the first concrete workflow (e.g., rent increase legality check)
2. Add project code scaffold (API/app) in a follow-up PR
3. Integrate Exa API calls and source rendering early
4. Add scenario-based tests once runtime code is introduced