#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Design System Generator - Aggregates search results and applies reasoning
to generate comprehensive design system recommendations.

Usage:
    from design_system import generate_design_system
    result = generate_design_system("SaaS dashboard", "My Project")

    # With persistence (Master + Overrides pattern)
    result = generate_design_system("SaaS dashboard", "My Project", persist=True)
    result = generate_design_system("SaaS dashboard", "My Project", persist=True, page="dashboard")
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from core import search, DATA_DIR


# ============ CONFIGURATION ============
REASONING_FILE = "ui-reasoning.csv"

SEARCH_CONFIG = {
    "product": {"max_results": 1},
    "style": {"max_results": 3},
    "color": {"max_results": 2},
    "landing": {"max_results": 2},
    "typography": {"max_results": 2}
}

# ============ CANONICAL SPACING SCALE ============
# Single source of truth — used by SKILL.md Rule 9 AND MASTER.md
# 8px base unit, doubling scale
SPACING_SCALE = {
    "--space-xs": ("0.5rem", "8px",   "Tight gaps, small padding"),
    "--space-sm": ("1rem",   "16px",  "Standard inner padding, icon gaps"),
    "--space-md": ("2rem",   "32px",  "Card padding, section inner spacing"),
    "--space-lg": ("4rem",   "64px",  "Section vertical padding"),
    "--space-xl": ("8rem",   "128px", "Hero sections, major vertical rhythm"),
}

# ============ CANONICAL SHADOW SCALE ============
SHADOW_SCALE = {
    "--shadow-sm": ("0 2px 10px rgba(0,0,0,0.3)",  "Subtle lift, hover state"),
    "--shadow-md": ("0 4px 20px rgba(0,0,0,0.5)",  "Cards, buttons"),
    "--shadow-lg": ("0 10px 40px rgba(0,0,0,0.8)", "Modals, dropdowns, featured"),
}


