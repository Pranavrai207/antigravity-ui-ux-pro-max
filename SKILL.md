---
name: ui-ux-pro-max
description: UI/UX design intelligence with searchable database
---
# ui-ux-pro-max

Comprehensive design guide for web and mobile applications. Contains 67 styles, 96 color palettes, 57 font pairings, 99 UX guidelines, and 25 chart types across 13 technology stacks. Searchable database with priority-based recommendations.

## Prerequisites

Check if Python is installed:

```bash
python3 --version || python --version
```

If Python is not installed, install it based on user's OS:

**macOS:**
```bash
brew install python3
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install python3
```

**Windows:**
```powershell
winget install Python.Python.3.12
```

---

## ⚡ MANDATORY FIRST STEP — Run Before Writing Any Code

**ALWAYS run the design system script BEFORE writing a single line of HTML/CSS/JS.**
If this step is skipped, the output will be inconsistent, low-quality, and non-replicable.

### Finding the Script Path

The script path depends on where the skill is installed. Detect it dynamically:

```bash
# Step 1: Find where search.py actually lives
SKILL_SCRIPT=$(find . -path "*/ui-ux-pro-max/scripts/search.py" 2>/dev/null | head -1)

# Step 2: Verify it was found
echo "Found: $SKILL_SCRIPT"

# Step 3: Use it
python3 "$SKILL_SCRIPT" "your query here" --design-system -p "Project Name"
```

**Common install locations to try if find fails:**
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "query" --design-system 2>/dev/null || \
python3 ui-ux-pro-max/scripts/search.py "query" --design-system 2>/dev/null || \
python3 ./scripts/search.py "query" --design-system
```

**CRITICAL:** If script cannot be found or throws an error → fix the path FIRST. Do NOT skip the design system step and start writing code from scratch. That leads to inconsistent, broken output.

---

## How to Use This Skill

When user requests UI/UX work (design, build, create, implement, review, fix, improve), follow this workflow:

### Step 1: Analyze User Requirements

Extract key information from user request:
- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page, etc.
- **Style keywords**: minimal, playful, professional, elegant, dark mode, etc.
- **Industry**: healthcare, fintech, gaming, education, etc.
- **Stack**: React, Vue, Next.js, or default to `html-vanilla` for plain HTML/CSS/JS

### Step 2: Generate Design System (REQUIRED — DO NOT SKIP)

**Always start with `--design-system`** to get comprehensive recommendations with reasoning:

```bash
python3 "$SKILL_SCRIPT" "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

This command:
1. Searches 5 domains in parallel (product, style, color, landing, typography)
2. Applies reasoning rules from `ui-reasoning.csv` to select best matches
3. Returns complete design system: pattern, style, colors, typography, effects
4. Includes anti-patterns to avoid

**Example:**
```bash
python3 "$SKILL_SCRIPT" "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### Step 2b: Persist Design System (Master + Overrides Pattern)

To save the design system for hierarchical retrieval across sessions, add `--persist`:

```bash
python3 "$SKILL_SCRIPT" "<query>" --design-system --persist -p "Project Name"
```

This creates:
- `design-system/MASTER.md` — Global Source of Truth with all design rules
- `design-system/pages/` — Folder for page-specific overrides

**With page-specific override:**
```bash
python3 "$SKILL_SCRIPT" "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

**How hierarchical retrieval works:**
1. When building a specific page (e.g., "Checkout"), first check `design-system/pages/checkout.md`
2. If the page file exists, its rules **override** the Master file
3. If not, use `design-system/MASTER.md` exclusively

### Step 3: Supplement with Detailed Searches (as needed)

After getting the design system, use domain searches to get additional details:

```bash
python3 "$SKILL_SCRIPT" "<keyword>" --domain <domain> [-n <max_results>]
```

**When to use detailed searches:**

| Need | Domain | Example |
|------|--------|---------|
| More style options | `style` | `--domain style "glassmorphism dark"` |
| Chart recommendations | `chart` | `--domain chart "real-time dashboard"` |
| UX best practices | `ux` | `--domain ux "animation accessibility"` |
| Alternative fonts | `typography` | `--domain typography "elegant luxury"` |
| Landing structure | `landing` | `--domain landing "hero social-proof"` |

