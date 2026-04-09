# Decisions

## [2026-03-29] Architecture Decisions

- **Remove CLI entirely** - Simplify codebase, web-only interface
- **Keep Flask + vanilla JS stack** - No framework migration
- **Use Vercel KV for persistence** - Free tier sufficient (256KB)
- **Maintain backward compatibility** - Keep existing data file formats
- **Extract GameState and GameEngine** - Separate logic from UI for testability
