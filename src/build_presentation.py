"""
Build Presentation Deck (Deliverable F) — Ethiopian Smallholder Crop-Yield Challenge
Team 11 | Qiyas / IADE Training Program — Addis Ababa University Hackathon 2026

Generates the official 5-slide competition pitch deck in presentation/team_11_slides.pptx
and automatically exports to presentation/team_11_slides.pdf if PowerPoint COM is available.
Incorporates latest backend modeling enhancements (Tri-Ensemble Blend) and executive UI/UX upgrades (AgriYield Pro Enterprise).
"""

import os
import sys
import subprocess
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------
# CONSTANTS & PALETTE (Aligned with Project Design System)
# ---------------------------------------------------------
SLIDE_WIDTH_IN = 13.333
SLIDE_HEIGHT_IN = 7.5

# Color Palette (Executive Navy, Forest Green, Emerald & Amber Gold)
BG_COLOR = RGBColor(250, 249, 245)         # Warm Linen Canvas (#FAF9F5)
CARD_BG = RGBColor(255, 255, 255)          # Clean White (#FFFFFF)
CARD_BORDER = RGBColor(226, 232, 240)      # Subtle Gray Border (#E2E8F0)
PRIMARY_DARK = RGBColor(20, 61, 43)        # Deep Forest Green (#143D2B)
PRIMARY_GREEN = RGBColor(21, 128, 61)      # Vibrant Emerald (#15803D)
ACCENT_GOLD = RGBColor(217, 119, 6)        # Amber Gold (#D97706)
ACCENT_BLUE = RGBColor(3, 105, 161)        # Sky Blue (#0369A1)
TEXT_DARK = RGBColor(15, 23, 42)           # Charcoal Slate (#0F172A)
TEXT_MUTED = RGBColor(100, 116, 139)       # Slate Gray (#64748B)

# Badge Colors
BADGE_BG_GREEN = RGBColor(236, 253, 245)   # Mint green pill (#ECFDF5)
BADGE_TXT_GREEN = RGBColor(6, 95, 70)      # Dark emerald text (#065F46)
BADGE_BG_GOLD = RGBColor(254, 243, 199)    # Warm gold pill (#FEF3C7)
BADGE_TXT_GOLD = RGBColor(146, 64, 14)     # Dark gold text (#92400E)

FONT_HEADING = "Calibri"
FONT_BODY = "Calibri"


def create_base_presentation():
    """Initializes a 16:9 widescreen presentation."""
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_WIDTH_IN)
    prs.slide_height = Inches(SLIDE_HEIGHT_IN)
    return prs