### Step 4: Stack Guidelines

Get implementation-specific best practices.

```bash
python3 "$SKILL_SCRIPT" "<keyword>" --stack html-tailwind
```

Available stacks: `html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`

---

## ⚡ FIRST-RUN PERFECTION RULES (MANDATORY)

**These rules MUST be followed on every project from the FIRST iteration. No second chances. No "we'll fix it later." The output must be production-grade immediately.**

### Rule 1: ZERO Inline Styles for Layout

**NEVER use inline `style="..."` for font-size, display, flex, or grid properties.**

| ❌ NEVER DO THIS | ✅ ALWAYS DO THIS |
|---|---|
| `<h1 style="font-size: 6rem">` | `h1 { font-size: clamp(2rem, 8vw, 6rem); }` |
| `<div style="display: flex; gap: 4rem">` | `.timeline-item { display: flex; gap: 4rem; }` |
| `<div style="font-size: 4rem">` | Use global `h1/h2/h3` with `clamp()` |

**Why:** Inline styles cannot be overridden by media queries. This is the #1 cause of mobile breakage.

**The only acceptable inline styles are:**
- `text-align: center` (non-layout cosmetic)
- `margin-bottom` for one-off spacing adjustments
- `max-width` + `margin: 0 auto` for content constraining
- `opacity` for cosmetic dimming

### Rule 2: Fluid Typography from Day One

**Every heading MUST use `clamp()` in CSS. Never hardcode font sizes.**

```css
/* MANDATORY in every project's CSS */
h1 { font-size: clamp(2rem, 8vw, 6rem); }
h2 { font-size: clamp(1.6rem, 5vw, 4rem); }
h3 { font-size: clamp(1.3rem, 3vw, 2.5rem); }
body { font-size: clamp(0.9rem, 1.5vw, 1.1rem); }
```

### Rule 3: Mobile-First Architecture

**Build for 360px FIRST, then enhance for desktop.** Every project must include these breakpoints from the initial CSS:

```css
/* Base styles = Mobile (360px) */

/* Tablet */
@media (min-width: 768px) { ... }

/* Desktop */
@media (min-width: 1024px) { ... }

/* Large Desktop */
@media (min-width: 1440px) { ... }
```

**Mandatory mobile patterns (include from the start):**
- Single-column grid on mobile (`grid-template-columns: 1fr`)
- Hamburger menu for navigation (not just hidden desktop nav)
- Stacked layouts for side-by-side content (timelines, comparison cards)
- Touch-friendly button sizes (min 44x44px, min-height: 48px)
- Reduced padding on mobile (2rem → 1rem for containers)

### Rule 4: Complete SEO & Meta on Every Page

**Every HTML page MUST have these from the first commit:**

```html
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="shortcut icon" href="favicon.png" type="image/x-icon">
  <title>[Page-Specific Title] | [Brand Name]</title>
  <meta name="description" content="[Compelling 150-char description]" />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:title" content="[Title]" />
  <meta property="og:description" content="[Description]" />
  <meta property="og:image" content="[Image URL]" />
</head>
```

### Rule 5: Accessibility Built-In (Not Bolted On)

**Every interactive element MUST have these from the start:**

```html
<!-- Navigation -->
<ul class="nav-links" role="navigation">
  <li><a href="/" aria-current="page">Home</a></li>
</ul>

<!-- Hamburger -->
<button class="hamburger" aria-label="Toggle navigation menu" aria-expanded="false">

<!-- Images -->
<img src="photo.jpg" alt="Red Ferrari SF90 Spider on display">

<!-- Forms -->
<label for="email">Email Address</label>
<input id="email" type="email" required>
```

### Rule 6: Premium UI Defaults

**Every project MUST include these CSS utilities from the start:**

```css
/* Custom Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 4px; }

/* Smooth Scroll */
html { scroll-behavior: smooth; }

/* Selection Color */
::selection { background: var(--accent); color: white; }

/* Focus Visible */
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* Reduced Motion — MANDATORY */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  .reveal { opacity: 1; transform: none; }
}
```

### Rule 7: Form UX Must Be Functional