# ============ DESIGN SYSTEM GENERATOR ============
class DesignSystemGenerator:
    """Generates design system recommendations from aggregated searches."""

    def __init__(self):
        self.reasoning_data = self._load_reasoning()

    def _load_reasoning(self) -> list:
        """Load reasoning rules from CSV."""
        filepath = DATA_DIR / REASONING_FILE
        if not filepath.exists():
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _multi_domain_search(self, query: str, style_priority: list = None) -> dict:
        """Execute searches across multiple domains."""
        results = {}
        for domain, config in SEARCH_CONFIG.items():
            if domain == "style" and style_priority:
                priority_query = " ".join(style_priority[:2]) if style_priority else query
                combined_query = f"{query} {priority_query}"
                results[domain] = search(combined_query, domain, config["max_results"])
            else:
                results[domain] = search(query, domain, config["max_results"])
        return results

    def _find_reasoning_rule(self, category: str) -> dict:
        """Find matching reasoning rule for a category."""
        category_lower = category.lower()

        for rule in self.reasoning_data:
            if rule.get("UI_Category", "").lower() == category_lower:
                return rule

        for rule in self.reasoning_data:
            ui_cat = rule.get("UI_Category", "").lower()
            if ui_cat in category_lower or category_lower in ui_cat:
                return rule

        for rule in self.reasoning_data:
            ui_cat = rule.get("UI_Category", "").lower()
            keywords = ui_cat.replace("/", " ").replace("-", " ").split()
            if any(kw in category_lower for kw in keywords):
                return rule

        return {}

    def _apply_reasoning(self, category: str, search_results: dict) -> dict:
        """Apply reasoning rules to search results."""
        rule = self._find_reasoning_rule(category)

        if not rule:
            return {
                "pattern": "Hero + Features + CTA",
                "style_priority": ["Minimalism", "Flat Design"],
                "color_mood": "Professional",
                "typography_mood": "Clean",
                "key_effects": "Subtle hover transitions",
                "anti_patterns": "",
                "decision_rules": {},
                "severity": "MEDIUM"
            }

        decision_rules = {}
        try:
            decision_rules = json.loads(rule.get("Decision_Rules", "{}"))
        except json.JSONDecodeError:
            pass

        return {
            "pattern": rule.get("Recommended_Pattern", ""),
            "style_priority": [s.strip() for s in rule.get("Style_Priority", "").split("+")],
            "color_mood": rule.get("Color_Mood", ""),
            "typography_mood": rule.get("Typography_Mood", ""),
            "key_effects": rule.get("Key_Effects", ""),
            "anti_patterns": rule.get("Anti_Patterns", ""),
            "decision_rules": decision_rules,
            "severity": rule.get("Severity", "MEDIUM")
        }

    def _select_best_match(self, results: list, priority_keywords: list) -> dict:
        """Select best matching result based on priority keywords."""
        if not results:
            return {}

        if not priority_keywords:
            return results[0]

        for priority in priority_keywords:
            priority_lower = priority.lower().strip()
            for result in results:
                style_name = result.get("Style Category", "").lower()
                if priority_lower in style_name or style_name in priority_lower:
                    return result

        scored = []
        for result in results:
            result_str = str(result).lower()
            score = 0
            for kw in priority_keywords:
                kw_lower = kw.lower().strip()
                if kw_lower in result.get("Style Category", "").lower():
                    score += 10
                elif kw_lower in result.get("Keywords", "").lower():
                    score += 3
                elif kw_lower in result_str:
                    score += 1
            scored.append((score, result))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored and scored[0][0] > 0 else results[0]

    def _extract_results(self, search_result: dict) -> list:
        """Extract results list from search result dict."""
        return search_result.get("results", [])

    def generate(self, query: str, project_name: str = None) -> dict:
        """Generate complete design system recommendation."""
        product_result = search(query, "product", 1)
        product_results = product_result.get("results", [])
        category = "General"
        if product_results:
            category = product_results[0].get("Product Type", "General")

        reasoning = self._apply_reasoning(category, {})
        style_priority = reasoning.get("style_priority", [])

        search_results = self._multi_domain_search(query, style_priority)
        search_results["product"] = product_result

        style_results = self._extract_results(search_results.get("style", {}))
        color_results = self._extract_results(search_results.get("color", {}))
        typography_results = self._extract_results(search_results.get("typography", {}))
        landing_results = self._extract_results(search_results.get("landing", {}))

        best_style = self._select_best_match(style_results, reasoning.get("style_priority", []))
        best_color = color_results[0] if color_results else {}
        best_typography = typography_results[0] if typography_results else {}
        best_landing = landing_results[0] if landing_results else {}

        style_effects = best_style.get("Effects & Animation", "")
        reasoning_effects = reasoning.get("key_effects", "")
        combined_effects = style_effects if style_effects else reasoning_effects

        return {
            "project_name": project_name or query.upper(),
            "category": category,
            "pattern": {
                "name": best_landing.get("Pattern Name", reasoning.get("pattern", "Hero + Features + CTA")),
                "sections": best_landing.get("Section Order", "Hero > Features > CTA"),
                "cta_placement": best_landing.get("Primary CTA Placement", "Above fold"),
                "color_strategy": best_landing.get("Color Strategy", ""),
                "conversion": best_landing.get("Conversion Optimization", "")
            },
            "style": {
                "name": best_style.get("Style Category", "Minimalism"),
                "type": best_style.get("Type", "General"),
                "effects": style_effects,
                "keywords": best_style.get("Keywords", ""),
                "best_for": best_style.get("Best For", ""),
                "performance": best_style.get("Performance", ""),
                "accessibility": best_style.get("Accessibility", ""),
                "checklist": best_style.get("Implementation Checklist", ""),
                "css_vars": best_style.get("Design System Variables", ""),
                "ai_prompt": best_style.get("AI Prompt Keywords", ""),
                "css_keywords": best_style.get("CSS/Technical Keywords", "")
            },
            "colors": {
                "primary": best_color.get("Primary (Hex)", "#2563EB"),
                "secondary": best_color.get("Secondary (Hex)", "#3B82F6"),
                "cta": best_color.get("CTA (Hex)", "#F97316"),
                "background": best_color.get("Background (Hex)", "#F8FAFC"),
                "text": best_color.get("Text (Hex)", "#1E293B"),
                "notes": best_color.get("Notes", "")
            },
            "typography": {
                "heading": best_typography.get("Heading Font", "Inter"),
                "body": best_typography.get("Body Font", "Inter"),
                "mood": best_typography.get("Mood/Style Keywords", reasoning.get("typography_mood", "")),
                "best_for": best_typography.get("Best For", ""),
                "google_fonts_url": best_typography.get("Google Fonts URL", ""),
                "css_import": best_typography.get("CSS Import", ""),
                "tailwind_config": best_typography.get("Tailwind Config", ""),
                "notes": best_typography.get("Notes", "")
            },
            "key_effects": combined_effects,
            "anti_patterns": reasoning.get("anti_patterns", ""),
            "decision_rules": reasoning.get("decision_rules", {}),
            "severity": reasoning.get("severity", "MEDIUM")
        }


# ============ PRE-DELIVERY CHECKLIST (Single Source of Truth) ============
PRE_DELIVERY_CHECKLIST = [
    # CSS Architecture
    ("CSS Architecture", [
        "[ ] ONE CSS approach only — Vanilla OR Tailwind, never mixed",
        "[ ] Every HTML class name exists as a rule in style.css",
        "[ ] No Tailwind class names (p-8, text-gray-300, max-w-[800px]) without Tailwind installed",
        "[ ] No inline style=\"\" for layout properties (flex, grid, font-size, display)",
    ]),
    # Multi-Page
    ("Multi-Page Consistency", [
        "[ ] Navbar HTML identical on all pages (only aria-current changes per page)",
        "[ ] Footer complete and identical on ALL pages — no simplified inner page footer",
        "[ ] CTA section before footer on every inner page",
        "[ ] Favicon linked on every page",
        "[ ] Every page has unique <title>, <meta description>, and OG tags",
    ]),
    # First-Run
    ("First-Run Perfection", [
        "[ ] ALL headings use clamp() — zero hardcoded font sizes",
        "[ ] Mobile hamburger implemented, functional, toggles aria-expanded",
        "[ ] All grids collapse to 1-column on mobile (360px)",
        "[ ] CSS variables defined for all design tokens (Rule 9 scale)",
        "[ ] Custom scrollbar styled",
        "[ ] prefers-reduced-motion media query included",
        "[ ] Scroll reveal (.reveal + IntersectionObserver) on every section",
        "[ ] Forms: per-field validation + loading state + success message",
        "[ ] All assets local (no external dependencies for critical assets)",
    ]),
    # Interaction
    ("Interaction", [
        "[ ] cursor: pointer on all clickable elements",
        "[ ] Hover states provide clear visual feedback",
        "[ ] Transitions smooth (250-350ms cubic-bezier)",
        "[ ] :focus-visible with accent color outline",
    ]),
    # Accessibility
    ("Accessibility", [
        "[ ] All images have descriptive alt text",
        "[ ] Form inputs have associated <label> elements",
        "[ ] role=\"navigation\" on nav elements",
        "[ ] aria-current=\"page\" on active nav links",
        "[ ] aria-expanded toggles on hamburger button",
        "[ ] Color not the only state indicator",
    ]),
    # Layout
    ("Layout & Responsive", [
        "[ ] No content hidden behind fixed navbar (use padding-top: var(--nav-h))",
        "[ ] No horizontal scroll on mobile",
        "[ ] Responsive at 360px, 768px, 1024px, 1440px",
    ]),
    # JS
    ("JavaScript", [
        "[ ] Every DOM query wrapped in null-check (if (el) { ... })",
        "[ ] All scroll listeners use { passive: true }",
        "[ ] Single main.js shared across all pages",
        "[ ] No console errors on any page",
    ]),
]


