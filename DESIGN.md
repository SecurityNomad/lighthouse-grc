---
name: Lighthouse GRC
description: A calm, tactile control surface for governance, risk & compliance work.
colors:
  indigo-primary: "#4f46e5"
  indigo-hover: "#6366f1"
  indigo-active: "#4338ca"
  indigo-focus-dark: "#818cf8"
  canvas-light: "#f1f5f9"
  canvas-dark: "#0f172a"
  panel-light: "#f8fafc"
  panel-dark: "#1e293b"
  ink-light: "#0f172a"
  ink-dark: "#f1f5f9"
  muted: "#64748b"
  subtle: "#94a3b8"
  neu-shadow-light: "#c5ccd6"
  neu-highlight-light: "#ffffff"
  neu-shadow-dark: "#090d17"
  neu-highlight-dark: "#192236"
  danger: "#dc2626"
  sev-critical: "#b91c1c"
  sev-high: "#c2410c"
  sev-medium: "#a16207"
  sev-low: "#15803d"
  info-blue: "#1d4ed8"
  accent-purple: "#7e22ce"
typography:
  display:
    fontFamily: '"Plus Jakarta Sans", Inter, sans-serif'
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  title:
    fontFamily: '"Plus Jakarta Sans", Inter, sans-serif'
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 600
    letterSpacing: "0.05em"
  mono:
    fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "0.75rem"
    fontWeight: 600
rounded:
  pill: "9999px"
  input: "12px"
  card: "16px"
  lg: "20px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
components:
  button-primary:
    backgroundColor: "{colors.indigo-primary}"
    textColor: "#ffffff"
    rounded: "{rounded.input}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.indigo-hover}"
  button-ghost:
    backgroundColor: "{colors.canvas-light}"
    textColor: "{colors.ink-light}"
    rounded: "{rounded.input}"
    padding: "8px 16px"
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "#ffffff"
    rounded: "{rounded.input}"
    padding: "8px 16px"
  input:
    backgroundColor: "{colors.canvas-light}"
    textColor: "{colors.ink-light}"
    rounded: "{rounded.input}"
    padding: "10px 12px"
  card:
    backgroundColor: "{colors.canvas-light}"
    rounded: "{rounded.card}"
    padding: "20px"
  badge:
    rounded: "{rounded.pill}"
    padding: "2px 8px"
---

# Design System: Lighthouse GRC

## 1. Overview

**Creative North Star: "The Quiet Instrument"**

Lighthouse is a precision instrument for people who carry the weight of an organisation's compliance posture. The interface behaves like a well-made control panel: soft, tactile, and quietly confident, never loud. Its signature is **neumorphism** — surfaces that share the exact tone of the canvas behind them and gain form only through a paired shadow-and-highlight, as if pressed up from or into the material. Controls look physically pressable; inputs look physically recessed. The effect is calm and tangible, the opposite of a cold enterprise grid.

The palette is deliberately restrained: a soft slate canvas in both light and dark, one indigo accent that carries every primary action, and a disciplined set of semantic badge colours that are the *only* place bright colour appears. Typography pairs Plus Jakarta Sans (structural, for headings and titles) with Inter (neutral, highly legible, for everything else). Density is real — this is a data tool with tables, dashboards, and forms — but rhythm and generous radii keep it from feeling cramped.

This system explicitly rejects three things (per PRODUCT.md): **enterprise-GRC bloat** (Archer/ServiceNow/OneTrust clutter), the **generic AI-SaaS template** (cream backgrounds, gradient-text heroes, endless identical icon-card grids, uppercase tracked eyebrows), and **crypto/fintech dark-neon** (navy-and-gold, black-and-neon "terminal" hype). Trust here is earned by restraint.

**Key Characteristics:**
- Tonal neumorphism: one canvas colour, form from paired shadow + highlight (not borders).
- One indigo accent for all primary action; colour otherwise reserved for meaning (severity/status).
- Full, first-class dark mode — every surface, shadow, and focus ring has a dark variant.
- Legible under load: dense tables and dashboards kept calm through rhythm, not chrome.
- Soft geometry: generous radii (12–16px), pill filters, rounded badges.

## 2. Colors

A restrained slate-and-indigo system: near-neutral canvas, a single indigo voice for action, and saturated colour reserved strictly for severity and status meaning.

### Primary
- **Signal Indigo** (`#4f46e5`, indigo-600): the one accent. Every primary button, active filter pill, active nav item, table-row hover tint, and focus ring derives from it. Hover lifts to a lighter indigo (`#6366f1`), active presses to a deeper one (`#4338ca`); dark-mode focus rings use `#818cf8` for contrast on the dark canvas.