**Forms must NEVER be dead-end HTML.** Always include:
- Client-side validation with clear per-field error states
- Validate on `blur` + re-validate on `input` if field has error
- Loading state on submit button ("Sending...")
- Success confirmation message after submission
- `preventDefault()` to stop page reload
- `role="alert"` or `aria-live="polite"` on error/success messages

### Rule 8: No External Dependencies for Brand Assets

**NEVER link to external URLs for logos, brand images, or critical assets.**
- Generate or create local SVG/CSS-based logos
- Store all images in a local `assets/` folder
- Use `generate_image` tool for hero images if needed

### Rule 9: Design System CSS Variables

**Every project MUST define a complete design token system before writing any component.
Use this EXACT spacing scale — it matches the generated MASTER.md:**

```css
:root {
  /* Colors */
  --bg-primary: #0a0a0a;
  --bg-secondary: #111111;
  --bg-card: #1a1a1a;
  --bg-glass: rgba(255,255,255,0.04);
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
  --text-muted: #5a5a5a;
  --accent: #dc2626;
  --accent-hover: #ef4444;
  --accent-glow: rgba(220,38,38,0.2);
  --border: rgba(255,255,255,0.1);
  --border-strong: rgba(255,255,255,0.3);

  /* Spacing — 8px base, doubling scale */
  --space-xs: 0.5rem;   /* 8px   */
  --space-sm: 1rem;     /* 16px  */
  --space-md: 2rem;     /* 32px  */
  --space-lg: 4rem;     /* 64px  */
  --space-xl: 8rem;     /* 128px */

  /* Typography */
  --font-display: 'DisplayFont', sans-serif;
  --font-heading: 'HeadingFont', sans-serif;
  --font-body: 'Inter', sans-serif;

  /* Transitions */
  --transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --transition-slow: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);

  /* Shadows */
  --shadow-sm: 0 2px 10px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 20px rgba(0,0,0,0.5);
  --shadow-lg: 0 10px 40px rgba(0,0,0,0.8);
  --shadow-accent: 0 0 30px rgba(220,38,38,0.2);

  /* Layout */
  --nav-h: 72px;
  --container-max: 1400px;
}
```

### Rule 10: Scroll Animations from the Start

**Every section MUST have entrance animations using IntersectionObserver:**

```javascript
// MANDATORY in every project's main.js
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
```

```css
/* MANDATORY reveal animation */
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}
.reveal.active {
  opacity: 1;
  transform: translateY(0);
}
.reveal:nth-child(2) { transition-delay: 0.1s; }
.reveal:nth-child(3) { transition-delay: 0.2s; }
.reveal:nth-child(4) { transition-delay: 0.3s; }
```

---

### Rule 11: CSS Architecture — Pick ONE, Never Mix ⚠️

**This is the #1 cause of silently broken layouts. Every class in HTML MUST exist in CSS.**

#### Option A — Vanilla CSS (DEFAULT for plain HTML/CSS/JS projects)

```css
/* style.css — named semantic component classes */
.navbar { ... }
.hero-section { ... }
.model-card { ... }
.btn-primary { ... }
.footer { ... }
```

```html
<!-- HTML uses ONLY classes defined in style.css above -->
<nav class="navbar">
  <div class="model-card">
    <a class="btn-primary">Click</a>
  </div>
</nav>
```

#### Option B — Tailwind CSS (ONLY if Tailwind CDN or tailwind.config.js is present)

```html
<!-- Tailwind utility classes ONLY when Tailwind is actually installed -->
<nav class="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl">
  <div class="max-w-7xl mx-auto px-4 flex items-center justify-between h-18">
```

#### ❌ FORBIDDEN — Never Mix These Two

```html
<!-- BROKEN: Tailwind class names WITHOUT Tailwind installed -->
<!-- These classes do NOTHING in plain CSS and silently break layout -->
<div class="max-w-[800px] text-gray-300 p-8 lg:grid-cols-3 lg-order-1">
<p class="size-xs opacity-50 text-right border-glass">
```

**Decision rule:**
- User shows `tailwind.config.js` or `<script src="cdn.tailwindcss.com">` → Option B
- User has a plain `style.css` → Option A
- User didn't specify → **Default to Option A**

**Self-check before writing HTML:** mentally open your style.css and confirm every class name you are about to type in HTML has a corresponding CSS rule. If it doesn't exist in the CSS → don't use it.