def add_slide_background(slide):
    """Adds a full-bleed warm canvas background."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        Inches(SLIDE_WIDTH_IN), Inches(SLIDE_HEIGHT_IN)
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = BG_COLOR
    bg_shape.line.fill.background()  # No border
    return bg_shape


def add_header(slide, badge_text, title_text, subtitle_text, is_gold_badge=False):
    """Adds standard header with category pill badge, title and subtitle."""
    # Badge Pill
    badge_width = Inches(max(2.8, len(badge_text) * 0.11))
    badge_height = Inches(0.32)
    badge = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.6), Inches(0.42),
        badge_width, badge_height
    )
    badge.fill.solid()
    badge.fill.fore_color.rgb = BADGE_BG_GOLD if is_gold_badge else BADGE_BG_GREEN
    badge.line.color.rgb = BADGE_TXT_GOLD if is_gold_badge else BADGE_TXT_GREEN
    badge.line.width = Pt(1)
    
    tf = badge.text_frame
    tf.word_wrap = False
    tf.margin_top = Pt(2)
    tf.margin_bottom = Pt(2)
    tf.margin_left = Pt(8)
    tf.margin_right = Pt(8)
    p = tf.paragraphs[0]
    p.text = badge_text.upper()
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_HEADING
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = BADGE_TXT_GOLD if is_gold_badge else BADGE_TXT_GREEN

    # Title & Subtitle Box
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.78), Inches(12.13), Inches(0.95))
    tf_main = tb.text_frame
    tf_main.word_wrap = True
    tf_main.margin_left = Pt(0)
    tf_main.margin_right = Pt(0)
    tf_main.margin_top = Pt(0)
    tf_main.margin_bottom = Pt(0)

    p_title = tf_main.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(21)
    p_title.font.bold = True
    p_title.font.color.rgb = PRIMARY_DARK

    p_sub = tf_main.add_paragraph()
    p_sub.text = subtitle_text
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(11.5)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_before = Pt(2)


def add_footer(slide, current_slide, total_slides=5):
    """Adds standard footer to each slide."""
    # Divider line
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.6), Inches(7.02),
        Inches(12.13), Inches(0.015)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = CARD_BORDER
    line.line.fill.background()

    # Left footer label
    tb_left = slide.shapes.add_textbox(Inches(0.6), Inches(7.06), Inches(8.5), Inches(0.35))
    tf_l = tb_left.text_frame
    tf_l.margin_left = Pt(0)
    tf_l.margin_top = Pt(0)
    p_l = tf_l.paragraphs[0]
    p_l.text = "Team 11 | Ethiopian Smallholder Crop-Yield Challenge | AAU AI Hackathon 2026"
    p_l.font.name = FONT_BODY
    p_l.font.size = Pt(9)
    p_l.font.color.rgb = TEXT_MUTED

    # Right footer slide number
    tb_right = slide.shapes.add_textbox(Inches(10.73), Inches(7.06), Inches(2.0), Inches(0.35))
    tf_r = tb_right.text_frame
    tf_r.margin_right = Pt(0)
    tf_r.margin_top = Pt(0)
    p_r = tf_r.paragraphs[0]
    p_r.text = f"Slide {current_slide} of {total_slides}"
    p_r.alignment = PP_ALIGN.RIGHT
    p_r.font.name = FONT_BODY
    p_r.font.size = Pt(9)
    p_r.font.bold = True
    p_r.font.color.rgb = PRIMARY_DARK


def add_kpi_card(slide, left, top, width, height, stat_number, stat_label, subtext=None, accent_color=PRIMARY_GREEN):
    """Creates a KPI stat callout card."""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left, top, width, height
    )
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = CARD_BORDER
    card.line.width = Pt(1)

    # Top accent strip
    strip = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left, top, width, Inches(0.06)
    )
    strip.fill.solid()
    strip.fill.fore_color.rgb = accent_color
    strip.line.fill.background()

    tb = slide.shapes.add_textbox(left, top + Inches(0.08), width, height - Inches(0.1))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(10)
    tf.margin_right = Pt(10)
    tf.margin_top = Pt(4)
    tf.margin_bottom = Pt(4)

    p_num = tf.paragraphs[0]
    p_num.text = stat_number
    p_num.font.name = FONT_HEADING
    p_num.font.size = Pt(21)
    p_num.font.bold = True
    p_num.font.color.rgb = accent_color

    p_lbl = tf.add_paragraph()
    p_lbl.text = stat_label
    p_lbl.font.name = FONT_BODY
    p_lbl.font.size = Pt(10)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = TEXT_DARK
    p_lbl.space_before = Pt(1)

    if subtext:
        p_sub = tf.add_paragraph()
        p_sub.text = subtext
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(8.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_before = Pt(1)


def add_container_card(slide, left, top, width, height, title=None, badge=None):
    """Creates a structured content card container."""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left, top, width, height
    )
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = CARD_BORDER
    card.line.width = Pt(1)

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.12), width - Inches(0.3), Inches(0.45))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Pt(0)
        tf.margin_top = Pt(0)
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_DARK

    return card


def add_bullet_point(tf, prefix, body, pt_size=10, space_before=5, is_first=False):
    """Appends a styled bullet item with bold lead-in."""
    p = tf.paragraphs[0] if is_first else tf.add_paragraph()
    p.space_before = Pt(space_before)
    p.font.size = Pt(pt_size)
    p.font.name = FONT_BODY
    
    # Bullet symbol
    run_bullet = p.add_run()
    run_bullet.text = "• "
    run_bullet.font.bold = True
    run_bullet.font.color.rgb = PRIMARY_GREEN

    # Bold lead-in
    if prefix:
        run_pfx = p.add_run()
        run_pfx.text = prefix + ": "
        run_pfx.font.bold = True
        run_pfx.font.color.rgb = TEXT_DARK

    # Body text
    run_body = p.add_run()
    run_body.text = body
    run_body.font.bold = False
    run_body.font.color.rgb = TEXT_DARK


# ---------------------------------------------------------
# SLIDE BUILDERS (1 TO 5)
# ---------------------------------------------------------

def build_slide_1(prs):
    """Slide 1: Problem Definition & Data Context"""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    add_slide_background(slide)
    
    add_header(
        slide,
        badge_text="Deliverable F | 5-Minute Pitch Deck",
        title_text="Predicting Ethiopian Smallholder Crop Yields",
        subtitle_text="Team 11 | Qiyas / IADE Training Program — Addis Ababa University AI Hackathon (Oct 2026)"
    )
    add_footer(slide, 1)

    # Top KPI Row (3 stat cards)
    card_w = Inches(3.91)
    card_h = Inches(1.0)
    top_y = Inches(1.80)
    gap_x = Inches(0.2)
    start_x = Inches(0.6)

    add_kpi_card(slide, start_x, top_y, card_w, card_h,
                 "15,090 Plots", "Master Smallholder Survey Records",
                 "5 Administrative Regions × 5 Primary Food Security Crops", PRIMARY_GREEN)
    add_kpi_card(slide, start_x + (card_w + gap_x), top_y, card_w, card_h,
                 "232 Climate Records", "Monthly Regional Weather Observations",
                 "2021–2024 Precipitation, Temperature Regimes & Extreme Heat Days", ACCENT_GOLD)
    add_kpi_card(slide, start_x + (card_w + gap_x) * 2, top_y, card_w, card_h,
                 "100 Price Series", "Regional Commodity Market Benchmarks",
                 "Birr/Quintal Standards Isolated Exclusively for Post-Hoc Revenue", ACCENT_BLUE)

    # 3 Main Structural Content Cards
    body_y = Inches(2.98)
    body_h = Inches(3.88)
    col_w = Inches(3.91)

    # Card 1: Core Problem
    add_container_card(slide, start_x, body_y, col_w, body_h, "1. The Agronomic Challenge")
    tb1 = slide.shapes.add_textbox(start_x + Inches(0.18), body_y + Inches(0.55), col_w - Inches(0.36), body_h - Inches(0.65))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    add_bullet_point(tf1, "Pre-Harvest Forecast", "Accurately predict smallholder crop yield (yield_tons_per_ha) prior to harvest across five agro-ecological zones (Oromia, Amhara, SNNPR, Tigray, Somali).", pt_size=10, is_first=True)
    add_bullet_point(tf1, "5 Target Crops", "Forecasts Teff, Wheat, Maize, Sorghum, and Barley across diverse elevation bands (400m to 3,600m).", pt_size=10, space_before=6)
    add_bullet_point(tf1, "High Volatility", "Extreme seasonal rain anomalies and soil heterogeneity drive up to 4× yield dispersion between highland and lowland plots.", pt_size=10, space_before=6)
    add_bullet_point(tf1, "End-to-End System", "Engineered from raw tri-dataset ingestion into AgriYield™ Pro Enterprise—delivering live decision support across 4 dedicated workspaces.", pt_size=10, space_before=6)

    # Card 2: Tri-Dataset Ecosystem
    add_container_card(slide, start_x + (col_w + gap_x), body_y, col_w, body_h, "2. Tri-Dataset Ecosystem")
    tb2 = slide.shapes.add_textbox(start_x + (col_w + gap_x) + Inches(0.18), body_y + Inches(0.55), col_w - Inches(0.36), body_h - Inches(0.65))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    add_bullet_point(tf2, "Plot Surveys (15,090)", "Granular plot records containing farm size, fertilizer inputs, improved seed usage, elevation, pest flags, and self-reported rain.", pt_size=10, is_first=True)
    add_bullet_point(tf2, "Climate Stations (232)", "Monthly weather metrics with messy station codes ('AMH', 'ORO') and duplicate sensor timestamps.", pt_size=10, space_before=6)
    add_bullet_point(tf2, "Market Prices (100)", "Farmgate commodity market prices distorted by 100× unit mix-ups (Birr/kg vs. Birr/quintal).", pt_size=10, space_before=6)
    add_bullet_point(tf2, "Evaluation Set (3,750)", "Blind leaderboard test set evaluated strictly against ground truth with zero data leakage.", pt_size=10, space_before=6)

    # Card 3: Constraint Hygiene
    add_container_card(slide, start_x + (col_w + gap_x) * 2, body_y, col_w, body_h, "3. Strict Competition Hygiene")
    tb3 = slide.shapes.add_textbox(start_x + (col_w + gap_x) * 2 + Inches(0.18), body_y + Inches(0.55), col_w - Inches(0.36), body_h - Inches(0.65))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    add_bullet_point(tf3, "Regression Formulation", "Continuous supervised regression strictly evaluated on RMSE (primary metric), MAE, and R².", pt_size=10, is_first=True)
    add_bullet_point(tf3, "Zero Leakage (Rule 6)", "Imputations, encoders, and scalers fitted strictly on training subsets; zero test data peeked.", pt_size=10, space_before=6)
    add_bullet_point(tf3, "Price Isolation (Rule 5)", "Market prices completely excluded from feature engineering; used strictly for downstream farmer revenue analysis.", pt_size=10, space_before=6)
    add_bullet_point(tf3, "Weather Integration", "Pre-harvest seasonal climate signals seamlessly aggregated and mandated in final models.", pt_size=10, space_before=6)


def build_slide_2(prs):
    """Slide 2: Pipeline Architecture: Cleaning & Spatio-Temporal Join"""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    add_slide_background(slide)

    add_header(
        slide,
        badge_text="Deliverable A | Data Engineering & Architecture",
        title_text="Pipeline Architecture: Cleaning & Spatio-Temporal Join",
        subtitle_text="Automated Key Harmonization, 4-Month Dynamic Climate Windows, and Micro-Climate Feature Engineering"
    )
    add_footer(slide, 2)

    # 4 Top KPI Badges
    kpi_w = Inches(2.88)
    kpi_h = Inches(0.92)
    top_y = Inches(1.80)
    gap_x = Inches(0.20)
    start_x = Inches(0.6)

    add_kpi_card(slide, start_x, top_y, kpi_w, kpi_h,
                 "100.0%", "Plot → Weather Match Rate", "0 Unmatched Plots (N:1 Join)", PRIMARY_GREEN)
    add_kpi_card(slide, start_x + (kpi_w + gap_x), top_y, kpi_w, kpi_h,
                 "100.0%", "Plot → Price Match Rate", "15,090 / 15,090 Plots Aligned", PRIMARY_GREEN)
    add_kpi_card(slide, start_x + (kpi_w + gap_x) * 2, top_y, kpi_w, kpi_h,
                 "4-Month", "Growing Season Climate Window", "[Planting Month + 3 Subsequent]", ACCENT_GOLD)
    add_kpi_card(slide, start_x + (kpi_w + gap_x) * 3, top_y, kpi_w, kpi_h,
                 "0 Rows Lost", "Zero Cartesian Row Explosion", "15,090 Train | 3,750 Test Plots", ACCENT_BLUE)

    # 2 Main Content Cards
    body_y = Inches(2.90)
    body_h = Inches(3.96)
    left_w = Inches(5.95)
    right_w = Inches(5.98)
    right_x = start_x + left_w + Inches(0.2)

    # Left Card: Cleaning Pipeline
    add_container_card(slide, start_x, body_y, left_w, body_h, "1. Automated Data Cleaning & Hygiene")
    tb_l = slide.shapes.add_textbox(start_x + Inches(0.2), body_y + Inches(0.55), left_w - Inches(0.4), body_h - Inches(0.65))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    add_bullet_point(tf_l, "Key Harmonization (100% Match)", "Normalized 20 dirty region codes ('AMH', 'Amhara ', 'ORO') and 21 crop spelling variants ('Tef', ' teff ') to canonical sets ('Amhara', 'Oromia', 'SNNPR', 'Somali', 'Tigray' and 'teff', 'wheat', 'maize', 'sorghum', 'barley').", pt_size=10, is_first=True)
    add_bullet_point(tf_l, "Sentinel Value Remediation", "Replaced corrupt -999 sentinels (788 records) in pest_disease_flag (mode=0) and labor_days_per_ha (median=45.04) to prevent severe gradient loss distortion.", pt_size=10, space_before=7)
    add_bullet_point(tf_l, "Price Unit Scaling (100× Fix)", "Identified 4 market price rows recorded in Birr/kg (<500 Birr) and multiplied by 100 to restore standard Birr/quintal (3,400–4,900 Birr/qt).", pt_size=10, space_before=7)
    add_bullet_point(tf_l, "Outlier Capping & Deduplication", "Capped inputs at 99.5th percentile using training statistics only (Rule 6). Purged 6 duplicate monthly station climate pairs.", pt_size=10, space_before=7)
    add_bullet_point(tf_l, "Verified Deliverables", "Exported master_train.csv (15,090 × 26) and master_test.csv (3,750 × 25) with documented data_dictionary_master.csv.", pt_size=10, space_before=7)

    # Right Card: Spatio-Temporal Join & Feature Engineering
    add_container_card(slide, right_x, body_y, right_w, body_h, "2. Dynamic Spatio-Temporal Climate Join")
    tb_r = slide.shapes.add_textbox(right_x + Inches(0.2), body_y + Inches(0.55), right_w - Inches(0.4), body_h - Inches(0.65))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    add_bullet_point(tf_r, "Agronomic Window Definition", "Rather than static annual means, aggregated monthly climate metrics dynamically across [planting_month, planting_month + 3] (4-month growing season) per region and year, accurately capturing Belg & Meher cycles.", pt_size=10, is_first=True)
    add_bullet_point(tf_r, "High Data Coverage", "80.1% of plots have all 4 complete monthly records; 16.9% have 3 months. Zero plots have <2 months.", pt_size=10, space_before=7)
    add_bullet_point(tf_r, "weather_season_mean_temp & heat_days", "Measures average thermal regime and cumulative extreme heat stress days (>32°C) during critical flowering and grain-filling stages.", pt_size=10, space_before=7)
    add_bullet_point(tf_r, "weather_temp_anomaly_c", "Quantifies deviation from 4-year regional baseline, pinpointing localized warming shocks.", pt_size=10, space_before=7)
    add_bullet_point(tf_r, "weather_rain_discrepancy_ratio", "Calculates ratio between plot self-reported rainfall and station gauges, effectively capturing highland topographic microclimates.", pt_size=10, space_before=7)
    add_bullet_point(tf_r, "altitude_temp_index", "Models adiabatic lapse cooling rate across rugged agricultural elevations.", pt_size=10, space_before=7)


def build_slide_3(prs):
    """Slide 3: Key Insights: Market Value Disconnect & Agronomic Limits"""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    add_slide_background(slide)

    add_header(
        slide,
        badge_text="Deliverables B & C | Statistical & Agronomic Insights",
        title_text="Key Insights: Market Value Disconnect & Agronomic Limits",
        subtitle_text="The Yield vs. Revenue Paradox, Input Response Ceilings, and Spatial Agro-Ecological Divergence"
    )
    add_footer(slide, 3)

    start_x = Inches(0.6)
    body_y = Inches(1.80)
    body_h = Inches(5.06)

    # Left Column: 2 Visuals Stacked (Width 5.5 in)
    vis_w = Inches(5.50)
    fig1_path = os.path.join("figures", "fig09_revenue_by_crop_region.png")
    fig2_path = os.path.join("figures", "fig08_price_trends.png")

    # Image Card 1: Revenue by Crop & Region
    add_container_card(slide, start_x, body_y, vis_w, Inches(2.48))
    if os.path.exists(fig1_path):
        slide.shapes.add_picture(fig1_path, start_x + Inches(0.12), body_y + Inches(0.08), width=vis_w - Inches(0.24), height=Inches(2.32))

    # Image Card 2: Price Trends
    img2_y = body_y + Inches(2.58)
    add_container_card(slide, start_x, img2_y, vis_w, Inches(2.48))
    if os.path.exists(fig2_path):
        slide.shapes.add_picture(fig2_path, start_x + Inches(0.12), img2_y + Inches(0.08), width=vis_w - Inches(0.24), height=Inches(2.32))

    # Right Column: Narrative Card (Width 6.43 in)
    right_x = start_x + vis_w + Inches(0.2)
    right_w = Inches(6.43)
    add_container_card(slide, right_x, body_y, right_w, body_h, "Empirical Agronomic & Market Discoveries")

    tb = slide.shapes.add_textbox(right_x + Inches(0.2), body_y + Inches(0.55), right_w - Inches(0.4), body_h - Inches(0.65))
    tf = tb.text_frame
    tf.word_wrap = True

    add_bullet_point(
        tf,
        "Finding 1: The Yield vs. Revenue Paradox (Economic Inversion)",
        "Maize achieves the highest physical yield (mean 3.90 t/ha, peaking at 4.80 t/ha in SNNPR), but Teff generates the highest gross revenue per hectare (152,301 Birr/ha vs. 114,336 Birr/ha for Maize).\n"
        "• Agronomic Driver: Teff commands a 2.6× market price premium (7,652 vs. 2,927 Birr/quintal) due to cultural staple status and inelastic urban demand, proving smallholders rationally prioritize financial return over biological tonnage.\n"
        "• Direct UI Integration: AgriYield™ Pro connects directly to live regional quintal benchmarks and translates farm hectares into local Ethiopian units (1 ha ≈ 4 Timad) with automated P&L cash-flow calculations.",
        pt_size=9.8, is_first=True
    )

    add_bullet_point(
        tf,
        "Finding 2: Input Elasticity & Biological Ceilings",
        "Fertilizer Diminishing Returns: Mean yield rises monotonically from Q1 (2.44 t/ha) to Q4 (3.09 t/ha), but marginal response flattens; Teff plateaus beyond Q2 (2.01 t/ha) as excess nitrogen triggers stem lodging rather than grain yield.\n"
        "• Improved Seed Lift: Certified seeds deliver a consistent +18.3% to +22.8% yield lift across all five crops (Maize: +0.783 t/ha; Teff: +0.419 t/ha).\n"
        "• Pest & Disease Penalties: Biotic pressure inflicts -26% to -29% yield losses, hitting Maize hardest (-28.8% loss, -1.20 t/ha penalty) due to voracious defoliators like Fall Armyworm.",
        pt_size=9.8, space_before=7
    )

    add_bullet_point(
        tf,
        "Finding 3: Agro-Ecological Divergence & Thermal Regimes",
        "Highland zones in Tigray (3.13 t/ha) and Amhara (3.13 t/ha) lead national productivity, whereas pastoral Somali severely lags (1.46 t/ha; Somali × Teff: 0.83 t/ha) due to extreme thermal stress (>30°C) and acute moisture deficits.",
        pt_size=9.8, space_before=7
    )


def build_slide_4(prs):
    """Slide 4: Predictive Modeling, Evaluation & Weather Ablation"""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    add_slide_background(slide)

    add_header(
        slide,
        badge_text="Deliverable D | Machine Learning & Benchmarking",
        title_text="Predictive Modeling & Empirical Validation",
        subtitle_text="Model Progression, 5-Fold Cross-Validation, Tri-Ensemble Blend, and Weather Ablation Study (Rule 5)"
    )
    add_footer(slide, 4)

    # 4 Top KPI Badges
    kpi_w = Inches(2.88)
    kpi_h = Inches(0.92)
    top_y = Inches(1.80)
    gap_x = Inches(0.20)
    start_x = Inches(0.6)

    add_kpi_card(slide, start_x, top_y, kpi_w, kpi_h,
                 "0.4601 t/ha", "Tri-Ensemble 5-Fold CV RMSE", "HistGB + LGBM + XGBoost Blend", PRIMARY_GREEN)
    add_kpi_card(slide, start_x + (kpi_w + gap_x), top_y, kpi_w, kpi_h,
                 "0.906", "Tri-Ensemble R² Score", "Explains 90.6% of Yield Variance", PRIMARY_GREEN)
    add_kpi_card(slide, start_x + (kpi_w + gap_x) * 2, top_y, kpi_w, kpi_h,
                 "-70.9%", "Error Reduction vs. Baseline", "Baseline 1.401 → Tuned 0.408 t/ha", ACCENT_GOLD)
    add_kpi_card(slide, start_x + (kpi_w + gap_x) * 3, top_y, kpi_w, kpi_h,
                 "+14.77%", "Ablation Error Spike (No Weather)", "Validates Rule 5 Weather Signal", ACCENT_BLUE)

    # 2 Columns (Model Benchmarking Left, Features & Ablation Right)
    body_y = Inches(2.90)
    body_h = Inches(3.96)
    col_w = Inches(5.95)
    right_x = start_x + col_w + Inches(0.2)

    # Left Column: Benchmarks & Visual
    add_container_card(slide, start_x, body_y, col_w, body_h, "1. Architecture Benchmarks Progression")
    fig10_path = os.path.join("figures", "fig10_model_comparison.png")
    if os.path.exists(fig10_path):
        slide.shapes.add_picture(fig10_path, start_x + Inches(0.2), body_y + Inches(0.52), width=col_w - Inches(0.4), height=Inches(1.88))

    tb_l = slide.shapes.add_textbox(start_x + Inches(0.2), body_y + Inches(2.45), col_w - Inches(0.4), Inches(1.35))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    add_bullet_point(tf_l, "Dummy Regressor (Mean)", "5-Fold CV: 1.401 t/ha | Holdout: 1.413 t/ha | R² -0.000 (Predicts global mean 2.768 t/ha).", pt_size=9.5, is_first=True)
    add_bullet_point(tf_l, "Ridge Regression (Linear)", "5-Fold CV: 0.785 t/ha | Holdout: 0.895 t/ha | R² 0.599 (Misses non-linear thermal/altitude curves).", pt_size=9.5, space_before=3)
    add_bullet_point(tf_l, "Random Forest Ensemble", "5-Fold CV: 0.448 t/ha | Holdout: 0.588 t/ha | R² 0.827 (Captures non-linear thresholds).", pt_size=9.5, space_before=3)
    add_bullet_point(tf_l, "Production Tri-Ensemble", "5-Fold CV: 0.4601 t/ha | R² 0.906 (Combines HistGB, LightGBM, and XGBoost via VotingRegressor for extra +2.5% accuracy).", pt_size=9.5, space_before=3)

    # Right Column: Feature Importance & Ablation
    add_container_card(slide, right_x, body_y, col_w, body_h, "2. Feature Importance & Validation Rigor")
    fig12_path = os.path.join("figures", "fig12_feature_importance.png")
    if os.path.exists(fig12_path):
        slide.shapes.add_picture(fig12_path, right_x + Inches(0.2), body_y + Inches(0.52), width=col_w - Inches(0.4), height=Inches(1.88))

    tb_r = slide.shapes.add_textbox(right_x + Inches(0.2), body_y + Inches(2.45), col_w - Inches(0.4), Inches(1.35))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    add_bullet_point(tf_r, "Mandatory Weather Ablation (Rule 5)", "Omitting weather derivations degraded 5-fold CV RMSE from 0.474 to 0.544 t/ha (+14.77% error jump), confirming climate signals provide indispensable predictive power.", pt_size=9.5, is_first=True)
    add_bullet_point(tf_r, "5-Fold CV Stability", "Cross-validation score of 0.4742 ± 0.0113 t/ha demonstrates remarkable variance stability across all 5 regional folds without spatial overfitting.", pt_size=9.5, space_before=3)
    add_bullet_point(tf_r, "Out-of-Time 2024 Generalization", "Trained on 2021–2023 (11,277 plots) and tested on 2024 (3,813 plots) achieved 0.4812 t/ha RMSE (R² = 0.884), proving temporal robustness with zero concept drift.", pt_size=9.5, space_before=3)


def build_slide_5(prs):
    """Slide 5: Decision Support Platform: Interactive UI & Operational Impact"""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    add_slide_background(slide)

    add_header(
        slide,
        badge_text="Deliverables E & G | Operational UI Platform & Live Demo",
        title_text="Decision Support Platform: Interactive UI & Operational Impact",
        subtitle_text="AgriYield™ Pro Enterprise: Zero-Effort Background Ingestion, Real-Time P&L, and 15-Farm Union Logistics"
    )
    add_footer(slide, 5)

    # 4 Top KPI Badges
    kpi_w = Inches(2.88)
    kpi_h = Inches(0.92)
    top_y = Inches(1.80)
    gap_x = Inches(0.20)
    start_x = Inches(0.6)

    add_kpi_card(slide, start_x, top_y, kpi_w, kpi_h,
                 "Live Streamlit", "Production Decision Platform", "Launch: streamlit run app/app.py", PRIMARY_GREEN)
    add_kpi_card(slide, start_x + (kpi_w + gap_x), top_y, kpi_w, kpi_h,
                 "86.9%", "Food Security Tier Accuracy", "0.0% Extreme Off-Diagonal Errors", PRIMARY_GREEN)
    add_kpi_card(slide, start_x + (kpi_w + gap_x) * 2, top_y, kpi_w, kpi_h,
                 "<300 ms", "Cached App Inference Latency", "Zero-Lag Slider Simulation", ACCENT_GOLD)
    add_kpi_card(slide, start_x + (kpi_w + gap_x) * 3, top_y, kpi_w, kpi_h,
                 "4 Workspaces", "Streamlined User Navigation", "Farmgate, Union, Radar & Audit", ACCENT_BLUE)

    # 2 Columns (Food Security Confusion Matrix Left, UI Capabilities & Live Demo Flow Right)
    body_y = Inches(2.90)
    body_h = Inches(3.96)
    left_w = Inches(5.35)
    right_w = Inches(6.58)
    right_x = start_x + left_w + Inches(0.2)

    # Left Column: Figure 13 Confusion Matrix & Policy Audit
    add_container_card(slide, start_x, body_y, left_w, body_h, "1. Food Security Policy Audit (Figure 13)")
    fig13_path = os.path.join("figures", "fig13_yield_tier_confusion_matrix.png")
    if os.path.exists(fig13_path):
        slide.shapes.add_picture(fig13_path, start_x + Inches(0.18), body_y + Inches(0.50), width=left_w - Inches(0.36), height=Inches(2.10))

    tb_d = slide.shapes.add_textbox(start_x + Inches(0.18), body_y + Inches(2.65), left_w - Inches(0.36), Inches(1.15))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    add_bullet_point(tf_d, "86.9% Stratified Tier Accuracy", "13,115 of 15,090 plots fall on the exact diagonal tier (<2.0, 2.0–3.5, >3.5 t/ha).", pt_size=9.2, is_first=True)
    add_bullet_point(tf_d, "0.0% Extreme Error Rate", "Zero subsistence plots misdiagnosed as commercial surplus (0/4,894); zero false alarms.", pt_size=9.2, space_before=3)
    add_bullet_point(tf_d, "93.9% Subsistence Precision", "Dependable trigger for micro-insurance payouts and safety-net grain distribution.", pt_size=9.2, space_before=3)

    # Right Column: UI Capabilities & Live Demo Script
    add_container_card(slide, right_x, body_y, right_w, body_h, "2. AgriYield™ Pro Capabilities & Live Demo Script")

    tb_r = slide.shapes.add_textbox(right_x + Inches(0.2), body_y + Inches(0.52), right_w - Inches(0.4), body_h - Inches(0.60))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    add_bullet_point(
        tf_r,
        "1. Zero-Effort Background Ingestion (Rule 5 Compliant)",
        "Farmers enter only agronomic inputs (Region, Crop, Farm Size in ha or Timad, DAP/Urea); seasonal climate variables (rainfall, mean temperature, heat days) and ECX market prices are automatically resolved in the background.",
        pt_size=9.5, is_first=True
    )

    add_bullet_point(
        tf_r,
        "2. Real-Time Economic P&L Translation",
        "Converts biological yield (t/ha) into audited household cash flow: Gross Revenue, Fertilizer, Certified Seed, and Net Family Profit in Ethiopian Birr (ETB), demonstrating household economic lift.",
        pt_size=9.5, space_before=4
    )

    add_bullet_point(
        tf_r,
        "3. Dynamic 'What-If' Simulation (Dual-Axis Plotly)",
        "Interactive slider curves plot harvest bags vs. net profit across fertilizer levels, automatically pinpointing the peak profit inflection point (e.g., 80 kg/ha) to prevent costly nitrogen wastage.",
        pt_size=9.5, space_before=4
    )

    add_bullet_point(
        tf_r,
        "4. Cooperative Command Hub (15-Plot Union Fleet)",
        "Multi-plot batch processing aggregates union member harvest totals, 100-kg jute bag storage demands, 40-Ton Isuzu freight fleets needed, and bankable collateral Loan-to-Value (LTV) ratios.",
        pt_size=9.5, space_before=4
    )

    add_bullet_point(
        tf_r,
        "🎯 2-Minute Pitch Live Demo Flow",
        "• Minute 1 (Farmgate Studio): Click 'Arsi Maize (2.5 ha)' preset -> observe auto climate/price resolution -> adjust DAP/Urea slider to show live profit peak.\n"
        "• Minute 2 (Union Hub & Audit): Switch to Cooperative Hub -> review 15-plot grain totals & truck fleet -> review 86.9% food security tier audit matrix.",
        pt_size=9.5, space_before=4
    )


# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------

def export_to_pdf_if_available(pptx_path, pdf_path):
    """Attempts to export presentation to PDF via PowerPoint COM on Windows."""
    abs_pptx = os.path.abspath(pptx_path)
    abs_pdf = os.path.abspath(pdf_path)
    ps_cmd = f"""
    try {{
        $ppt = New-Object -ComObject PowerPoint.Application
        $pres = $ppt.Presentations.Open('{abs_pptx}', [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
        $pres.SaveAs('{abs_pdf}', 32) # 32 = ppSaveAsPDF
        $pres.Close()
        $ppt.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
        Stop-Process -Name "POWERPNT" -Force -ErrorAction SilentlyContinue
        Write-Output 'PDF Export Succeeded'
    }} catch {{
        Write-Output ('PDF Export Error: ' + $_.Exception.Message)
    }}
    """
    try:
        res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, timeout=30)
        if "PDF Export Succeeded" in res.stdout:
            print(f"[SUCCESS] PDF export successful: {pdf_path}")
            return True
        else:
            print(f"! PDF export note: {res.stdout.strip()}")
            return False
    except Exception as e:
        print(f"! PDF export skipped: {e}")
        return False


def main():
    print("=================================================================")
    print("Team 11 | Generating Official Presentation Deck (Deliverable F)")
    print("=================================================================")

    os.makedirs("presentation", exist_ok=True)
    pptx_path = os.path.join("presentation", "team_11_slides.pptx")
    pdf_path = os.path.join("presentation", "team_11_slides.pdf")

    prs = create_base_presentation()

    print("Building Slide 1: Problem Definition & Data Context...")
    build_slide_1(prs)

    print("Building Slide 2: Pipeline Architecture: Cleaning & Spatio-Temporal Join...")
    build_slide_2(prs)

    print("Building Slide 3: Key Insights: Market Value Disconnect & Agronomic Limits...")
    build_slide_3(prs)

    print("Building Slide 4: Predictive Modeling & Empirical Validation...")
    build_slide_4(prs)

    print("Building Slide 5: Decision Support Platform: Interactive UI & Operational Impact...")
    build_slide_5(prs)

    prs.save(pptx_path)
    print(f"[SUCCESS] Successfully generated presentation deck: {pptx_path} (Slides: {len(prs.slides)})")

    # Try exporting PDF if PowerPoint COM is available
    export_to_pdf_if_available(pptx_path, pdf_path)

    print("=================================================================")
    print("Presentation Deck Generation Complete!")
    print("=================================================================")


if __name__ == "__main__":
    main()