### Neutral
- **Slate Canvas — Light** (`#f1f5f9`, slate-100): the light-mode body and the base for every raised/inset neumorphic surface. Surfaces are *the same colour as the canvas*; depth comes only from shadow.
- **Slate Canvas — Dark** (`#0f172a`, slate-900): the dark-mode equivalent.
- **Panel** (`#f8fafc` light / `#1e293b` dark, slate-50 / slate-800): modal panels sit slightly off the canvas so overlays read as a distinct layer.
- **Ink** (`#0f172a` on light / `#f1f5f9` on dark): primary text. High-contrast by default — no light-grey body copy.
- **Muted** (`#64748b`, slate-500) / **Subtle** (`#94a3b8`, slate-400): secondary text, captions, table headers, placeholder chevrons. Reserve subtle for genuinely non-essential text; never body copy.
- **Neu Shadow / Highlight**: light mode pairs a cool grey shadow (`#c5ccd6`) with a white highlight (`#ffffff`); dark mode pairs a near-black shadow (`#090d17`) with a lifted highlight (`#192236`). These four values *are* the elevation system (see §4).

### Tertiary — Semantic (severity & status only)
Bright colour appears **only** to encode meaning, always paired with a text label (never colour alone):
- **Critical** red (`#b91c1c`) · **High** orange (`#c2410c`) · **Medium** yellow (`#a16207`) · **Low** green (`#15803d`) — the impact/severity ramp.
- **Info** blue (`#1d4ed8`) · **Accent** purple (`#7e22ce`) · neutral grey — status states (Open / In Treatment / Closed, framework tags, plugin modes). Badges render these as a tinted-100 background with a 700 foreground (dark mode: 900/30 background, 400 foreground).

### Named Rules
**The One Voice Rule.** Indigo is the only non-semantic accent. If an element needs colour and it isn't encoding severity or status, it is indigo or it is neutral — never a second decorative hue.

**The Colour-Means-Something Rule.** Saturated colour is reserved for data meaning. A red thing is a Critical thing; a green thing is a Low/passing thing. Colour is never decoration.

## 3. Typography

**Display Font:** Plus Jakarta Sans (with Inter, sans-serif fallback)
**Body Font:** Inter (with system-ui, sans-serif fallback)
**Label/Mono Font:** ui-monospace stack (SFMono / Menlo) for identifiers only

**Character:** A structural-humanist pairing. Plus Jakarta Sans gives headings a touch more geometry and personality; Inter keeps the dense body text neutral and maximally legible. They contrast on a real axis (structural vs. neutral), not two near-identical sans-serifs.

### Hierarchy
- **Display / Page Title** (Plus Jakarta Sans, 700, 1.5rem/24px, tight `-0.01em`): one per page, the screen's name (`page-title`).
- **Title / Section** (Plus Jakarta Sans, 600, 0.875rem/14px): modal titles, section headers, card headings.
- **Body** (Inter, 400, 0.875rem/14px, line-height 1.5): the workhorse — table cells, descriptions, form values. Cap prose blocks at 65–75ch.
- **Label** (Inter, 600, 0.75rem/12px, `0.05em`, uppercase): form labels and table column headers. Uppercase + tracking is a deliberate *label* signal — not a decorative section eyebrow.
- **Mono** (ui-monospace, 600, 0.75rem/12px): control reference IDs and other codes only.