---

### Rule 12: Multi-Page Consistency — Nav & Footer Identical Everywhere ⚠️

**When building a multi-page site, nav and footer are NEVER simplified for inner pages.**

#### Build Order (follow this exactly):
1. Write nav HTML once
2. Write footer HTML once (complete — with nav columns, social links, copyright)
3. Copy both to ALL pages before writing any page content
4. Only change `aria-current="page"` on the active nav link per page
5. Write page-specific content last

#### MANDATORY on every single page:

```html
<!-- NAV — identical on all pages, only aria-current changes -->
<nav class="navbar" id="navbar" role="navigation" aria-label="Main navigation">
  <a href="index.html" class="nav-logo" aria-label="Brand Home">BRAND</a>
  <button class="hamburger" id="hamburger" aria-label="Toggle navigation menu" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>
  <ul class="nav-links" id="nav-links">
    <li><a href="index.html">Home</a></li>
    <li><a href="models.html">Models</a></li>
    <li><a href="about.html">About</a></li>
    <li><a href="contact.html">Contact</a></li>
  </ul>
</nav>

<!-- FOOTER — COMPLETE on every page, never a "lite" version -->
<footer class="footer" role="contentinfo">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <!-- Logo + address -->
      </div>
      <nav class="footer-nav" aria-label="Footer navigation">
        <div class="footer-col">
          <h4>COLUMN 1</h4>
          <ul>...</ul>
        </div>
        <div class="footer-col">
          <h4>COLUMN 2</h4>
          <ul>...</ul>
        </div>
        <div class="footer-col">
          <h4>COLUMN 3</h4>
          <ul>...</ul>
        </div>
      </nav>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2025 Brand Name. All rights reserved.</p>
      <div class="footer-social" aria-label="Social media links">
        <!-- Social icon links -->
      </div>
    </div>
  </div>
</footer>
```

**Anti-patterns — NEVER do these:**
```html
<!-- ❌ Bare footer on inner pages -->
<footer>
  <p>&copy; 2025 Brand Name.</p>
</footer>

<!-- ❌ Missing CTA section on inner pages -->
<!-- Every inner page needs a CTA section before the footer -->
```

---

## Stack Selection Guide

**Choosing the wrong stack causes broken CSS. Use this decision table:**

| Project Setup | Correct Stack |
|---|---|
| Plain HTML + hand-written CSS | **Option A (Vanilla CSS)** — no Tailwind classes |
| HTML + Tailwind CDN in `<head>` | **Option B (Tailwind)** |
| HTML + `tailwind.config.js` + PostCSS | **Option B (Tailwind)** |
| React without Tailwind | `react` stack guidelines |
| React with Tailwind | `react` stack + Tailwind utilities |
| Next.js | `nextjs` stack guidelines |

**Default when not specified → Vanilla CSS (Option A)**

---

## Search Reference

### Available Domains

| Domain | Use For | Example Keywords |
|--------|---------|------------------|
| `product` | Product type recommendations | SaaS, e-commerce, portfolio, healthcare, beauty, service |
| `style` | UI styles, colors, effects | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | Font pairings, Google Fonts | elegant, playful, professional, modern |
| `color` | Color palettes by product type | saas, ecommerce, healthcare, beauty, fintech, service |
| `landing` | Page structure, CTA strategies | hero, hero-centric, testimonial, pricing, social-proof |
| `chart` | Chart types, library recommendations | trend, comparison, timeline, funnel, pie |
| `ux` | Best practices, anti-patterns | animation, accessibility, z-index, loading |
| `react` | React/Next.js performance | waterfall, bundle, suspense, memo, rerender, cache |
| `web` | Web interface guidelines | aria, focus, keyboard, semantic, virtualize |
| `prompt` | AI prompts, CSS keywords | (style name) |

### Available Stacks

| Stack | Focus |
|-------|-------|
| `html-tailwind` | Tailwind utilities, responsive, a11y (requires Tailwind installed) |
| `react` | State, hooks, performance, patterns |
| `nextjs` | SSR, routing, images, API routes |
| `vue` | Composition API, Pinia, Vue Router |
| `svelte` | Runes, stores, SvelteKit |
| `swiftui` | Views, State, Navigation, Animation |
| `react-native` | Components, Navigation, Lists |
| `flutter` | Widgets, State, Layout, Theming |
| `shadcn` | shadcn/ui components, theming, forms, patterns |
| `jetpack-compose` | Composables, Modifiers, State Hoisting, Recomposition |

