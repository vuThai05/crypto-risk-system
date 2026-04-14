# 01_TECH_STACK.md

Use this prompt to choose and enforce the Phase 1 frontend stack for the Crypto Risk System.

## Prompt

You are a senior frontend engineer designing the Phase 1 frontend for an existing crypto market risk analytics backend.

Project context:
- Backend exists in this repo as a FastAPI modular monolith.
- API prefix is `/api/v1`.
- Current endpoints include:
  - `GET /market-risk`
  - `GET /top-risky-assets?limit=...`
  - `GET /coins/{coin_id}/risk`
  - `POST /trigger-ingestion`
- Current data model includes top-100 coins, market snapshots, OHLCV candles, feature metrics, risk metrics, and market aggregates.
- Risk is not price prediction. It is a market/asset risk signal derived from volatility, drawdown, and average return.
- CoinGecko is on a free/demo budget. The frontend must never call CoinGecko directly.
- Phase 1 primary experience is a risk bubble map, inspired by Crypto Bubbles, but focused on risk intelligence rather than pure price performance.

## Required Stack Decision

Use:
- React + Vite + TypeScript for the app shell.
- React Router for client-side routing.
- TanStack Query for server state, caching, polling, retries, and mutations.
- Zustand only for cross-page UI state that would otherwise become awkward with props, such as selected coin, global filters, and panel state.
- Plain CSS with CSS variables and component-scoped CSS files. Do not add a large UI kit in Phase 1.
- D3 modules for visualization math:
  - `d3-force` for bubble layout/collision.
  - `d3-scale` for radius and color scales.
- Canvas for the main bubble board. Use SVG only for small static legends or meters.
- Vitest + React Testing Library for unit/component tests.
- Playwright later for smoke/visual checks once the app shell exists.

## Environment Contract

Use:
- `VITE_API_BASE_URL=http://localhost:8000/api/v1` as the local default.
- All API calls must go through a typed frontend API client.
- The frontend must tolerate backend Decimal fields encoded as either numbers or strings.

## Do Not Use In Phase 1

- Do not use Next.js unless there is a confirmed SSR/SEO requirement.
- Do not call CoinGecko directly from the browser.
- Do not use Redux for Phase 1.
- Do not add a full UI component framework just to get cards, buttons, and inputs.
- Do not introduce WebSockets until the backend supports event streams.
- Do not make price charts the center of the product.

## Suggested App Structure

```txt
frontend/
  src/
    app/
      App.tsx
      router.tsx
      providers.tsx
    api/
      client.ts
      riskApi.ts
      types.ts
      normalizers.ts
    state/
      useRiskMapStore.ts
    components/
      bubble/
      controls/
      data-trust/
      dossier/
      layout/
      market/
    pages/
      RiskMapPage.tsx
      CoinDossierPage.tsx
      MarketPage.tsx
      OpsPage.tsx
    styles/
      tokens.css
      globals.css
```

## Output Required From The Agent

When this prompt is used, output:
- The chosen stack and why it fits this project.
- The dependency list split into required and optional.
- The frontend folder structure.
- The runtime environment variables.
- The tradeoffs and constraints caused by the CoinGecko free/demo budget.
- Any backend API additions needed before the frontend can be complete.

## Acceptance Criteria

- The stack supports a 100-coin interactive bubble map smoothly.
- The browser never spends CoinGecko quota.
- Data fetching is cacheable, typed, and resilient to stale data.
- The stack stays lightweight enough for a small Phase 1 app.
- The implementation can grow into Phase 2 without a rewrite.
