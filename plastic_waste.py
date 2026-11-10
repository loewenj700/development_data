"""
analysis.py — Ocean Plastic Choropleth
Loads OWID data, computes all numbers in the draft, and generates 3 charts.
Run from: drafts/2026-11-10_ocean-plastic-choropleth/
"""
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Point to chartkit (absolute path works from both main repo and worktree)
sys.path.insert(0, "/Users/loewenj700/Desktop/writing/.claude/skills/python-charts/scripts")
import chartkit as ck
from add_border import add_border

# ── Load data ──────────────────────────────────────────────────────────────────
df_abs = pd.read_csv("data/plastic-entering-ocean.csv")
df_cap = pd.read_csv("data/plastic-entering-ocean-per-capita.csv")

print("Absolute dataset columns:", df_abs.columns.tolist())
print(df_abs.head())
print()
print("Per-capita dataset columns:", df_cap.columns.tolist())
print(df_cap.head())
print()

# Rename for convenience
COL_ABS = "Plastic pollution entering the ocean through rivers"
COL_CAP = "Plastic pollution entering the ocean through rivers, per person"

# Check year coverage
print("Year(s) in absolute data:", df_abs["Year"].unique())
print("Year(s) in per-capita data:", df_cap["Year"].unique())
print()

# ── Core computations ──────────────────────────────────────────────────────────

# Total ocean plastic from rivers
total_tonnes = df_abs[COL_ABS].sum()
print(f"TOTAL ocean plastic (all countries, 2019): {total_tonnes:,.0f} tonnes")

# Top 15 by absolute volume (countries only)
top15_abs = (
    df_abs[df_abs["Code"].notna() & df_abs["Code"].str.match(r"^[A-Z]{3}$")]
    .sort_values(COL_ABS, ascending=False)
    .head(15)
    .copy()
)
top15_abs["pct_of_total"] = top15_abs[COL_ABS] / total_tonnes * 100
print("\nTop 15 by absolute volume (tonnes, 2019):")
print(top15_abs[["Entity", "Code", COL_ABS, "pct_of_total"]].to_string(index=False))

# Philippines
phil = df_abs[df_abs["Entity"] == "Philippines"][COL_ABS].values[0]
phil_pct = phil / total_tonnes * 100
print(f"\nPhilippines: {phil:,.0f} tonnes = {phil_pct:.1f}% of global total")

# India
india = df_abs[df_abs["Entity"] == "India"][COL_ABS].values[0]
india_pct = india / total_tonnes * 100
print(f"India: {india:,.0f} tonnes = {india_pct:.1f}% of global total")

# Malaysia
malaysia = df_abs[df_abs["Entity"] == "Malaysia"][COL_ABS].values[0]
malaysia_pct = malaysia / total_tonnes * 100
print(f"Malaysia: {malaysia:,.0f} tonnes = {malaysia_pct:.1f}% of global total")

# China
china = df_abs[df_abs["Entity"] == "China"][COL_ABS].values[0]
china_pct = china / total_tonnes * 100
print(f"China: {china:,.0f} tonnes = {china_pct:.1f}% of global total")

# Indonesia
indonesia = df_abs[df_abs["Entity"] == "Indonesia"][COL_ABS].values[0]
indonesia_pct = indonesia / total_tonnes * 100
print(f"Indonesia: {indonesia:,.0f} tonnes = {indonesia_pct:.1f}% of global total")

# Asia totals
asian_countries = [
    "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh",
    "Bhutan", "Brunei", "Cambodia", "China", "Cyprus",
    "East Timor", "Georgia", "India", "Indonesia", "Iran",
    "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan",
    "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Malaysia",
    "Maldives", "Mongolia", "Myanmar", "Nepal", "North Korea",
    "Oman", "Pakistan", "Palestine", "Philippines", "Qatar",
    "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria",
    "Taiwan", "Tajikistan", "Thailand", "Turkey", "Turkmenistan",
    "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen",
]

asia_df = df_abs[df_abs["Entity"].isin(asian_countries)]
asia_total = asia_df[COL_ABS].sum()
asia_pct = asia_total / total_tonnes * 100
print(f"\nAsia total: {asia_total:,.0f} tonnes = {asia_pct:.1f}% of global total")

# Top 15 by per capita
top15_cap = (
    df_cap[df_cap["Code"].notna() & df_cap["Code"].str.match(r"^[A-Z]{3}$")]
    .sort_values(COL_CAP, ascending=False)
    .head(15)
    .copy()
)
print("\nTop 15 by per capita (kg/person/year, 2019):")
print(top15_cap[["Entity", "Code", COL_CAP]].to_string(index=False))