---

## Common Rules for Professional UI

### Icons & Visual Elements

| Rule | Do | Don't |
|------|----|----- |
| **No emoji icons** | Use SVG icons (Heroicons, Lucide, Simple Icons) | Use emojis like 🎨 🚀 ⚙️ as UI icons |
| **Stable hover states** | Use color/opacity transitions on hover | Use scale transforms that shift layout |
| **Correct brand logos** | Research official SVG from Simple Icons | Guess or use incorrect logo paths |
| **Consistent icon sizing** | Use fixed viewBox (24x24) | Mix different icon sizes randomly |

### Interaction & Cursor

| Rule | Do | Don't |
|------|----|----- |
| **Cursor pointer** | Add `cursor: pointer` to all clickable cards | Leave default cursor on interactive elements |
| **Hover feedback** | Provide visual feedback (color, shadow, border) | No indication element is interactive |
| **Smooth transitions** | Use `transition: all 0.3s cubic-bezier(...)` | Instant state changes or too slow (>500ms) |

### Layout & Spacing

| Rule | Do | Don't |
|------|----|----- |
| **Floating navbar** | Add proper top offset for content | Let content hide behind fixed elements |
| **Content padding** | Use `padding-top: var(--nav-h)` on first section | Hardcode navbar offset per page |
| **Consistent max-width** | Use `--container-max` variable throughout | Mix different container widths |

---

## Pre-Delivery Checklist

Before delivering UI code, verify ALL of these:

### ⚠️ CSS Architecture (New)
- [ ] ONE CSS approach only — Vanilla OR Tailwind, never mixed
- [ ] Every class name used in HTML exists as a rule in style.css
- [ ] No Tailwind utility names (p-8, text-gray-300, max-w-[...]) without Tailwind installed
- [ ] No inline `style=""` for layout properties (flex, grid, font-size, display)

### ⚠️ Multi-Page Consistency (New)
- [ ] Navbar HTML **identical** on all pages (only `aria-current` changes)
- [ ] Footer **complete and identical** on ALL pages — no simplified inner page footer
- [ ] CTA section before footer on every page
- [ ] Favicon linked on every page
- [ ] Every page has unique `<title>`, `<meta description>`, and OG tags

### First-Run Perfection ⚡
- [ ] ALL headings use `clamp()` — zero hardcoded font sizes
- [ ] Mobile hamburger implemented, functional, and toggles `aria-expanded`
- [ ] All grids collapse to single-column on mobile (360px)
- [ ] CSS variables defined for all design tokens
- [ ] Custom scrollbar styled
- [ ] `prefers-reduced-motion` media query included
- [ ] Scroll reveal (`.reveal` + IntersectionObserver) on every section
- [ ] Forms: per-field validation + loading state + success message
- [ ] All assets local (no external dependencies for critical assets)

### Visual Quality
- [ ] No emojis used as icons (SVG only)
- [ ] Hover states don't cause layout shift
- [ ] All colors use CSS variables, not hardcoded hex

### Interaction
- [ ] `cursor: pointer` on all clickable elements
- [ ] Hover states provide clear visual feedback
- [ ] Transitions smooth (250–350ms cubic-bezier)
- [ ] Focus states visible (`:focus-visible` with accent outline)

### Accessibility
- [ ] All images have descriptive alt text
- [ ] Form inputs have associated labels
- [ ] `role="navigation"` on nav elements
- [ ] `aria-current="page"` on active nav links
- [ ] `aria-expanded` toggles on hamburger
- [ ] Color not the only state indicator

### Layout
- [ ] No content hidden behind fixed navbar
- [ ] No horizontal scroll on mobile
- [ ] Responsive at 360px, 768px, 1024px, 1440px

### JavaScript
- [ ] Every DOM query wrapped in null-check (`if (el) { ... }`)
- [ ] All scroll listeners use `{ passive: true }`
- [ ] Single `main.js` shared across all pages
- [ ] No console errors on any page