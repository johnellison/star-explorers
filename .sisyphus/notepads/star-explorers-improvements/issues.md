# Issues

## [2026-03-29] Pre-Existing Issues

- **Critical**: Vercel loses all progress on cold starts (data copied to `/tmp`)
- **No direct kid input** - Only dad's judgment via keyboard
- **Thin question bank** - Only math and spelling, missing science, geography, reading
- **Only 25 sessions** - Wraps with modulo after that
- **No text-to-speech** - No independent play option for kids
- **No kid-facing progress visualization** - Stats are parent-facing only
- **Duplicate game logic** - ~700 lines duplicated between CLI and web
- **No auto-save** - State lost if browser closes mid-session
- **Minimal sound effects** - Only correct/wrong chimes
- **No accessibility/calm mode** - Constant animations could overwhelm neurodivergent kids

## [2026-03-29] LSP Errors

- Multiple type errors in `questions.py`, `session.py`, `app.py`, `generate_images.py`
- Missing import resolution for `flask`, `rich`, `google.genai`
- To be fixed in Task 10 (Testing & Documentation)