# ============ OUTPUT FORMATTERS ============
BOX_WIDTH = 92

def format_ascii_box(design_system: dict) -> str:
    """Format design system as ASCII box — terminal display."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")

    def wrap(text: str, prefix: str, width: int) -> list:
        if not text:
            return []
        words = text.split()
        lines, cur = [], prefix
        for word in words:
            if len(cur) + len(word) + 1 <= width - 2:
                cur += (" " if cur != prefix else "") + word
            else:
                if cur != prefix:
                    lines.append(cur)
                cur = prefix + word
        if cur != prefix:
            lines.append(cur)
        return lines

    sections = [s.strip() for s in pattern.get("sections", "").split(">") if s.strip()]
    w = BOX_WIDTH - 1
    L = []

    L.append("+" + "-" * w + "+")
    L.append(f"|  TARGET: {project} — RECOMMENDED DESIGN SYSTEM".ljust(BOX_WIDTH) + "|")
    L.append("+" + "-" * w + "+")
    L.append("|" + " " * BOX_WIDTH + "|")

    # Pattern
    L.append(f"|  PATTERN: {pattern.get('name', '')}".ljust(BOX_WIDTH) + "|")
    if pattern.get("conversion"):
        L.append(f"|     Conversion: {pattern.get('conversion', '')}".ljust(BOX_WIDTH) + "|")
    if pattern.get("cta_placement"):
        L.append(f"|     CTA: {pattern.get('cta_placement', '')}".ljust(BOX_WIDTH) + "|")
    L.append("|     Sections:".ljust(BOX_WIDTH) + "|")
    for i, s in enumerate(sections, 1):
        L.append(f"|       {i}. {s}".ljust(BOX_WIDTH) + "|")
    L.append("|" + " " * BOX_WIDTH + "|")

    # Style
    L.append(f"|  STYLE: {style.get('name', '')}".ljust(BOX_WIDTH) + "|")
    if style.get("keywords"):
        for line in wrap(f"Keywords: {style.get('keywords', '')}", "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("best_for"):
        for line in wrap(f"Best For: {style.get('best_for', '')}", "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("ai_prompt"):
        for line in wrap(f"AI Prompt: {style.get('ai_prompt', '')[:200]}", "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("css_keywords"):
        for line in wrap(f"CSS Keys: {style.get('css_keywords', '')[:200]}", "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
    if style.get("performance") or style.get("accessibility"):
        L.append(f"|     Perf: {style.get('performance','')} | A11y: {style.get('accessibility','')}".ljust(BOX_WIDTH) + "|")
    L.append("|" + " " * BOX_WIDTH + "|")

    # Colors
    L.append("|  COLORS:".ljust(BOX_WIDTH) + "|")
    L.append(f"|     Primary:    {colors.get('primary', '')}".ljust(BOX_WIDTH) + "|")
    L.append(f"|     Secondary:  {colors.get('secondary', '')}".ljust(BOX_WIDTH) + "|")
    L.append(f"|     CTA:        {colors.get('cta', '')}".ljust(BOX_WIDTH) + "|")
    L.append(f"|     Background: {colors.get('background', '')}".ljust(BOX_WIDTH) + "|")
    L.append(f"|     Text:       {colors.get('text', '')}".ljust(BOX_WIDTH) + "|")
    if colors.get("notes"):
        for line in wrap(f"Notes: {colors.get('notes', '')}", "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
    L.append("|" + " " * BOX_WIDTH + "|")

    # Typography
    L.append(f"|  TYPOGRAPHY: {typography.get('heading', '')} / {typography.get('body', '')}".ljust(BOX_WIDTH) + "|")
    if typography.get("mood"):
        for line in wrap(f"Mood: {typography.get('mood', '')}", "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
    if typography.get("best_for"):
        for line in wrap(f"Best For: {typography.get('best_for', '')}", "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
    if typography.get("google_fonts_url"):
        L.append(f"|     Google Fonts: {typography.get('google_fonts_url', '')}".ljust(BOX_WIDTH) + "|")
    if typography.get("css_import"):
        L.append(f"|     CSS Import: {typography.get('css_import', '')[:70]}...".ljust(BOX_WIDTH) + "|")
    if typography.get("notes"):
        for line in wrap(f"Notes: {typography.get('notes', '')}", "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
    L.append("|" + " " * BOX_WIDTH + "|")

    # Key Effects
    if effects:
        L.append("|  KEY EFFECTS:".ljust(BOX_WIDTH) + "|")
        for line in wrap(effects, "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
        L.append("|" + " " * BOX_WIDTH + "|")

    # Anti-patterns
    if anti_patterns:
        L.append("|  AVOID (Anti-patterns):".ljust(BOX_WIDTH) + "|")
        for line in wrap(anti_patterns, "|     ", BOX_WIDTH):
            L.append(line.ljust(BOX_WIDTH) + "|")
        L.append("|" + " " * BOX_WIDTH + "|")

    # Pre-Delivery Checklist — critical items only for terminal display
    L.append("|  PRE-DELIVERY CHECKLIST (critical):".ljust(BOX_WIDTH) + "|")
    critical_items = [
        "[ ] ONE CSS approach only — Vanilla OR Tailwind, never mixed",
        "[ ] Every HTML class exists in style.css (no phantom classes)",
        "[ ] Nav + footer IDENTICAL on all pages",
        "[ ] ALL headings use clamp() — zero hardcoded sizes",
        "[ ] cursor: pointer on all clickable elements",
        "[ ] prefers-reduced-motion respected",
        "[ ] Responsive: 360px, 768px, 1024px, 1440px",
        "[ ] No console errors on any page",
    ]
    for item in critical_items:
        L.append(f"|     {item}".ljust(BOX_WIDTH) + "|")
    L.append("|" + " " * BOX_WIDTH + "|")

    L.append("+" + "-" * w + "+")
    return "\n".join(L)


def format_markdown(design_system: dict) -> str:
    """Format design system as markdown."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")

    L = []
    L.append(f"## Design System: {project}")
    L.append("")

    L.append("### Pattern")
    L.append(f"- **Name:** {pattern.get('name', '')}")
    if pattern.get("conversion"):
        L.append(f"- **Conversion Focus:** {pattern.get('conversion', '')}")
    if pattern.get("cta_placement"):
        L.append(f"- **CTA Placement:** {pattern.get('cta_placement', '')}")
    if pattern.get("color_strategy"):
        L.append(f"- **Color Strategy:** {pattern.get('color_strategy', '')}")
    L.append(f"- **Sections:** {pattern.get('sections', '')}")
    L.append("")

    L.append("### Style")
    L.append(f"- **Name:** {style.get('name', '')}")
    if style.get("keywords"):
        L.append(f"- **Keywords:** {style.get('keywords', '')}")
    if style.get("best_for"):
        L.append(f"- **Best For:** {style.get('best_for', '')}")
    if style.get("ai_prompt"):
        L.append(f"- **AI Prompt:** {style.get('ai_prompt', '')}")
    if style.get("css_keywords"):
        L.append(f"- **CSS Keywords:** {style.get('css_keywords', '')}")
    if style.get("performance") or style.get("accessibility"):
        L.append(f"- **Performance:** {style.get('performance', '')} | **Accessibility:** {style.get('accessibility', '')}")
    L.append("")

    L.append("### Colors")
    L.append("| Role | Hex |")
    L.append("|------|-----|")
    L.append(f"| Primary | {colors.get('primary', '')} |")
    L.append(f"| Secondary | {colors.get('secondary', '')} |")
    L.append(f"| CTA | {colors.get('cta', '')} |")
    L.append(f"| Background | {colors.get('background', '')} |")
    L.append(f"| Text | {colors.get('text', '')} |")
    if colors.get("notes"):
        L.append(f"\n*Notes: {colors.get('notes', '')}*")
    L.append("")

    L.append("### Typography")
    L.append(f"- **Heading:** {typography.get('heading', '')}")
    L.append(f"- **Body:** {typography.get('body', '')}")
    if typography.get("mood"):
        L.append(f"- **Mood:** {typography.get('mood', '')}")
    if typography.get("best_for"):
        L.append(f"- **Best For:** {typography.get('best_for', '')}")
    if typography.get("google_fonts_url"):
        L.append(f"- **Google Fonts:** {typography.get('google_fonts_url', '')}")
    if typography.get("css_import"):
        L.append("- **CSS Import:**")
        L.append("```css")
        L.append(typography.get("css_import", ""))
        L.append("```")
    if typography.get("notes"):
        L.append(f"- **Notes:** {typography.get('notes', '')}")
    L.append("")

    if effects:
        L.append("### Key Effects")
        L.append(effects)
        L.append("")

    if anti_patterns:
        L.append("### Avoid (Anti-patterns)")
        nb = "\n- "
        L.append(f"- {anti_patterns.replace(' + ', nb)}")
        L.append("")

    L.append("### Pre-Delivery Checklist")
    for section_name, items in PRE_DELIVERY_CHECKLIST:
        L.append(f"\n**{section_name}**")
        for item in items:
            L.append(f"{item}")
    L.append("")

    return "\n".join(L)


