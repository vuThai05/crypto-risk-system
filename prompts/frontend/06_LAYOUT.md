# 06_LAYOUT.md

Use this prompt to define Phase 1 layout rules. This file focuses on page structure, placement, sizing, responsiveness, and empty-space control. It does not define final visual styling; `02_DESIGN.md` will own visual direction.

## Prompt

You are a senior product-minded frontend engineer designing the Phase 1 layout system for the Crypto Risk System.

Project context:
- Phase 1 should not feel like a sparse admin dashboard.
- The main page centers on an interactive risk bubble map for top-100 coins.
- Supporting panels must explain market state, filters, selected coin details, and data freshness.
- The UI must work on desktop, tablet, and mobile.

## Global Layout Model

Use a "risk cockpit" layout:

```txt
top command bar
left filter rail | center main stage | right insight rail
bottom status strip
```

The center main stage owns the primary experience. Rails support it; they should not compete with it.

## Desktop Layout

Target width: `1280px` and above.

Suggested measurements:
- Top command bar: `56-64px` high, full width.
- Left filter rail: `240-280px` wide.
- Right insight rail: `320-380px` wide.
- Bottom status strip: `44-56px` high, full width.
- Center stage: fills all remaining width and height.

Placement:
- Search and primary refresh action live in the top command bar.
- Risk filters live in the left rail.
- Market weather and selected coin summary live in the right rail.
- Bubble canvas lives in the center and should visually dominate the viewport.
- Freshness/model status lives in the bottom strip and right rail.

## Tablet Layout

Target width: `768px` to `1279px`.

Rules:
- Keep top command bar fixed-height.
- Collapse the left filter rail into a drawer or sheet.
- Keep the right insight rail visible only if width allows; otherwise collapse it into a drawer.
- Center bubble canvas should keep priority over side panels.
- Bottom status strip can become a compact two-line area if needed.

## Mobile Layout

Target width: below `768px`.

Rules:
- Top command bar becomes compact.
- Filter rail becomes a bottom sheet.
- Insight rail becomes a slide-over panel.
- Bubble canvas should appear first and remain large enough to be useful.
- If labels become crowded, show labels only for the largest bubbles and use tap/tooltip for the rest.
- Coin dossier opens as a full-height sheet or route-level page.

## Main Stage Rules

For `RiskBubbleCanvas`:
- Do not wrap it in a decorative card.
- Give it a functional viewport boundary only if needed for controls or hit testing.
- It should fill the available center stage.
- It must resize with the viewport without changing surrounding layout dimensions.
- Use stable dimensions so hover and selection do not shift the page.

For empty data:
- Keep the main stage occupied.
- Show a centered empty state with a setup path: start worker, trigger ingestion, or check data freshness.
- Keep side rails visible so the page does not collapse into whitespace.

## Rail Rules

Left rail:
- Use compact grouped controls.
- Avoid long explanatory copy.
- Keep controls scrollable if height is limited.

Right rail:
- Top section: market weather.
- Middle section: selected coin or top extreme coins.
- Bottom section: data freshness/model info.
- If no coin is selected, show market-level insight rather than leaving the rail empty.

Bottom strip:
- Keep text short and stable.
- Show last market timestamp, last risk computation timestamp, stale status, and model version when available.

## Layering And Z-Index

Suggested order:
- Canvas: base layer.
- Tooltip: above canvas.
- Command bar and rails: above canvas.
- Drawers/sheets: above rails.
- Modal-level errors, if any: highest.

Do not let tooltips cover command controls or drawer controls.

## Scroll And Overflow

- The whole app shell should not require horizontal scrolling.
- Rails may scroll independently.
- The center canvas should resize instead of forcing page overflow.
- On mobile, avoid nested scroll traps in sheets.

## Output Required From The Agent

When this prompt is used, output:
- Layout regions and dimensions.
- Responsive behavior by breakpoint.
- Which components live in each region.
- Empty-state placement rules.
- Overflow and z-index rules.
- Any CSS grid/flex strategy needed to implement the app shell.

## Acceptance Criteria

- The main bubble map does not feel like an embedded preview.
- Desktop view has no large dead zones.
- Mobile view starts with the usable risk map, not a marketing section.
- Rails collapse gracefully without losing key actions.
- Empty and stale states still occupy the page intentionally.
