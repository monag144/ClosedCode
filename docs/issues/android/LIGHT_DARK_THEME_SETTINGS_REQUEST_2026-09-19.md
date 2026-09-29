# Android Feature Request — Light / Dark Theme Settings — 2026-09-19

**Status:** OPEN PRODUCT REQUEST  
**Surface:** ClosedCode Android client  
**Requested by:** Director

## Product direction

Add a theme preference in **Settings**.

Do **not** add another persistent theme toggle/control to the primary coding-agent UI.

The current color treatment is visually distracting and feels closer to OpenCode styling than the desired ClosedCode identity.

## Required modes

### Light

Target appearance:

- predominantly white / near-white background;
- black or near-black primary text;
- softer black / grayscale borders and secondary UI elements;
- restrained gray hierarchy for cards, separators, secondary labels, and disabled states;
- preserve the existing yellow Send/action accent where appropriate.

The goal is a clean, neutral, high-legibility light interface rather than a colorful or heavily branded surface.

### Dark

Target appearance:

- predominantly black / near-black background;
- white / near-white primary text;
- restrained dark-gray surfaces and borders for hierarchy;
- secondary text in softer gray;
- preserve the yellow Send/action accent where appropriate.

The desired reference feel is similar to the current ChatGPT dark UI: simple black/white contrast with restrained neutral grays.

## Settings behavior

Recommended setting:

`Settings → Appearance → Theme`

Values:

- Light
- Dark

A future optional `System default` value may be added if useful, but it is not required by this request.

## Scope constraint

This request is about **color/theme presentation**, not a redesign of the coding-agent interaction model.

Do not:

- rearrange core controls merely to implement theming;
- add theme buttons to the main agent screen;
- expand this into an unrelated UI redesign;
- change provider/tool/session behavior.

## Acceptance condition

Switching the theme from Settings should update the app consistently across:

- main transcript;
- user/assistant messages;
- tool cards;
- composer;
- Send/Stop controls;
- session/thread UI;
- settings;
- dialogs/sheets;
- workspace/diff surfaces;
- empty/error/loading states.

Text contrast must remain readable and the yellow action accent should remain coherent in both modes.