# ============ MAIN ENTRY POINT ============
def generate_design_system(query: str, project_name: str = None, output_format: str = "ascii",
                           persist: bool = False, page: str = None, output_dir: str = None) -> str:
    """
    Main entry point for design system generation.

    Args:
        query: Search query (e.g., "SaaS dashboard", "e-commerce luxury")
        project_name: Optional project name for output header
        output_format: "ascii" (default) or "markdown"
        persist: If True, save design system to design-system/ folder
        page: Optional page name for page-specific override file
        output_dir: Optional output directory (defaults to current working directory)

    Returns:
        Formatted design system string
    """
    generator = DesignSystemGenerator()
    design_system = generator.generate(query, project_name)

    if persist:
        persist_design_system(design_system, page, output_dir, query)

    if output_format == "markdown":
        return format_markdown(design_system)
    return format_ascii_box(design_system)


# ============ PERSISTENCE FUNCTIONS ============
def persist_design_system(design_system: dict, page: str = None, output_dir: str = None, page_query: str = None) -> dict:
    """
    Persist design system to design-system/<project>/ folder using Master + Overrides pattern.
    """
    base_dir = Path(output_dir) if output_dir else Path.cwd()
    project_name = design_system.get("project_name", "default")
    project_slug = project_name.lower().replace(" ", "-")

    design_system_dir = base_dir / "design-system" / project_slug
    pages_dir = design_system_dir / "pages"
    created_files = []

    design_system_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)

    master_file = design_system_dir / "MASTER.md"
    master_content = format_master_md(design_system)
    with open(master_file, "w", encoding="utf-8") as f:
        f.write(master_content)
    created_files.append(str(master_file))

    if page:
        page_file = pages_dir / f"{page.lower().replace(' ', '-')}.md"
        page_content = format_page_override_md(design_system, page, page_query)
        with open(page_file, "w", encoding="utf-8") as f:
            f.write(page_content)
        created_files.append(str(page_file))

    return {
        "status": "success",
        "design_system_dir": str(design_system_dir),
        "created_files": created_files
    }


