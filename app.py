import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

logging.getLogger("streamlit").setLevel(logging.ERROR)

st.set_page_config(
    page_title="EU CO2 Cars Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

EARTH_SCALE = [
    [0.00, "#52b788"],
    [0.25, "#95d5b2"],
    [0.50, "#d4a373"],
    [0.75, "#bc8a5f"],
    [1.00, "#774936"],
]

LINE_PALETTE = [
    "#2d6a4f", "#774936", "#40916c", "#bc8a5f",
    "#1b4332", "#9c6644", "#588157", "#7f5539",
    "#52b788", "#d4a373",
]

st.markdown(
    """
    <style>
        .stApp { background-color: #faf6ef; }
        h1, h2, h3, h4, p, label, span, div { color: #000000; }
        [data-testid="stMetricValue"] { color: #000000; font-weight: 600; }
        [data-testid="stMetricLabel"] { color: #000000; }
        [data-baseweb="popover"] li,
        [data-baseweb="popover"] span,
        [data-baseweb="popover"] div { color: #ffffff !important; }
        [data-baseweb="select"] [role="option"] { color: #ffffff !important; }
        [data-baseweb="select"] *,
        [data-baseweb="select"] div[role="combobox"],
        [data-baseweb="select"] div[role="combobox"] *,
        [data-baseweb="select"] input { color: #ffffff !important; }
        [data-baseweb="tag"] * { color: #ffffff !important; }
        [data-testid="stDownloadButton"] button,
        [data-testid="stDownloadButton"] button *,
        .stDownloadButton button,
        .stDownloadButton button * { color: #ffffff !important; }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px; background-color: #f0e7d6; padding: 4px;
            border-radius: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 18px; border-radius: 6px; color: #6b705c;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2d6a4f; color: white;
        }
        #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

EU_AGGREGATE_CODES = {"EU27_2020", "EU28", "EU27", "EA", "EA19", "EA20"}

@st.cache_data
def load_dataset(path="data/co2_cars.csv"):
    raw = pd.read_csv(path)
    raw["obs_value"] = pd.to_numeric(raw["obs_value"], errors="coerce")
    raw = raw.dropna(subset=["obs_value"])
    raw["time"] = raw["time"].astype(int)
    return raw

df = load_dataset()
countries_df = df[~df["geo"].isin(EU_AGGREGATE_CODES)].copy()
all_countries = sorted(countries_df["geo_label"].unique())
year_min, year_max = int(countries_df["time"].min()), int(countries_df["time"].max())

st.title("EU New Passenger Cars CO2 Dashboard")
st.markdown(
    "Average CO2 emissions per kilometre from newly registered passenger "
    "cars across European countries, 2000-2024. Source: "
    "[European Environment Agency](https://www.eea.europa.eu/en/datahub/datahubitem-view/5d252092-d328-40d8-bca2-c0734bd6143b) "
    "(EU SDG indicator 13.31)."
)

tab_overview, tab_trends, tab_country, tab_data = st.tabs(
    ["Overview", "Trends", "Country deep-dive", "Data"]
)

with tab_overview:
    latest_year = year_max
    latest = countries_df[countries_df["time"] == latest_year]
    earliest = countries_df[countries_df["time"] == year_min]
    avg_now = latest["obs_value"].mean()
    avg_then = earliest["obs_value"].mean()
    pct_change = (avg_now - avg_then) / avg_then * 100
    best = latest.loc[latest["obs_value"].idxmin()]
    worst = latest.loc[latest["obs_value"].idxmax()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"EU average ({latest_year})", f"{avg_now:.1f} g/km")
    c2.metric(
        f"Change since {year_min}",
        f"{avg_now - avg_then:+.1f} g/km",
        f"{pct_change:+.1f}%",
        delta_color="inverse",
    )
    c3.metric(f"Lowest emitter ({latest_year})", best["geo_label"], f"{best['obs_value']:.1f} g/km")
    c4.metric(
        f"Highest emitter ({latest_year})",
        worst["geo_label"],
        f"{worst['obs_value']:.1f} g/km",
        delta_color="inverse",
    )

    st.markdown("&nbsp;")
    map_col, bar_col = st.columns([3, 2])

    with map_col:
        st.subheader(f"Where things stand in {latest_year}")
        map_fig = px.choropleth(
            latest,
            locations="geo_label",
            locationmode="country names",
            color="obs_value",
            color_continuous_scale=EARTH_SCALE,
            scope="europe",
            labels={"obs_value": "g CO2/km"},
        )
        map_fig.update_layout(
            height=520,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            geo=dict(bgcolor="rgba(0,0,0,0)"),
            font=dict(color="#000000"),
            coloraxis_colorbar=dict(tickfont=dict(color="#000000"), title=dict(font=dict(color="#000000"))),
        )
        st.plotly_chart(map_fig, use_container_width=True)

    with bar_col:
        st.subheader("Country ranking")
        ranking = latest.sort_values("obs_value")
        bar_fig = px.bar(
            ranking,
            x="obs_value",
            y="geo_label",
            orientation="h",
            color="obs_value",
            color_continuous_scale=EARTH_SCALE,
            labels={"obs_value": "g CO2/km", "geo_label": ""},
        )
        bar_fig.update_layout(
            height=520,
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#000000"),
            xaxis=dict(tickfont=dict(color="#000000"), title=dict(font=dict(color="#000000"))),
            yaxis=dict(tickfont=dict(color="#000000"), title=dict(font=dict(color="#000000"))),
        )
        st.plotly_chart(bar_fig, use_container_width=True)

with tab_trends:
    st.subheader("Trajectories over time")
    preferred = ["Germany", "France", "Italy", "Spain", "Poland", "Netherlands"]
    default_pick = [c for c in preferred if c in all_countries] or all_countries[:5]
    picked = st.multiselect("Countries to plot", all_countries, default=default_pick)
    yr_range = st.slider("Year range", year_min, year_max, (year_min, year_max))

    plot_df = countries_df[
        countries_df["geo_label"].isin(picked)
        & countries_df["time"].between(*yr_range)
    ].sort_values(["geo_label", "time"])

    if plot_df.empty:
        st.info("Pick at least one country to see the trend.")
    else:
        line_fig = px.line(
            plot_df,
            x="time",
            y="obs_value",
            color="geo_label",
            color_discrete_sequence=LINE_PALETTE,
            labels={"time": "Year", "obs_value": "g CO2/km", "geo_label": "Country"},
            markers=True,
        )
        if yr_range[0] <= 2021 <= yr_range[1]:
            line_fig.add_vline(
                x=2021,
                line_width=1,
                line_dash="dot",
                line_color="#6b705c",
                annotation_text="WLTP test procedure",
                annotation_position="top right",
                annotation_font_color="#6b705c",
            )
        line_fig.update_layout(
            height=540,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#fdfaf3",
            hovermode="x unified",
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center", font=dict(color="#000000")),
            font=dict(color="#000000"),
            xaxis=dict(tickfont=dict(color="#000000"), title=dict(font=dict(color="#000000"))),
            yaxis=dict(tickfont=dict(color="#000000"), title=dict(font=dict(color="#000000"))),
        )
        st.plotly_chart(line_fig, use_container_width=True)
        st.caption(
            "From 2021 onwards values are reported under the WLTP test procedure "
            "instead of NEDC. The two methods are not directly comparable, which "
            "explains the upward step in 2021."
        )

def rank_in_year(year_snapshot, country):
    if year_snapshot.empty or country not in set(year_snapshot["geo_label"]):
        return "n/a"
    rk = year_snapshot["obs_value"].rank(method="min").astype(int)
    pos = int(rk[year_snapshot["geo_label"] == country].iloc[0])
    return f"{pos} of {len(year_snapshot)}"

with tab_country:
    st.subheader("Country deep-dive")
    default_idx = all_countries.index("Germany") if "Germany" in all_countries else 0
    chosen = st.selectbox("Choose a country", all_countries, index=default_idx)
    cdata = countries_df[countries_df["geo_label"] == chosen].sort_values("time")

    if cdata.empty:
        st.warning("No data available for this country.")
    else:
        first_row = cdata.iloc[0]
        last_row = cdata.iloc[-1]
        net_change = last_row["obs_value"] - first_row["obs_value"]
        latest_snap = countries_df[countries_df["time"] == year_max]
        eu_latest_avg = latest_snap["obs_value"].mean()
        gap_to_eu = last_row["obs_value"] - eu_latest_avg

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"{int(last_row['time'])} value", f"{last_row['obs_value']:.1f} g/km")
        m2.metric(
            "Net change",
            f"{net_change:+.1f} g/km",
            f"{int(first_row['time'])} to {int(last_row['time'])}",
            delta_color="inverse",
        )
        m3.metric("EU rank (lower = better)", rank_in_year(latest_snap, chosen))
        m4.metric(
            "Gap to EU average",
            f"{gap_to_eu:+.1f} g/km",
            "Above EU avg" if gap_to_eu > 0 else "Below EU avg",
            delta_color="inverse",
        )

        st.markdown("&nbsp;")
        eu_trend = (
            countries_df.groupby("time", as_index=False)["obs_value"]
            .mean()
            .rename(columns={"obs_value": "eu_avg"})
        )
        merged = cdata.merge(eu_trend, on="time")

        compare = go.Figure()
        compare.add_trace(go.Scatter(
            x=merged["time"], y=merged["eu_avg"],
            name="EU average", mode="lines",
            line=dict(color="#bc8a5f", width=2, dash="dash"),
        ))
        compare.add_trace(go.Scatter(
            x=merged["time"], y=merged["obs_value"],
            name=chosen, mode="lines+markers",
            line=dict(color="#2d6a4f", width=3),
            marker=dict(size=7),
        ))
        compare.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#fdfaf3",
            xaxis_title="Year",
            yaxis_title="g CO2/km",
            hovermode="x unified",
            legend=dict(orientation="h", y=1.1, x=0, font=dict(color="#000000")),
            font=dict(color="#000000"),
            xaxis=dict(tickfont=dict(color="#000000"), title=dict(font=dict(color="#000000"))),
            yaxis=dict(tickfont=dict(color="#000000"), title=dict(font=dict(color="#000000"))),
        )
        st.plotly_chart(compare, use_container_width=True)

        yoy = cdata.copy()
        yoy["delta"] = yoy["obs_value"].diff()
        yoy = yoy.dropna(subset=["delta"])
        yoy["bar_color"] = yoy["delta"].apply(lambda v: "#774936" if v > 0 else "#2d6a4f")

        yoy_fig = go.Figure(go.Bar(
            x=yoy["time"], y=yoy["delta"],
            marker_color=yoy["bar_color"],
        ))
        yoy_fig.update_layout(
            title=dict(text="Year-on-year change", font=dict(color="#000000")),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#fdfaf3",
            xaxis_title="Year",
            yaxis_title="Change in g CO2/km",
            font=dict(color="#000000"),
            xaxis=dict(tickfont=dict(color="#000000"), title=dict(font=dict(color="#000000"))),
            yaxis=dict(tickfont=dict(color="#000000"), title=dict(font=dict(color="#000000"))),
        )
        st.plotly_chart(yoy_fig, use_container_width=True)

with tab_data:
    st.subheader("Underlying dataset")
    yrs = st.slider(
        "Year range", year_min, year_max, (year_min, year_max),
        key="data_tab_years",
    )
    chosen_set = st.multiselect(
        "Countries (leave empty for all)",
        all_countries, default=[], key="data_tab_countries",
    )

    view = countries_df[countries_df["time"].between(*yrs)]
    if chosen_set:
        view = view[view["geo_label"].isin(chosen_set)]

    pretty = (
        view[["geo_label", "time", "obs_value"]]
        .rename(columns={"geo_label": "Country", "time": "Year", "obs_value": "CO2 (g/km)"})
        .sort_values(["Year", "Country"], ascending=[False, True])
    )

    st.dataframe(pretty, use_container_width=True, hide_index=True)

    st.download_button(
        "Download filtered data (CSV)",
        data=pretty.to_csv(index=False).encode("utf-8"),
        file_name=f"co2_cars_{yrs[0]}_{yrs[1]}.csv",
        mime="text/csv",
    )

    with st.expander("About this dataset"):
        st.markdown(
            "**Source.** European Environment Agency, EU SDG indicator 13.31 "
            "(average CO2 emissions per km from new passenger cars).\n\n"
            "**Coverage.** EU Member States plus a small number of associated "
            "countries, annual values from 2000 to 2024. The 2024 figures are "
            "provisional.\n\n"
            "**Methodology.** Up to 2020, emissions are reported under the "
            "New European Driving Cycle (NEDC). From 2021 onward, the Worldwide "
            "harmonised Light vehicles Test Procedure (WLTP) applies. The two "
            "methods are not directly comparable, which is why a step appears in "
            "the data in 2021.\n\n"
            "**Regulatory context.** Regulation (EU) 2019/631 sets fleet-wide "
            "CO2 targets for manufacturers. The values shown here are the "
            "realised outcomes reported by Member States."
        )

st.markdown("---")
st.caption("5DATA004W Data Science Project Lifecycle. University of Westminster.")
