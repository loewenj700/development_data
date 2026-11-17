"""
Renewable Energy Progress Dashboard
A three-tab Streamlit app using Our World in Data renewable energy datasets.

Data sources:
  - share-electricity-renewables.csv (Our World in Data, Ember/IEA)
  - solar-capacity.csv (Our World in Data, IRENA)
  - wind-capacity.csv (Our World in Data, IRENA)
  - global-renewable-capacity-by-tech.csv (Our World in Data, IRENA)

Run from this folder:
  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Renewable Energy Progress",
    page_icon="⚡",
    layout="wide"
)

# ─── LOAD DATA ────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    df_share = pd.read_csv("data/share-electricity-renewables.csv")
    df_share.columns = ["Entity", "Code", "Year", "Renewables_pct"]

    df_solar = pd.read_csv("data/solar-capacity.csv")
    df_solar.columns = ["Entity", "Code", "Year", "Solar_GW"]

    df_wind = pd.read_csv("data/wind-capacity.csv")
    df_wind.columns = ["Entity", "Code", "Year", "Wind_GW"]

    df_tech = pd.read_csv("data/global-renewable-capacity-by-tech.csv")
    df_tech.columns = ["Entity", "Year", "Capacity_GW"]

    return df_share, df_solar, df_wind, df_tech

df_share, df_solar, df_wind, df_tech = load_data()

# ─── HEADER ──────────────────────────────────────────────────────────────────

st.title("Renewable Energy Progress Dashboard")
st.markdown(
    "Global renewable energy data from [Our World in Data](https://ourworldindata.org/energy) "
    "(IRENA / Ember / IEA). Solar capacity grew from **41 GW in 2010** to **1,424 GW in 2023** — "
    "a 34× increase in 13 years."
)

# ─── TABS ─────────────────────────────────────────────────────────────────────

tab1, tab2, tab3 = st.tabs([
    "🌍 Renewable Share by Country",
    "☀️ Solar & Wind Capacity Map",
    "📈 Global Capacity Growth"
])

# ─── TAB 1: Choropleth — % electricity from renewables ───────────────────────

with tab1:
    st.subheader("Share of Electricity from Renewables by Country")

    # Filter to actual countries (3-letter ISO codes)
    df_share_cty = df_share[
        df_share["Code"].notna() &
        (df_share["Code"].str.len() == 3)
    ].copy()

    year_min = int(df_share_cty["Year"].min())
    year_max = int(df_share_cty["Year"].max())
    selected_year = st.slider(
        "Select year",
        min_value=year_min,
        max_value=year_max,
        value=2023,
        step=1,
        key="tab1_year"
    )

    df_yr = df_share_cty[df_share_cty["Year"] == selected_year].copy()

    if df_yr.empty:
        st.warning(f"No data for {selected_year}. Try a different year.")
    else:
        colorscale = [
            [0, '#001F4D'],
            [0.3, '#003B8F'],
            [0.6, '#0066CC'],
            [0.8, '#00AAFF'],
            [1.0, '#00FF88']
        ]

        fig = go.Figure(data=go.Choropleth(
            locations=df_yr["Code"],
            z=df_yr["Renewables_pct"],
            text=df_yr["Entity"],
            colorscale=colorscale,
            autocolorscale=False,
            zmin=0,
            zmax=100,
            marker_line_color='rgba(100,120,180,0.4)',
            marker_line_width=0.5,
            colorbar=dict(
                title=dict(text="% renewable"),
                ticksuffix="%"
            ),
            hovertemplate="<b>%{text}</b><br>%{z:.1f}% renewable<extra></extra>"
        ))

        fig.update_layout(
            title=dict(
                text=f"Share of electricity from renewables ({selected_year})",
                x=0.5
            ),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth',
                bgcolor='rgba(0,10,30,1)',
                coastlinecolor='rgba(100,150,200,0.5)',
                showland=True,
                landcolor='rgba(20,30,60,1)',
                showocean=True,
                oceancolor='rgba(0,5,20,1)',
            ),
            paper_bgcolor='rgba(5,10,30,1)',
            font=dict(color='white'),
            margin=dict(l=0, r=0, t=50, b=0),
            height=500,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Summary stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Countries above 50%", f"{(df_yr['Renewables_pct'] >= 50).sum()}")
        col2.metric("Countries above 80%", f"{(df_yr['Renewables_pct'] >= 80).sum()}")
        world_avg = df_share[(df_share["Entity"] == "World") & (df_share["Year"] == selected_year)]["Renewables_pct"].values
        if len(world_avg) > 0:
            col3.metric("World average", f"{world_avg[0]:.1f}%")

# ─── TAB 2: Bubble map — solar / wind capacity ───────────────────────────────

with tab2:
    st.subheader("Installed Renewable Capacity by Country (GW)")

    energy_type = st.selectbox(
        "Energy type",
        options=["Solar", "Wind", "Combined (Solar + Wind)"],
        index=0,
        key="tab2_energy"
    )

    year_min2 = 2000
    year_max2 = 2023
    selected_year2 = st.slider(
        "Select year",
        min_value=year_min2,
        max_value=year_max2,
        value=2023,
        step=1,
        key="tab2_year"
    )

    if energy_type == "Solar":
        df_cap = df_solar[
            (df_solar["Year"] == selected_year2) &
            (df_solar["Code"].str.len() == 3) &
            (df_solar["Solar_GW"] > 0.05)
        ].copy()
        df_cap["GW"] = df_cap["Solar_GW"]
        bubble_color = "#FFD700"
        label = "Solar (GW)"

    elif energy_type == "Wind":
        df_cap = df_wind[
            (df_wind["Year"] == selected_year2) &
            (df_wind["Code"].str.len() == 3) &
            (df_wind["Wind_GW"] > 0.05)
        ].copy()
        df_cap["GW"] = df_cap["Wind_GW"]
        bubble_color = "#00BFFF"
        label = "Wind (GW)"

    else:  # Combined
        df_s = df_solar[(df_solar["Year"] == selected_year2) & (df_solar["Code"].str.len() == 3)][["Entity", "Code", "Solar_GW"]]
        df_w = df_wind[(df_wind["Year"] == selected_year2) & (df_wind["Code"].str.len() == 3)][["Entity", "Code", "Wind_GW"]]
        df_cap = df_s.merge(df_w, on=["Entity", "Code"], how="outer").fillna(0)
        df_cap["GW"] = df_cap["Solar_GW"] + df_cap["Wind_GW"]
        df_cap = df_cap[df_cap["GW"] > 0.05]
        bubble_color = "#00FF88"
        label = "Solar + Wind (GW)"

    if df_cap.empty:
        st.warning(f"No data for {energy_type} in {selected_year2}.")
    else:
        df_cap["marker_size"] = np.sqrt(df_cap["GW"]) * 2.5

        fig2 = go.Figure()
        fig2.add_trace(go.Scattergeo(
            locations=df_cap["Code"],
            text=df_cap["Entity"],
            customdata=df_cap["GW"].round(1),
            hovertemplate="<b>%{text}</b><br>%{customdata:.1f} GW<extra></extra>",
            marker=dict(
                size=df_cap["marker_size"].tolist(),
                sizemode='diameter',
                sizemin=4,
                color=bubble_color,
                opacity=0.75,
                line=dict(width=0.5, color='rgba(255,255,255,0.3)'),
            ),
            showlegend=False
        ))

        fig2.update_layout(
            title=dict(text=f"{energy_type} installed capacity ({selected_year2})", x=0.5),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth',
                bgcolor='rgba(0,10,30,1)',
                coastlinecolor='rgba(100,150,200,0.4)',
                showland=True,
                landcolor='rgba(20,30,60,1)',
                showocean=True,
                oceancolor='rgba(0,5,20,1)',
            ),
            paper_bgcolor='rgba(5,10,30,1)',
            font=dict(color='white'),
            margin=dict(l=0, r=0, t=50, b=0),
            height=500,
        )

        st.plotly_chart(fig2, use_container_width=True)

        # Top 5 table
        top5 = df_cap.nlargest(5, "GW")[["Entity", "GW"]].rename(columns={"Entity": "Country", "GW": label})
        top5[label] = top5[label].round(1)
        st.markdown(f"**Top 5 countries by {energy_type.lower()} capacity ({selected_year2}):**")
        st.dataframe(top5.reset_index(drop=True), use_container_width=True, hide_index=True)

# ─── TAB 3: Stacked area — global capacity by tech 2000–2023 ─────────────────

with tab3:
    st.subheader("Global Installed Renewable Capacity by Technology, 2000–2023")

    years_range = list(range(2000, 2024))

    def get_tech(entity):
        return (
            df_tech[(df_tech["Entity"] == entity) & (df_tech["Year"].isin(years_range))]
            [["Year", "Capacity_GW"]].set_index("Year")["Capacity_GW"]
        )

    solar_s = get_tech("Solar (total)").rename("Solar")
    wind_s = get_tech("Wind (total)").rename("Wind")
    hydro_s = get_tech("Hydropower (total)").rename("Hydro")
    all_s = get_tech("All renewables (total)").rename("All")
    other_s = (all_s - solar_s - wind_s - hydro_s).clip(lower=0).rename("Other")

    df_area = pd.concat([solar_s, wind_s, hydro_s, other_s, all_s], axis=1).reset_index()
    years = df_area["Year"].tolist()

    colors = {
        "Hydro": "#1E90FF",
        "Other": "#90EE90",
        "Wind": "#00BFFF",
        "Solar": "#FFD700",
    }

    fig3 = go.Figure()
    for tech in ["Hydro", "Other", "Wind", "Solar"]:
        fig3.add_trace(go.Scatter(
            x=years,
            y=df_area[tech].tolist(),
            name=tech,
            mode='lines',
            line=dict(width=1, color=colors[tech]),
            fill='tonexty',
            fillcolor=colors[tech],
            opacity=0.85,
            stackgroup='one',
        ))

    # Annotation: solar exceeds wind
    crossover_yr = int(df_area[df_area["Solar"] > df_area["Wind"]]["Year"].min())
    crossover_total = df_area[df_area["Year"] == crossover_yr]["All"].iloc[0]
    fig3.add_annotation(
        x=crossover_yr,
        y=crossover_total * 0.72,
        text=f"Solar exceeds wind ({crossover_yr})",
        font=dict(size=14, color="#FFD700"),
        showarrow=True,
        arrowhead=2,
        arrowcolor="#FFD700",
        ax=70, ay=-50,
        bgcolor="rgba(0,0,0,0.75)",
        bordercolor="#FFD700",
        borderwidth=1,
    )

    fig3.update_layout(
        title=dict(text="Global installed renewable capacity by technology (GW), 2000–2023", x=0.5),
        xaxis=dict(title="Year", tickmode='linear', dtick=5, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title="Installed capacity (GW)", gridcolor='rgba(255,255,255,0.1)'),
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(0,0,0,0.5)', font=dict(size=14)),
        paper_bgcolor='rgba(5,10,30,1)',
        plot_bgcolor='rgba(10,15,40,1)',
        font=dict(color='white'),
        margin=dict(l=80, r=20, t=60, b=60),
        height=500,
    )

    st.plotly_chart(fig3, use_container_width=True)

    # Key 2023 numbers
    row_2023 = df_area[df_area["Year"] == 2023].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Solar 2023", f"{row_2023['Solar']:.0f} GW")
    c2.metric("Wind 2023", f"{row_2023['Wind']:.0f} GW")
    c3.metric("Hydro 2023", f"{row_2023['Hydro']:.0f} GW")
    c4.metric("Total 2023", f"{row_2023['All']:.0f} GW")

st.caption(
    "Data: Our World in Data / IRENA / Ember / IEA. "
    "Solar capacity (IRENA), wind capacity (IRENA), "
    "renewable share (Ember). Last update: 2023."
)