### Named Rules
**The Label-Not-Eyebrow Rule.** Uppercase tracked text is permitted **only** as a functional form/column label. It must never appear as a decorative kicker above a section heading (that's the AI-SaaS tell PRODUCT.md rejects).

## 4. Elevation

Elevation is the heart of the system: **tonal neumorphism**, not conventional shadows-on-white. Every surface is the same colour as the canvas and gains form from a *paired* light + dark shadow — a dark shadow on the bottom-right, a light highlight on the top-left — so it appears extruded from (raised) or pressed into (inset) the material. There are effectively no borders; depth carries structure. Both modes are first-class: light mode uses `#c5ccd6` / `#ffffff`, dark mode uses `#090d17` / `#192236`.

### Shadow Vocabulary
- **Raised — card** (`6px 6px 14px shadow, -6px -6px 14px highlight`): cards, panels, table wrappers. The default resting state for content containers.
- **Raised — small** (`4px 4px 8–10px …`): smaller cards, ghost buttons, pills.
- **Inset** (`inset 3px 3px 7px …`): inputs, selects, search bars — anything you type or press *into*.
- **Pressed** (`inset 2px 2px 5px …`): the `:active` state of a ghost button and the active filter pill; the control physically depresses.
- **Accent glow** (`0 4px 14px rgba(99,102,241,0.35)`): the one non-neumorphic shadow — the indigo primary button floats on a soft coloured glow, lifting `translateY(-1px)` on hover.

### Named Rules
**The Same-Tone Rule.** Surfaces never differ in fill colour from their canvas; if you're reaching for a lighter/darker background to separate a card, use the neumorphic shadow pair instead. (Exception: modal panels, which intentionally shift one step to read as an overlay layer.)

**The Raised-or-Inset Rule.** Interactive elements declare their nature through depth: things you press are raised and depress on `:active`; things you fill are inset. Never flat.

## 5. Components

### Buttons
- **Shape:** soft rectangles, 12px radius (`rounded-xl`).
- **Primary (`btn-primary`):** Signal Indigo (`#4f46e5`) fill, white text, 600 weight, `8px 16px` padding, resting on an indigo glow (`0 4px 14px rgba(99,102,241,0.35)`). Hover lightens to `#6366f1`, deepens the glow, and lifts `translateY(-1px)`; active presses to `#4338ca`. Disabled drops to 50% opacity.
- **Ghost (`neu-btn`):** canvas-tone fill, raised neu shadow, slate-700 text. Hover deepens the shadow; active insets it (the button physically presses in). This is the default secondary/cancel action.
- **Danger (`btn-danger`):** red-600 (`#dc2626`) fill, white text — destructive actions only.

### Filter Pills (chips)
- **Inactive (`neu-pill`):** raised, canvas-tone, pill radius, muted text; hover darkens the text.
- **Active (`neu-pill-active`):** indigo-600 fill, white text, *inset* shadow so the selected pill reads as pressed-in. Used for status/severity filter rows.

### Cards / Containers (`neu-card`)
- **Corner Style:** 16px radius (`rounded-2xl`); small variant 12px.
- **Background:** canvas tone (same as body).
- **Shadow Strategy:** Raised — card (see §4). This *is* the border; do not add one.
- **Internal Padding:** 20px (`p-5`) typical.

### Inputs / Fields (`neu-input`, `neu-select`)
- **Style:** inset neu shadow (recessed), canvas-tone fill, 12px radius, no border.
- **Focus:** the inset shadow persists and a 2px indigo ring is added (`#6366f1` light / `#818cf8` dark). Focus is always visible.
- **Select:** same treatment with a custom slate chevron; native appearance removed.

### Navigation (Sidebar)
- **Style:** a fixed dark slate-900 rail (dark in both themes), collapsible with persisted state. Nav items are 14px Inter; **active** item is a solid indigo-600 pill with white text; hover fills slate-800. Collapsed state shows icon-only items plus a client-context indicator.

### Tables (`neu-table`)
- Wrapped in a `neu-card` (rounded, raised, `overflow-hidden`). Column headers are uppercase Label type in muted colour; rows separate with hairline dividers and tint **indigo-50/40** (light) / **indigo-950/30** (dark) on hover. Right-aligned row actions reveal on hover.

### Badges (`badge`)
- Pill-shaped, 12px semibold, tinted-100 background + 700 foreground (light) / 900-30 + 400 (dark). One badge class per semantic role (red/orange/yellow/green/blue/purple/indigo/gray). Always carries a text label.

## 6. Do's and Don'ts

### Do:
- **Do** convey elevation with the paired neu shadow (`6px 6px 14px #c5ccd6, -6px -6px 14px #ffffff` and its dark twin), not with a border or a different-coloured fill.
- **Do** keep indigo as the single action voice; reach for neutral or indigo before any other hue (**The One Voice Rule**).
- **Do** reserve saturated colour for severity/status meaning, always paired with a text label — never colour alone (colour-blind safe).
- **Do** give every interactive element a visible `:focus-visible` state (the 2px indigo ring) and every surface a dark-mode variant.
- **Do** keep body text at Ink contrast (≥4.5:1); if a grey feels "elegant," it's probably failing contrast — bump it toward Ink.
- **Do** provide a `prefers-reduced-motion` alternative for the button lift, row-hover, and any entrance (crossfade or instant).

### Don't:
- **Don't** build **enterprise-GRC bloat** — dense border-grid tables, chrome-heavy toolbars, config-maze panels (Archer/ServiceNow/OneTrust). Let whitespace and depth do the work.
- **Don't** ship the **generic AI-SaaS template**: no cream/sand backgrounds, no gradient/`background-clip:text` headings, no endless identical icon-card grids, and no tiny uppercase tracked eyebrow above sections (uppercase tracking is for functional labels only — **The Label-Not-Eyebrow Rule**).
- **Don't** drift toward **crypto/fintech dark-neon** — no navy-and-gold, no black-and-neon glow, no "trading terminal" theatrics. The dark mode is a calm slate, not a hype surface.
- **Don't** add gamified/consumer touches (badges-as-rewards, confetti) that undercut credibility with auditors and CISOs.
- **Don't** put a fill-colour difference *and* a neu shadow on the same card; pick depth. And never nest a raised card inside another raised card.
- **Don't** use `border-left`/`border-right` >1px as a coloured accent stripe on cards, rows, or alerts — use a full treatment or a badge instead.