# Philippines per capita
phil_cap = df_cap[df_cap["Entity"] == "Philippines"][COL_CAP].values[0]
print(f"\nPhilippines per capita: {phil_cap:.2f} kg/person/year")

# Malaysia per capita
malay_cap = df_cap[df_cap["Entity"] == "Malaysia"][COL_CAP].values[0]
print(f"Malaysia per capita: {malay_cap:.2f} kg/person/year")

# ── Chart 1: World choropleth — per capita plastic ─────────────────────────────
print("\n--- Chart 1: World choropleth per capita ---")

df_cap_countries = df_cap[
    df_cap["Code"].notna() & df_cap["Code"].str.match(r"^[A-Z]{3}$")
].copy()

# Custom reversed teal scale: low = pale, high = deep teal (more = worse)
teal_scale = [[0, "#E0F7FA"], [0.3, "#4DB6AC"], [0.6, "#00897B"], [1.0, "#004D40"]]

fig1 = go.Figure(go.Choropleth(
    locations=df_cap_countries["Code"],
    z=df_cap_countries[COL_CAP],
    colorscale=teal_scale,
    zmin=0,
    zmax=float(df_cap_countries[COL_CAP].quantile(0.98)),
    marker_line_color="white",
    marker_line_width=0.4,
    colorbar=dict(
        ticksuffix=" kg",
        thickness=18,
        len=0.6,
        x=0.98,
        tickfont=dict(size=28),
        title=dict(text="kg/person<br>/year", font=dict(size=28)),
    ),
))
fig1.update_geos(
    showframe=False,
    showcoastlines=False,
    projection_type="natural earth",
    showland=True,
    landcolor="#EDEDED",
    showcountries=False,
    lataxis_range=[-58, 85],
)
fig1.update_layout(
    template="plotly_white",
    width=1600,
    height=1000,
    font=dict(family="Arial, Helvetica, sans-serif", size=32, color="#222222"),
    title=dict(
        text=(
            "<b>Philippines sends more than a third of all river plastic to the ocean</b>"
            "<br><span style='font-size:28px;color:#6E6E6E'>"
            "Ocean plastic emitted per person (kg/year), 2019</span>"
        ),
        x=0.02,
        xanchor="left",
        y=0.97,
        yanchor="top",
        font=dict(size=36),
    ),
    margin=dict(l=20, r=20, t=170, b=110),
    paper_bgcolor="white",
    plot_bgcolor="white",
)
fig1.add_annotation(
    x=0.80, y=0.35,
    xref="paper", yref="paper",
    text="<b>Philippines</b><br>3.2 kg/person/yr",
    showarrow=True,
    arrowhead=2,
    ax=50, ay=-40,
    font=dict(size=28, color="#004D40"),
    bgcolor="white",
    bordercolor="#004D40",
    borderwidth=1,
)
fig1.add_annotation(
    x=0.74, y=0.37,
    xref="paper", yref="paper",
    text="<b>Malaysia</b><br>2.2 kg/person/yr",
    showarrow=True,
    arrowhead=2,
    ax=-50, ay=40,
    font=dict(size=26, color="#00897B"),
    bgcolor="white",
    bordercolor="#00897B",
    borderwidth=1,
)

ck.save(fig1, "chart_1.png")
add_border("chart_1.png")
print("Chart 1 saved.")

# ── Chart 2: Bubble scatter_geo — Asia zoom ────────────────────────────────────
print("\n--- Chart 2: Asia bubble map ---")

df_abs_countries = df_abs[
    df_abs["Code"].notna() & df_abs["Code"].str.match(r"^[A-Z]{3}$")
].copy()

df_bubble = df_abs_countries[df_abs_countries[COL_ABS] >= 100].copy()

