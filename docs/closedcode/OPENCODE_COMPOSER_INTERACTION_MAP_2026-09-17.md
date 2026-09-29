# OpenCode Composer Interaction Map — ClosedCode Android

Date: 2026-09-17

Purpose: authoritative implementation crosswalk for the ClosedCode Android recreation of the OpenCode composer controls. This map is derived from the repository's OpenCode source, not from visual guessing.

## Scope

The Director identified four remaining interactive surfaces that must behave like OpenCode:

1. agent / Build-Plan control;
2. model selector;
3. reasoning/model-variant control;
4. session usage/details control.

ClosedCode is a native Android client and therefore cannot literally execute the SolidJS/Kobalte implementation byte-for-byte. The implementation target is source-equivalent state transitions, selection semantics, dismissal/focus behavior, backend payload semantics, and motion timing, with a native Android presentation matching the supplied OpenCode screenshots.

## Agent control

Primary sources:

- `packages/app/src/context/local.tsx`
- `packages/app/src/context/local-agent.ts`
- `packages/app/src/pages/session/composer/session-composer-controls.ts`
- `packages/session-ui/src/v2/components/prompt-input/index.tsx`

Source semantics:

- visible primary-agent list excludes `mode === "subagent"` and hidden agents;
- resolve requested agent by exact name, then `build`, then first available;
- selected agent is persisted per session;
- if custom agents are hidden, OpenCode resolves to `build`;
- selecting an agent also adopts that agent's configured model and variant when present, otherwise retains the previous session model/variant;
- agent cycling wraps at both ends;
- the prompt request carries the selected agent name.

ClosedCode must not hardcode Build/Plan as the backend state model. Those names may be the common UI choices, but the available list must come from the live agent contract.

## Model selector

Primary sources:

- `packages/app/src/components/dialog-select-model.tsx`
- `packages/app/src/pages/session/composer/prompt-model-selection.ts`
- `packages/app/src/context/local.tsx`
- `packages/app/src/components/prompt-input-v2.tsx`

Source semantics:

- model list is filtered to visible models;
- selected model must belong to a connected provider;
- search matches model name, model id, and provider name;
- results sort by model name and group by provider;
- provider groups use OpenCode's provider ordering logic;
- current model is restored using session selection / agent model / configured default / recent / connected-provider fallback semantics;
- selecting a model updates visibility and recent-model state;
- the actual prompt request carries exact `providerID` and `modelID`;
- selector open resets active item to current model when possible;
- search input receives focus after open;
- arrow keys wrap through options;
- Enter selects active option;
- Escape closes without applying;
- selection closes first, then applies selection after close to avoid focus/animation glitches;
- outside interaction closes without forcing trigger focus restoration.

## Reasoning / model variant control

Primary sources:

- `packages/app/src/context/model-variant.ts`
- `packages/app/src/context/local.tsx`
- `packages/app/src/pages/session/composer/prompt-model-selection.ts`
- `packages/app/e2e/regression/prompt-thinking-level.spec.ts`

Source semantics:

- variant choices come from the selected model's declared variant list;
- the control is not a universal hardcoded Low/Medium/High list;
- explicit `null` selection means use the model default;
- an explicit selected variant wins if still valid;
- otherwise a valid agent-configured variant wins;
- otherwise a saved per-model variant may be restored;
- invalid/stale variants are ignored;
- cycling wraps through the declared list and back to default according to `cycleModelVariant`;
- prompt submission includes `variant` only when an explicit/current variant resolves.

## Menu / popup interaction primitive

Primary sources:

- `packages/ui/src/v2/components/menu-v2.tsx`
- `packages/ui/src/v2/components/menu-v2.css`
- `packages/app/src/components/dialog-select-model.tsx`

Source semantics relevant to native Android parity:

- expanded trigger uses pressed/expanded visual state;
- menu open animation is exactly `120ms ease-out`;
- opening transform is `scale(0.96) -> scale(1)`;
- opening opacity is `0 -> 1`;
- transform origin follows the popup anchor;
- menu rows are 28px high in desktop V2, with 4px radius and highlighted/checked states;
- selected radio item uses accent text/check indicator;
- pointer/focus outside dismisses;
- Escape dismisses;
- OpenCode deliberately controls whether trigger focus is restored based on dismissal cause.

For the Director-supplied mobile screenshots, ClosedCode should project the same state machine into the native bottom-sheet geometry shown by the reference rather than falling back to stock `AlertDialog`.

## Prompt-input transition behavior

Primary sources:

- `packages/session-ui/src/v2/components/prompt-input/machine.ts`
- `packages/session-ui/src/v2/components/prompt-input/interaction.ts`
- `packages/session-ui/src/v2/components/prompt-input/index.tsx`

Relevant interaction state is explicit and event-driven. Native Android controls should likewise use one state owner rather than allowing independent dialogs to write unrelated preference keys.

## Usage/context control

Primary sources:

- `packages/app/src/components/session-context-usage.tsx`
- `packages/app/src/components/session/session-context-metrics.ts`
- `packages/app/src/components/session/session-context-tab.tsx`

OpenCode derives context usage from actual session messages/provider model limits. Its context metrics include message count, provider/model, total/input/output/reasoning/cache tokens, context usage percentage, cost, session-created time, and last activity.

ClosedCode must populate the Director-supplied mobile usage/details surface from live session/message metadata rather than static labels.

## Existing ClosedCode defects this map replaces

At the time this map was written, Android `MainActivity` still used:

- hardcoded Build/Plan `AlertDialog`;
- hardcoded Auto/Low/Medium/High `AlertDialog`;
- two-stage provider then model `AlertDialog`;
- global SharedPreferences keys that do not match OpenCode's per-session model/agent/variant state;
- no OpenCode-equivalent menu state machine or motion contract.

Those are temporary approximations and should be removed as the mapped controls are implemented.
