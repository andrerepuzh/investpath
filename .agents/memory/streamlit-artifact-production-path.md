---
name: Streamlit artifact production paths
description: Working-directory difference between a Streamlit artifact's development and production commands.
---

The artifact development command may run from the artifact directory, while the production command can run from the workspace root. A relative script path that works in the preview can therefore fail after publishing. Verify the production command from its actual working directory and use the corresponding script path.

**Why:** InvestPath preview launched with a relative path from its artifact folder, but the production command resolved that same path from the workspace root and could not find the app.

**How to apply:** When configuring Python/Streamlit artifact deployment, test the production run command from the workspace root before asking the user to publish.
