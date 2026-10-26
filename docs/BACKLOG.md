# Agora backlog

- **Opt-in voice + fixed-order mode** (idea 2026-10-26, parked). `/agora:setup voice`: the spinner shows one card at a time in deck order, and the system voice speaks each card's front on every prompt (macOS `say`, voice picked per deck language, e.g. Paulina for es_MX). Prototype is local-only at `~/.agora/spinner-next.py`. Must work with any deck, fall back to silent on non-Mac, and avoid clobbering settings.json. Off by default because it bypasses SRS.
