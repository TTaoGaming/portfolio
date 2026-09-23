# Quorum: independent verdicts by model family

Tommy Tai asked for a four-family quorum on this packet: Anthropic Claude, OpenAI GPT, Moonshot Kimi and Google Gemini. A verdict counts only if it comes from a different model family than the other verdicts. A family's first verdict is the one that counts.

**How to add a verdict**
1. Check out this branch and run `./verify_all.sh`, or the subset your tools allow.
2. Recompute the packet digest:

   ```bash
   python3 tools/make_manifest.py   # prints the packet digest
   ```

   Then check it against your own `sha256sum` of the files listed in `MANIFEST.json`.
3. Add `quorum/<family>_<model>.json` in the shape of `quorum/anthropic_claude-opus-5-5.json`. Record:
   - which checks you ran and their exact output lines;
   - what you did *not* check;
   - `"verdict": "CONFIRMED"` or `"CONTRADICTED"`, with the reason.
4. Post the same verdict in Slack #gen143-ops, in the QUORUM thread, with your run's metadata: model, surface, session or run id, and UTC time.

**Quorum:** four families CONFIRMED, with no CONTRADICTED verdict that remains unresolved. A self-report from whoever found the chain does not count.

| Family | Model | Verdict | File |
|---|---|---|---|
| anthropic | claude-opus-5-5 | CONFIRMED | `anthropic_claude-opus-5-5.json` |
| openai | GPT-6 Sol | pending | – |
| moonshot | Kimi K3 | pending | – |
| google | Gemini | pending | – |
