# 02_DESIGN.md

Use this prompt to define the visual system for the Crypto Risk System frontend (Phase 1). This file owns colors, gradients, glow, motion, and theme switching behavior.

## Prompt

You are a senior product designer + frontend engineer. Define a cohesive design system for a crypto market risk intelligence UI (not a trading dashboard).

Hard requirements from the project owner:
- Global background (dark): `#090514` to `#0D0B1A`.
- Accent / CTA: `#6D28D9` or `#7C3AED` (neon purple), optionally blended with `#3B82F6` (blue) in gradients.
- Surface / cards: `#1A162B` or `rgba(26, 22, 43, 0.6)` for glass.
- Text: `#FFFFFF` (headings) and `#9CA3AF` (secondary text).
- Glow language is driven by gradients + blur and multi-layer shadows, not flat colors.
- Must support dark mode and light mode via a toggle button.
- Theme toggle should have a visible gradient/motion effect.
- The full UI components should only appear after the user presses an "Activate" button, with an animated reveal.

## Visual Direction

Name the style internally as: "Neon Risk Cockpit".
- Mood: calm, high-contrast, technical, slightly futuristic.
- Primary material: glass surfaces on deep-space background.
- Primary visual energy: subtle purple/blue glow fields that hint at market stress without being noisy.

## Typography

Pick a clear, modern, non-default font pair:
- Display/heading: a geometric sans with character (example: "Space Grotesk" or "Sora").
- Body: a highly readable sans (example: "IBM Plex Sans" or "Inter").

Rules:
- Headings are short, high contrast.
- Secondary text should never fall below readability thresholds.
- Avoid dense paragraphs; prefer short blocks of explanation.

## Theme Tokens (CSS Variables)

Define tokens for both themes. Provide a concrete token table and a CSS variables snippet.

### Dark Theme (default)
- `--bg-0`: `#090514`
- `--bg-1`: `#0D0B1A`
- `--surface-0`: `#1A162B`
- `--surface-glass`: `rgba(26, 22, 43, 0.60)`
- `--border-subtle`: `rgba(255, 255, 255, 0.10)`
- `--text-0`: `#FFFFFF`
- `--text-1`: `#9CA3AF`
- `--accent-0`: `#6D28D9`
- `--accent-1`: `#7C3AED`
- `--accent-2`: `#3B82F6`
- `--danger`: a red that reads on dark without turning neon (pick one).
- `--ok`: a green that reads on dark without turning neon (pick one).

### Light Theme
Keep the same brand accents, but invert surfaces so the app remains readable and still "tech".
- Background becomes off-white with a faint violet cast (pick 2 hexes).
- Surfaces become white or near-white with subtle glass border.
- Text becomes near-black for headings and neutral gray for secondary.
- Glows become softer and smaller so the app does not look like a nightclub in daylight.

## Gradients (Recipes)

Define reusable gradient recipes as variables or mixins:

- Background gradient:
  - A subtle vertical blend from `--bg-0` to `--bg-1`, plus optional faint radial in corners.

- Accent gradient (CTA):
  - Purple to violet to blue: `--accent-0 -> --accent-1 -> --accent-2`.
  - Provide a direction rule (left-to-right) and a "hotspot" variant for hover.

- Risk-level gradients (optional, Phase 1):
  - Low/Medium/High/Extreme mapping that does not conflict with the purple brand.
  - Risk color should be readable on both themes.

## Glow System (Core)

Specify the two allowed glow mechanisms:

1) Background glow fields
- Implement as absolutely positioned circles/ovals.
- Use `border-radius: 50%`.
- Use `radial-gradient(...)` with alpha stops.
- Use `filter: blur(100px)` (or smaller in light theme).
- Limit to 2-4 glow fields per page to avoid haze.

2) CTA glow
- Implement as multi-layer `box-shadow` with purple/violet hues.
- Provide a 3-layer shadow recipe: tight, medium, wide.
- Hover increases glow slightly; active compresses.

## Glass Surfaces

Define a single glass recipe:
- Background: `--surface-glass`
- Border: `--border-subtle`
- Backdrop blur: `backdrop-filter: blur(10px)` with graceful fallback if unsupported.
- Do not nest glass cards inside glass cards.

## Motion

Define motion rules with durations and easing:
- Standard: 180-240ms
- Emphasis: 320-420ms
- Easing: `cubic-bezier(0.2, 0.8, 0.2, 1)`
- Respect `prefers-reduced-motion` by reducing blur animations and disabling large translations.

## Theme Toggle Behavior

The toggle must feel like a state change, not a checkbox:
- On toggle, animate:
  - background gradient cross-fade (via opacity layer),
  - accent glow ripple (brief, 200-300ms),
  - icon rotation or slide (subtle).
- The toggle should live in the top command bar, right side.
- Persist theme in `localStorage`.

## "Activate" Gate (Reveal UI)

Phase 1 must start in a pre-activated state:
- Show a full-viewport overlay with:
  - the app name,
  - a one-line risk-oriented tagline,
  - a single CTA button: "Activate Cockpit".
- On click:
  - CTA emits a short gradient pulse,
  - overlay fades out,
  - main UI fades/steps in (stagger: command bar, rails, main stage).
- Persist activation in session memory (not localStorage) unless specified otherwise.

This is not a marketing landing page. It is an intentional "arming" moment before showing live risk.

## Accessibility

- Minimum contrast targets for both themes.
- Focus rings must be visible on both backgrounds.
- Tooltips must be readable and not rely on color alone.

## Output Required From The Agent

When this prompt is used, output:
- A complete token table for dark and light.
- CSS variables snippet for both themes.
- Gradient recipes.
- Glow recipes (background and CTA).
- Motion specs (durations, easing, reduced-motion behavior).
- The exact UX behavior for theme toggle and activation reveal.