fig2 = px.scatter_geo(
    df_bubble,
    locations="Code",
    size=COL_ABS,
    color=COL_ABS,
    hover_name="Entity",
    color_continuous_scale="Teal",
    size_max=70,
    projection="natural earth",
)
fig2.update_coloraxes(
    colorbar=dict(
        ticksuffix=" t",
        thickness=18,
        len=0.6,
        x=0.98,
        tickfont=dict(size=28),
        title=dict(text="Tonnes/yr", font=dict(size=28)),
    )
)
fig2.update_geos(
    showframe=False,
    showcoastlines=True,
    coastlinecolor="#CCCCCC",
    coastlinewidth=0.5,
    showland=True,
    landcolor="#F5F5F5",
    showocean=True,
    oceancolor="#E8F4F8",
    showlakes=False,
    showcountries=True,
    countrycolor="#DDDDDD",
    countrywidth=0.3,
    lonaxis_range=[70, 155],
    lataxis_range=[-15, 45],
)
fig2.update_layout(
    template="plotly_white",
    width=1600,
    height=1000,
    font=dict(family="Arial, Helvetica, sans-serif", size=32, color="#222222"),
    title=dict(
        text=(
            "<b>Asia dominates — the Philippines alone sends 36% of global river plastic</b>"
            "<br><span style='font-size:28px;color:#6E6E6E'>"
            "Ocean plastic emitted per country (absolute tonnes), 2019 — Asia focus</span>"
        ),
        x=0.02,
        xanchor="left",
        y=0.97,
        yanchor="top",
        font=dict(size=36),
    ),
    margin=dict(l=20, r=20, t=180, b=80),
    paper_bgcolor="white",
    plot_bgcolor="white",
)

ck.save(fig2, "chart_2.png")
add_border("chart_2.png")
print("Chart 2 saved.")

# ── Chart 3: Horizontal bar — top 15 ─────────────────────────────────────────
print("\n--- Chart 3: Top 15 horizontal bar ---")

top15 = top15_abs.head(15).copy()
top15 = top15.sort_values(COL_ABS, ascending=True)  # ascending for horizontal bar

# Color: teal gradient by rank
n = len(top15)
teal_colors = []
for i in range(n):
    ratio = i / (n - 1)
    r_val = int(224 - ratio * (224 - 0))
    g_val = int(247 - ratio * (247 - 77))
    b_val = int(250 - ratio * (250 - 64))
    teal_colors.append(f"rgb({r_val},{g_val},{b_val})")

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=top15[COL_ABS],
    y=top15["Entity"],
    orientation="h",
    marker_color=teal_colors,
    text=[f"{v:,.0f} t" for v in top15[COL_ABS]],
    textposition="outside",
    textfont=dict(size=28),
    cliponaxis=False,
))
fig3.update_layout(
    template="plotly_white",
    width=1600,
    height=1100,
    font=dict(family="Arial, Helvetica, sans-serif", size=32, color="#222222"),
    title=dict(
        text=(
            "<b>Top 15 countries by river plastic emitted to ocean</b>"
            "<br><span style='font-size:28px;color:#6E6E6E'>"
            "Absolute tonnes per year, 2019</span>"
        ),
        x=0.02,
        xanchor="left",
        y=0.97,
        yanchor="top",
        font=dict(size=36),
    ),
    margin=dict(l=200, r=320, t=180, b=100),
    paper_bgcolor="white",
    plot_bgcolor="white",
    showlegend=False,
)
fig3.update_xaxes(
    showgrid=True,
    gridcolor="#EEEEEE",
    showline=False,
    tickfont=dict(size=28),
    range=[0, top15[COL_ABS].max() * 1.3],
)
fig3.update_yaxes(
    showgrid=False,
    tickfont=dict(size=28),
    automargin=True,
)

ck.save(fig3, "chart_3.png")
add_border("chart_3.png")
print("Chart 3 saved.")

# ── Summary of key numbers ─────────────────────────────────────────────────────
print("\n=== KEY NUMBERS FOR DRAFT ===")
print(f"Total river plastic to ocean (2019): {total_tonnes:,.0f} tonnes")
print(f"Philippines: {phil:,.0f} tonnes ({phil_pct:.1f}%)")
print(f"India: {india:,.0f} tonnes ({india_pct:.1f}%)")
print(f"Malaysia: {malaysia:,.0f} tonnes ({malaysia_pct:.1f}%)")
print(f"China: {china:,.0f} tonnes ({china_pct:.1f}%)")
print(f"Indonesia: {indonesia:,.0f} tonnes ({indonesia_pct:.1f}%)")
print(f"Asia total: {asia_total:,.0f} tonnes ({asia_pct:.1f}%)")
print(f"Philippines per capita: {phil_cap:.2f} kg/person/year")
print(f"Malaysia per capita: {malay_cap:.2f} kg/person/year")
print(f"\nTop 5 absolute:")
for _, row in top15_abs.head(5).iterrows():
    print(f"  {row['Entity']}: {row[COL_ABS]:,.0f} tonnes ({row['pct_of_total']:.1f}%)")
