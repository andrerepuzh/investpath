---
name: Streamlit workflow startup
description: Avoid Streamlit's first-run terminal prompt when starting the app workflow.
---

Start the Streamlit workflow with headless mode and usage statistics disabled:
`--server.headless true --browser.gatherUsageStats false`.

**Why:** In this Replit environment, Streamlit's first-run email prompt blocked
the workflow from opening its port when run without a terminal.

**How to apply:** Keep both options in the workflow command and manual launch
instructions so first startup does not wait for interactive input.
