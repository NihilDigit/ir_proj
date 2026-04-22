"""Shared plotnine theme for the IR course report figures.

Design targets:
- IEEE figure submission guidelines (9-10pt text, ≥0.5pt strokes, ≥300 dpi,
  high-contrast color, no reliance on color alone for meaning).
- Unified color + typography tokens shared with report/typst/theme.typ so
  statistical plots and architecture diagrams read as one family.
- Print-first: every element has full-contrast ink color; secondary content
  is differentiated by size/position, not by low-contrast gray.
"""

from plotnine import (
    theme_classic,
    theme,
    element_text,
    element_line,
    element_rect,
    element_blank,
    labs,
)

# ── Design tokens (mirror typst/theme.typ) ──
# All foreground text uses ink or accent — never muted gray — for print contrast.
TOKENS = {
    "ink":    "#1F2937",   # foreground text, axes, data
    "muted":  "#6B7280",   # ONLY for subtle gridlines; never for text
    "accent": "#2563EB",   # one strategic highlight per figure
    "warm":   "#B91C1C",   # reserved; avoid in charts (red-green CVD risk)
    "soft":   "#F3F4F6",   # light fill (for background panels only)
    "grid":   "#D1D5DB",   # gridline — slightly darker than before for print
    "paper":  "#FFFFFF",
}

# HarmonyOS Sans SC covers Latin + CJK; visually comparable to Helvetica (an
# IEEE-recommended family). A single family keeps mixed-lang labels coherent.
FONT_SANS = "HarmonyOS Sans SC"
FONT_MONO = "JetBrains Mono"

# Per IEEE: 1-column figure = 3.5 in (88.9 mm), 2-column = 7.16 in.
# Our course-report spec asks for ~6.5 cm (≈ 2.56 in) half-page width, which is
# slightly narrower than IEEE's 1-column. We keep spec target but keep font
# sizes at IEEE minimums so text stays readable in print.
FIG_WIDTH_IN = 2.6
FIG_HEIGHT_IN = 1.75


def theme_ir(grid: bool = False):
    """Return the project's standard plotnine theme (IEEE-compliant).

    Args:
        grid: adds faint gridlines if True. Off by default; enable only when
              the data benefits from a reference scale.
    """
    t = theme_classic(base_family=FONT_SANS, base_size=9) + theme(
        figure_size=(FIG_WIDTH_IN, FIG_HEIGHT_IN),
        dpi=300,
        # Typography — all full-contrast ink, no gray text.
        text=element_text(color=TOKENS["ink"], family=FONT_SANS),
        plot_title=element_text(size=10, weight="bold", ha="left", margin={"b": 4}),
        axis_title=element_text(size=9, color=TOKENS["ink"]),
        axis_title_x=element_text(margin={"t": 4}),
        # CJK-safe convention: we never use matplotlib's default rotated y-axis
        # title (90° rotation tilts each CJK glyph sideways — never correct for
        # Chinese). Instead we blank the built-in y title and carry the y-axis
        # meaning via the plot subtitle, which sits upright above the panel
        # (classic Chinese academic layout). Callers use y_top_label("…").
        axis_title_y=element_blank(),
        plot_subtitle=element_text(
            size=9, ha="left", color=TOKENS["ink"], margin={"l": 0, "b": 2},
        ),
        axis_text=element_text(size=8, color=TOKENS["ink"]),
        legend_title=element_text(size=8, color=TOKENS["ink"]),
        legend_text=element_text(size=8, color=TOKENS["ink"]),
        # Axes / ticks — all ≥ 0.5pt for print.
        axis_line=element_line(color=TOKENS["ink"], size=0.6),
        axis_ticks=element_line(color=TOKENS["ink"], size=0.5),
        axis_ticks_length=3,
        # Backgrounds — clean white panel.
        plot_background=element_rect(fill=TOKENS["paper"], color="none"),
        panel_background=element_rect(fill=TOKENS["paper"], color="none"),
        legend_background=element_blank(),
        legend_key=element_blank(),
    )
    if grid:
        t += theme(
            panel_grid_major_y=element_line(color=TOKENS["grid"], size=0.4),
            panel_grid_minor=element_blank(),
        )
    return t


def y_top_label(text: str):
    """Place an upright horizontal label above the y-axis (Chinese-paper style).

    Use in place of `labs(y=...)` so CJK characters stay upright without
    fighting matplotlib's rotated y-axis title. Compose like any other plotnine
    layer:

        ggplot(...) + geom_...() + y_top_label("词项数") + theme_ir()
    """
    return labs(subtitle=text)