def format_master_md(design_system: dict) -> str:
    """Format design system as MASTER.md with hierarchical override logic."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    L = []
    L.append("# Design System Master File")
    L.append("")
    L.append("> **LOGIC:** When building a specific page, first check `design-system/pages/[page-name].md`.")
    L.append("> If that file exists, its rules **override** this Master file.")
    L.append("> If not, strictly follow the rules below.")
    L.append("")
    L.append("---")
    L.append("")
    L.append(f"**Project:** {project}")
    L.append(f"**Generated:** {timestamp}")
    L.append(f"**Category:** {design_system.get('category', 'General')}")
    L.append("")
    L.append("---")
    L.append("")

    # ── CSS Architecture ──────────────────────────────────────────────────
    L.append("## CSS Architecture Rule (MANDATORY)")
    L.append("")
    L.append("**Pick ONE approach. Never mix.**")
    L.append("")
    L.append("| Scenario | Approach |")
    L.append("|----------|----------|")
    L.append("| Plain HTML + hand-written CSS file | **Vanilla CSS** — named component classes only |")
    L.append("| HTML + Tailwind CDN or tailwind.config.js | **Tailwind** — utility classes |")
    L.append("| Not specified | **Default: Vanilla CSS** |")
    L.append("")
    L.append("**Self-check:** Before writing any HTML, confirm every class you type exists in style.css.")
    L.append("If it doesn't have a CSS rule → don't use it.")
    L.append("")
    L.append("**Forbidden patterns:**")
    L.append("```html")
    L.append("<!-- NEVER: Tailwind class names without Tailwind installed -->")
    L.append('<div class="max-w-[800px] text-gray-300 p-8 lg:grid-cols-3">')
    L.append("<!-- These silently do nothing in plain CSS -->")
    L.append("```")
    L.append("")

    # ── Multi-Page Rule ───────────────────────────────────────────────────
    L.append("## Multi-Page Consistency Rule (MANDATORY)")
    L.append("")
    L.append("**Build nav + footer first. Copy to ALL pages. Never simplify for inner pages.**")
    L.append("")
    L.append("- Navbar HTML **identical** on all pages — only `aria-current=\"page\"` changes")
    L.append("- Footer **complete** on ALL pages — no bare copyright-only footer on inner pages")
    L.append("- CTA section before footer on every page")
    L.append("- Favicon + unique `<title>` + `<meta description>` on every page")
    L.append("")

    # ── Color Palette ─────────────────────────────────────────────────────
    L.append("## Global Rules")
    L.append("")
    L.append("### Color Palette")
    L.append("")
    L.append("| Role | Hex | CSS Variable |")
    L.append("|------|-----|--------------|")
    L.append(f"| Primary | `{colors.get('primary', '#2563EB')}` | `--color-primary` |")
    L.append(f"| Secondary | `{colors.get('secondary', '#3B82F6')}` | `--color-secondary` |")
    L.append(f"| CTA/Accent | `{colors.get('cta', '#F97316')}` | `--color-cta` |")
    L.append(f"| Background | `{colors.get('background', '#F8FAFC')}` | `--color-background` |")
    L.append(f"| Text | `{colors.get('text', '#1E293B')}` | `--color-text` |")
    L.append("")
    if colors.get("notes"):
        L.append(f"**Color Notes:** {colors.get('notes', '')}")
        L.append("")

    # ── Typography ────────────────────────────────────────────────────────
    L.append("### Typography")
    L.append("")
    L.append(f"- **Heading Font:** {typography.get('heading', 'Inter')}")
    L.append(f"- **Body Font:** {typography.get('body', 'Inter')}")
    if typography.get("mood"):
        L.append(f"- **Mood:** {typography.get('mood', '')}")
    if typography.get("google_fonts_url"):
        L.append(f"- **Google Fonts:** [{typography.get('heading', '')} + {typography.get('body', '')}]({typography.get('google_fonts_url', '')})")
    L.append("")
    L.append("**Fluid typography (MANDATORY — no hardcoded font sizes):**")
    L.append("```css")
    L.append("h1 { font-size: clamp(2rem, 8vw, 6rem); }")
    L.append("h2 { font-size: clamp(1.6rem, 5vw, 4rem); }")
    L.append("h3 { font-size: clamp(1.3rem, 3vw, 2.5rem); }")
    L.append("body { font-size: clamp(0.9rem, 1.5vw, 1.1rem); }")
    L.append("```")
    L.append("")
    if typography.get("css_import"):
        L.append("**CSS Import:**")
        L.append("```css")
        L.append(typography.get("css_import", ""))
        L.append("```")
        L.append("")

    # ── Spacing Tokens (canonical scale from SKILL.md Rule 9) ─────────────
    L.append("### Spacing Variables (8px base, doubling scale)")
    L.append("")
    L.append("| Token | rem | px | Usage |")
    L.append("|-------|-----|----|-------|")
    for token, (rem, px, usage) in SPACING_SCALE.items():
        L.append(f"| `{token}` | `{rem}` | `{px}` | {usage} |")
    L.append("")
    L.append("```css")
    L.append(":root {")
    for token, (rem, px, _) in SPACING_SCALE.items():
        L.append(f"  {token}: {rem};  /* {px} */")
    L.append("}")
    L.append("```")
    L.append("")

    # ── Shadow Depths ──────────────────────────────────────────────────────
    L.append("### Shadow Depths")
    L.append("")
    L.append("| Token | Value | Usage |")
    L.append("|-------|-------|-------|")
    for token, (value, usage) in SHADOW_SCALE.items():
        L.append(f"| `{token}` | `{value}` | {usage} |")
    L.append("")

    # ── Component Specs ────────────────────────────────────────────────────
    L.append("---")
    L.append("")
    L.append("## Component Specs")
    L.append("")

    L.append("### Buttons")
    L.append("")
    L.append("```css")
    L.append("/* Primary Button */")
    L.append(".btn-primary {")
    L.append(f"  background: {colors.get('cta', '#F97316')};")
    L.append("  color: #000;")
    L.append("  padding: 1rem 2.5rem;")
    L.append("  border: 1px solid transparent;")
    L.append("  font-weight: 700;")
    L.append("  letter-spacing: 0.1em;")
    L.append("  text-transform: uppercase;")
    L.append("  cursor: pointer;")
    L.append("  transition: var(--transition);")
    L.append("  min-height: 48px;")
    L.append("}")
    L.append(".btn-primary:hover {")
    L.append("  transform: translateY(-2px);")
    L.append(f"  box-shadow: var(--shadow-md);")
    L.append("}")
    L.append("")
    L.append("/* Ghost Button */")
    L.append(".btn-ghost {")
    L.append("  background: transparent;")
    L.append(f"  color: {colors.get('primary', '#2563EB')};")
    L.append(f"  border: 1px solid {colors.get('primary', '#2563EB')};")
    L.append("  padding: 1rem 2.5rem;")
    L.append("  font-weight: 700;")
    L.append("  cursor: pointer;")
    L.append("  transition: var(--transition);")
    L.append("  min-height: 48px;")
    L.append("}")
    L.append(".btn-ghost:hover {")
    L.append("  transform: translateY(-2px);")
    L.append("}")
    L.append("```")
    L.append("")

    L.append("### Cards")
    L.append("")
    L.append("```css")
    L.append(".card {")
    L.append(f"  background: {colors.get('background', '#FFFFFF')};")
    L.append("  border: 1px solid var(--border);")
    L.append("  padding: var(--space-md);")
    L.append("  transition: var(--transition);")
    L.append("  cursor: pointer;")
    L.append("}")
    L.append(".card:hover {")
    L.append(f"  border-color: {colors.get('primary', '#2563EB')};")
    L.append("  box-shadow: var(--shadow-md);")
    L.append("  transform: translateY(-4px);")
    L.append("}")
    L.append("```")
    L.append("")

    L.append("### Inputs")
    L.append("")
    L.append("```css")
    L.append(".input {")
    L.append("  width: 100%;")
    L.append("  background: var(--bg-secondary);")
    L.append("  border: 1px solid var(--border);")
    L.append("  color: var(--text-primary);")
    L.append("  padding: var(--space-sm) var(--space-md);")
    L.append("  font-size: 0.9rem;")
    L.append("  transition: var(--transition);")
    L.append("  min-height: 48px;")
    L.append("}")
    L.append(".input:focus {")
    L.append(f"  border-color: {colors.get('primary', '#2563EB')};")
    L.append("  outline: none;")
    L.append(f"  box-shadow: 0 0 0 3px {colors.get('primary', '#2563EB')}20;")
    L.append("}")
    L.append("/* Error state — applied to parent .form-group, not the input */")
    L.append(".form-group.has-error .input { border-color: #ef4444; }")
    L.append(".error-msg { display: none; font-size: 0.75rem; color: #ef4444; margin-top: 0.3rem; }")
    L.append(".form-group.has-error .error-msg { display: block; }")
    L.append("```")
    L.append("")

    # ── Style Guidelines ───────────────────────────────────────────────────
    L.append("---")
    L.append("")
    L.append("## Style Guidelines")
    L.append("")
    L.append(f"**Style:** {style.get('name', 'Minimalism')}")
    L.append("")
    if style.get("keywords"):
        L.append(f"**Keywords:** {style.get('keywords', '')}")
        L.append("")
    if style.get("best_for"):
        L.append(f"**Best For:** {style.get('best_for', '')}")
        L.append("")
    if style.get("ai_prompt"):
        L.append(f"**AI Prompt:** {style.get('ai_prompt', '')}")
        L.append("")
    if style.get("css_keywords"):
        L.append(f"**CSS Keywords:** {style.get('css_keywords', '')}")
        L.append("")
    if effects:
        L.append(f"**Key Effects:** {effects}")
        L.append("")

    L.append("### Page Pattern")
    L.append("")
    L.append(f"**Pattern Name:** {pattern.get('name', '')}")
    L.append("")
    if pattern.get("conversion"):
        L.append(f"- **Conversion Strategy:** {pattern.get('conversion', '')}")
    if pattern.get("cta_placement"):
        L.append(f"- **CTA Placement:** {pattern.get('cta_placement', '')}")
    L.append(f"- **Section Order:** {pattern.get('sections', '')}")
    L.append("")

    # ── Anti-Patterns ──────────────────────────────────────────────────────
    L.append("---")
    L.append("")
    L.append("## Anti-Patterns (Do NOT Use)")
    L.append("")
    if anti_patterns:
        for a in [x.strip() for x in anti_patterns.split("+") if x.strip()]:
            L.append(f"- ❌ {a}")
    L.append("")
    L.append("### Universal Forbidden Patterns")
    L.append("")
    L.append("- ❌ **Mixing CSS approaches** — Vanilla class names AND Tailwind utilities in same project")
    L.append("- ❌ **Phantom CSS classes** — Class in HTML with no corresponding CSS rule")
    L.append("- ❌ **Inline layout styles** — `style=\"display:flex\"`, `style=\"font-size:6rem\"` etc.")
    L.append("- ❌ **Simplified inner page footer** — Every page gets the full footer")
    L.append("- ❌ **Missing nav on any page** — Copy nav to every page before writing content")
    L.append("- ❌ **Emojis as icons** — Use SVG icons (Heroicons, Lucide, Simple Icons)")
    L.append("- ❌ **Missing cursor: pointer** — All clickable elements must have it")
    L.append("- ❌ **Layout-shifting hovers** — Avoid scale transforms that shift surrounding layout")
    L.append("- ❌ **Hardcoded font sizes** — Always use clamp()")
    L.append("- ❌ **Missing null-checks in JS** — Wrap every DOM query: `if (el) { ... }`")
    L.append("")

    # ── Pre-Delivery Checklist ─────────────────────────────────────────────
    L.append("---")
    L.append("")
    L.append("## Pre-Delivery Checklist")
    L.append("")
    L.append("Before delivering any UI code, verify every item:")
    L.append("")
    for section_name, items in PRE_DELIVERY_CHECKLIST:
        L.append(f"**{section_name}**")
        for item in items:
            L.append(item)
        L.append("")

    return "\n".join(L)


def format_page_override_md(design_system: dict, page_name: str, page_query: str = None) -> str:
    """Format a page-specific override file with intelligent AI-generated content."""
    project = design_system.get("project_name", "PROJECT")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    page_title = page_name.replace("-", " ").replace("_", " ").title()

    page_overrides = _generate_intelligent_overrides(page_name, page_query, design_system)

    L = []
    L.append(f"# {page_title} Page Overrides")
    L.append("")
    L.append(f"> **PROJECT:** {project}")
    L.append(f"> **Generated:** {timestamp}")
    L.append(f"> **Page Type:** {page_overrides.get('page_type', 'General')}")
    L.append("")
    L.append("> ⚠️ **IMPORTANT:** Rules in this file **override** the Master file (`MASTER.md`).")
    L.append("> Only deviations from the Master are documented here. For all other rules, refer to MASTER.md.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Page-Specific Rules")
    L.append("")

    for section, key in [("Layout Overrides", "layout"), ("Spacing Overrides", "spacing"),
                         ("Typography Overrides", "typography"), ("Color Overrides", "colors")]:
        L.append(f"### {section}")
        L.append("")
        data = page_overrides.get(key, {})
        if data:
            for k, v in data.items():
                L.append(f"- **{k}:** {v}")
        else:
            L.append("- No overrides — use Master rules")
        L.append("")

    L.append("### Component Overrides")
    L.append("")
    components = page_overrides.get("components", [])
    if components:
        for c in components:
            L.append(f"- {c}")
    else:
        L.append("- No overrides — use Master component specs")
    L.append("")

    L.append("---")
    L.append("")
    L.append("## Page-Specific Components")
    L.append("")
    unique = page_overrides.get("unique_components", [])
    if unique:
        for u in unique:
            L.append(f"- {u}")
    else:
        L.append("- No unique components for this page")
    L.append("")

    L.append("---")
    L.append("")
    L.append("## Recommendations")
    L.append("")
    recs = page_overrides.get("recommendations", [])
    if recs:
        for r in recs:
            L.append(f"- {r}")
    L.append("")

    return "\n".join(L)


def _generate_intelligent_overrides(page_name: str, page_query: str, design_system: dict) -> dict:
    """Generate intelligent overrides based on page type using layered search."""
    from core import search

    page_lower = page_name.lower()
    query_lower = (page_query or "").lower()
    combined_context = f"{page_lower} {query_lower}"

    style_search = search(combined_context, "style", max_results=1)
    ux_search = search(combined_context, "ux", max_results=3)
    landing_search = search(combined_context, "landing", max_results=1)

    style_results = style_search.get("results", [])
    ux_results = ux_search.get("results", [])
    landing_results = landing_search.get("results", [])

    page_type = _detect_page_type(combined_context, style_results)

    layout, spacing, typography, colors, components, unique_components, recommendations = {}, {}, {}, {}, [], [], []

    if style_results:
        style = style_results[0]
        keywords = style.get("Keywords", "")
        effects = style.get("Effects & Animation", "")

        if any(kw in keywords.lower() for kw in ["data", "dense", "dashboard", "grid"]):
            layout["Max Width"] = "1400px or full-width"
            layout["Grid"] = "12-column grid for data flexibility"
            spacing["Content Density"] = "High — optimize for information display"
        elif any(kw in keywords.lower() for kw in ["minimal", "simple", "clean", "single"]):
            layout["Max Width"] = "800px (narrow, focused)"
            layout["Layout"] = "Single column, centered"
            spacing["Content Density"] = "Low — focus on clarity"
        else:
            layout["Max Width"] = "1200px (standard)"
            layout["Layout"] = "Full-width sections, centered content"

        if effects:
            recommendations.append(f"Effects: {effects}")

    for ux in ux_results:
        category = ux.get("Category", "")
        do_text = ux.get("Do", "")
        dont_text = ux.get("Don't", "")
        if do_text:
            recommendations.append(f"{category}: {do_text}")
        if dont_text:
            components.append(f"Avoid: {dont_text}")

    if landing_results:
        landing = landing_results[0]
        sections = landing.get("Section Order", "")
        cta_placement = landing.get("Primary CTA Placement", "")
        color_strategy = landing.get("Color Strategy", "")

        if sections:
            layout["Sections"] = sections
        if cta_placement:
            recommendations.append(f"CTA Placement: {cta_placement}")
        if color_strategy:
            colors["Strategy"] = color_strategy

    if not layout:
        layout["Max Width"] = "1200px"
        layout["Layout"] = "Responsive grid"

    if not recommendations:
        recommendations = [
            "Refer to MASTER.md for all design rules",
            "Add specific overrides as needed for this page"
        ]

    return {
        "page_type": page_type,
        "layout": layout,
        "spacing": spacing,
        "typography": typography,
        "colors": colors,
        "components": components,
        "unique_components": unique_components,
        "recommendations": recommendations
    }


def _detect_page_type(context: str, style_results: list) -> str:
    """Detect page type from context and search results."""
    context_lower = context.lower()
    page_patterns = [
        (["dashboard", "admin", "analytics", "data", "metrics", "stats", "monitor"], "Dashboard / Data View"),
        (["checkout", "payment", "cart", "purchase", "order", "billing"], "Checkout / Payment"),
        (["settings", "profile", "account", "preferences", "config"], "Settings / Profile"),
        (["landing", "marketing", "homepage", "hero", "home", "promo"], "Landing / Marketing"),
        (["login", "signin", "signup", "register", "auth", "password"], "Authentication"),
        (["pricing", "plans", "subscription", "tiers", "packages"], "Pricing / Plans"),
        (["blog", "article", "post", "news", "content", "story"], "Blog / Article"),
        (["product", "item", "detail", "pdp", "shop", "store"], "Product Detail"),
        (["search", "results", "browse", "filter", "catalog", "list"], "Search Results"),
        (["empty", "404", "error", "not found", "zero"], "Empty State"),
    ]

    for keywords, page_type in page_patterns:
        if any(kw in context_lower for kw in keywords):
            return page_type

    if style_results:
        best_for = style_results[0].get("Best For", "").lower()
        if "dashboard" in best_for or "data" in best_for:
            return "Dashboard / Data View"
        elif "landing" in best_for or "marketing" in best_for:
            return "Landing / Marketing"

    return "General"


# ============ CLI SUPPORT ============
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Design System")
    parser.add_argument("query", help="Search query (e.g., 'SaaS dashboard')")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii", help="Output format")

    args = parser.parse_args()
    result = generate_design_system(args.query, args.project_name, args.format)
    print(result)