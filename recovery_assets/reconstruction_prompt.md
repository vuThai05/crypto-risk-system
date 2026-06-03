# CRYPTO RISK SYSTEM FRONTEND RECONSTRUCTION

You are continuing an existing frontend recovery and reconstruction project.

IMPORTANT:

The original frontend source code was accidentally deleted.

The project was successfully rebuilt once before, but a cleanup operation deleted most of the regenerated frontend source.

This is NOT a greenfield project.

This is NOT a redesign project.

This is NOT an architecture rewrite.

Your mission is to reconstruct the lost frontend as faithfully as possible using all surviving artifacts and previous project context.

---

# ABSOLUTE SAFETY RULES

DO NOT:

* delete files
* remove folders
* clean repositories
* move files
* rename directories
* overwrite large sections of code
* perform repository maintenance
* perform cleanup operations

unless explicitly instructed.

Your only objective is reconstruction.

---

# AVAILABLE RECOVERY ASSETS

Inspect EVERYTHING inside:

recovery_assets/

before generating any code.

The folder contains:

## Screenshots

screenshots/risk-dashboard.png

screenshots/markets.png

screenshots/risk-trends.png

screenshots/analytics.png

These screenshots are the PRIMARY visual source of truth.

---

## Recovered Build Artifacts

next_artifacts/layout.css

next_artifacts/analytics_page.js

next_artifacts/markets_page.js

next_artifacts/risk_dashboard_page.js

next_artifacts/risk_trends_page.js

These files contain recovered build output and should be analyzed before reconstruction.

Use them to infer:

* component hierarchy
* JSX structure
* chart usage
* data flow
* route composition
* shared components
* naming conventions

---

## Recovered Next.js Build Data

next_server_app/

next_static_chunks/

Use them as additional reconstruction references.

---

# EXISTING FRONTEND STRUCTURE

The existing frontend folder structure already exists.

Use the current structure.

DO NOT redesign the project structure.

Expected structure:

frontend_v2/

src/

app/

analytics/

markets/

risk-dashboard/

risk-trends/

components/

charts/

layout/

market-overview/

ui/

hooks/

lib/

services/

styles/

Continue building inside this structure.

---

# UI-UX-PRO-MAX REQUIREMENT

A custom design skill exists inside:

.agent/ui-ux-pro-max

You MUST use this skill throughout the reconstruction process.

Use it to improve:

* spacing consistency
* typography hierarchy
* visual rhythm
* information density
* component polish
* hover states
* empty states
* loading states
* responsive behavior
* visual hierarchy

HOWEVER:

Do NOT redesign the product.

Do NOT change layout structure.

Do NOT change route hierarchy.

Do NOT introduce a new visual identity.

The skill should be used for refinement and polish only.

The screenshots remain the visual source of truth.

Goal:

The rebuilt frontend should feel like the original frontend designed by a stronger UI/UX engineer.

---

# PROJECT DESCRIPTION

Project Name:

Crypto Risk System

Purpose:

Enterprise crypto market risk analytics platform.

Target Users:

* crypto analysts
* researchers
* traders
* market observers

Style:

* enterprise fintech SaaS
* institutional analytics platform
* modern risk console
* professional dashboard

Inspirations:

* Coinbase Institutional
* Stripe Dashboard
* Vercel
* Linear
* Bloomberg Terminal (modernized)

Avoid:

* cyberpunk
* neon themes
* gaming UI
* crypto casino aesthetics
* excessive gradients
* flashy effects

---

# ROUTES

Preserve exactly:

/risk-dashboard

/markets

/risk-trends

/analytics

Do not rename routes.

Do not introduce alternative routes.

---

# BACKEND API CONTRACT

Available endpoints:

GET /api/v1/health

GET /api/v1/market-risk

GET /api/v1/coins/{coin_id}/risk

GET /api/v1/top-risky-assets

POST /api/v1/trigger-ingestion

Use these endpoints.

Do not invent additional APIs.

---

# PAGE REQUIREMENTS

## Risk Dashboard

Must contain:

* KPI cards
* risk distribution
* top risk assets
* market summary
* quick navigation

Match screenshots closely.

---

## Markets

Must contain:

* market table
* search
* sorting
* filtering
* watchlist
* watchlist-only filter
* risk badges

Each row must support watchlist toggling via star icon.

Match screenshots closely.

---

## Risk Trends

Must contain:

* timeline chart
* coin selector
* watchlist filter
* largest movers panel

Match screenshots closely.

---

## Analytics

Must contain:

* KPI cards
* market risk timeline
* risk distribution
* data quality section

Match screenshots closely.

---

# TECH STACK

Next.js App Router

TypeScript

TailwindCSS

shadcn/ui

TanStack Table

Lucide React

Recharts

React Query

---

# RECONSTRUCTION PRIORITY

If multiple sources disagree:

Priority 1:
Screenshots

Priority 2:
Recovered page.js artifacts

Priority 3:
layout.css

Priority 4:
Next.js build artifacts

Priority 5:
Previous conversation context

---

# IMPLEMENTATION ORDER

Step 1:
Inspect recovery_assets

Step 2:
Analyze architecture

Step 3:
Reconstruct layout.tsx

Step 4:
Reconstruct navigation

Step 5:
Reconstruct shared components

Step 6:
Reconstruct Markets

Step 7:
Reconstruct Risk Dashboard

Step 8:
Reconstruct Risk Trends

Step 9:
Reconstruct Analytics

Step 10:
UI/UX polish using ui-ux-pro-max

---

# OUTPUT REQUIREMENT

Before generating code:

Provide a reconstruction plan based on discovered artifacts.

Then rebuild incrementally.

After each major milestone:

STOP

and wait for confirmation before proceeding.

Do not generate the entire frontend blindly in one pass.

The goal is maximum reconstruction fidelity, not speed.