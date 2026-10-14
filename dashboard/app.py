import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, ctx, no_update

from src.visualization import (
    load_data, get_latest_year, figure_to_base64,
    create_hdi_trend, create_top10_chart, create_bottom10_chart,
    create_life_expectancy_scatter, create_gni_scatter,
    create_mean_schooling_scatter, create_expected_schooling_scatter,
    create_hdi_distribution, create_correlation_heatmap,
)

# =========================================================
# DATA
# =========================================================

df = load_data()
LATEST = get_latest_year(df)
FIRST = int(df["year"].min())
YEARS = sorted(df["year"].unique(), reverse=True)
COUNTRIES = sorted(df["country"].unique())
TOTAL_COUNTRIES = df["country"].nunique()

app = Dash(
    __name__,
    assets_folder=str(Path(__file__).resolve().parent / "assets"),
    title="HDI Dashboard",
)

GRAPH_CONFIG = {"displaylogo": False, "responsive": True}
LOADING_COLOUR = "#0077c8"


# =========================================================
# LAYOUT HELPERS
# =========================================================

def graph(graph_id, figure=None):
    # Start from an empty figure so the chart has a valid layout before the
    # first callback fills it in.
    figure = figure if figure is not None else go.Figure()
    return dcc.Loading(
        dcc.Graph(id=graph_id, figure=figure, config=GRAPH_CONFIG, className="graph"),
        type="circle",
        color=LOADING_COLOUR,
    )


def image(image_id):
    return dcc.Loading(
        html.Img(id=image_id, className="seaborn-img", alt=""),
        type="circle",
        color=LOADING_COLOUR,
    )


def kpi(label_id, value_id, sub_id):
    return html.Div(
        [
            html.Div(id=label_id, className="kpi-label"),
            html.Div(id=value_id, className="kpi-value"),
            html.Div(id=sub_id, className="kpi-sub"),
        ],
        className="kpi",
    )


def section(title, description, children):
    return html.Section(
        [
            html.Div(
                [html.H2(title), html.P(description)],
                className="section-head",
            ),
            html.Div(children, className="chart-grid"),
        ],
        className="section",
    )


def rankings_section(top10_fig, bottom10_fig):
    """Built fresh on every global view, so the charts always size correctly.
    (Plotly cannot size a chart that is drawn inside a hidden container.)"""
    return section(
        "Rankings",
        f"The 10 highest and 10 lowest HDI scores among all "
        f"{TOTAL_COUNTRIES} countries in the selected year.",
        [
            html.Div(graph("top10-chart", top10_fig), className="chart-card"),
            html.Div(graph("bottom10-chart", bottom10_fig), className="chart-card"),
        ],
    )


app.layout = html.Div(
    [
        html.Header(
            html.Div(
                [
                    html.Div(
                        [
                            html.H1("Human Development Index Dashboard"),
                            html.P(
                                f"Human Development Report data for "
                                f"{TOTAL_COUNTRIES} countries, {FIRST}–{LATEST}"
                            ),
                        ]
                    ),
                    html.Span("DV Lab project", className="project-tag"),
                ],
                className="header-inner",
            ),
            className="header",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Year", htmlFor="year-dropdown"),
                                dcc.Dropdown(
                                    id="year-dropdown",
                                    options=[
                                        {"label": str(y), "value": int(y)}
                                        for y in YEARS
                                    ],
                                    value=LATEST,
                                    clearable=False,
                                ),
                            ],
                            className="filter year-filter",
                        ),
                        html.Div(
                            [
                                html.Label(
                                    "Countries to compare",
                                    htmlFor="country-dropdown",
                                ),
                                dcc.Dropdown(
                                    id="country-dropdown",
                                    options=[
                                        {"label": c, "value": c}
                                        for c in COUNTRIES
                                    ],
                                    value=[],
                                    multi=True,
                                    searchable=True,
                                    placeholder="All countries. Type to search and add countries.",
                                ),
                            ],
                            className="filter country-filter",
                        ),
                        html.Div(
                            [
                                html.Button(
                                    "Apply", id="apply-btn", n_clicks=0,
                                    className="btn primary",
                                ),
                                html.Button(
                                    "Reset", id="reset-btn", n_clicks=0,
                                    className="btn",
                                ),
                            ],
                            className="filter-actions",
                        ),
                    ],
                    className="filter-bar",
                ),
                html.Div(
                    [
                        html.Span(id="view-pill", className="pill"),
                        html.Span(
                            "You changed a filter. Press Apply to update the charts.",
                            id="pending-hint",
                            className="pending hidden",
                            role="status",
                        ),
                    ],
                    className="status-row",
                ),
            ],
            className="filter-wrap",
        ),
        html.Div(
            [
                html.P(id="filter-note", className="filter-note"),
                html.Div(
                    [
                        kpi("kpi-avg-label", "kpi-avg", "kpi-avg-sub"),
                        kpi("kpi-high-label", "kpi-high", "kpi-high-sub"),
                        kpi("kpi-low-label", "kpi-low", "kpi-low-sub"),
                        kpi("kpi-count-label", "kpi-count", "kpi-count-sub"),
                    ],
                    className="kpi-strip",
                ),
                section(
                    "HDI over time",
                    "Average HDI of all countries. Select countries to see "
                    "their own trend against the all-country average.",
                    [html.Div(graph("trend-chart"), className="chart-card wide")],
                ),
                html.Div(id="rankings-wrap"),
                section(
                    "Development indicators and HDI",
                    "Each point is one country in the selected year. "
                    "Hover over a point for exact values.",
                    [
                        html.Div(graph("life-chart"), className="chart-card"),
                        html.Div(graph("gni-chart"), className="chart-card"),
                        html.Div(graph("mean-school-chart"), className="chart-card"),
                        html.Div(graph("exp-school-chart"), className="chart-card"),
                    ],
                ),
                section(
                    "Distribution and correlation",
                    "How HDI is spread across countries, and how closely the "
                    "indicators move together.",
                    [
                        html.Div(image("distribution-img"), id="distribution-card"),
                        html.Div(image("heatmap-img"), id="heatmap-card"),
                    ],
                ),
                html.Footer(
                    "Source: UNDP Human Development Report. Some missing "
                    "values in the source data were filled by interpolation "
                    "during preprocessing.",
                    className="footer",
                ),
            ],
            className="page",
        ),
        dcc.Store(id="applied-filters"),
    ],
    className="app-shell",
)


# =========================================================
# CALLBACK HELPERS
# =========================================================

HIDDEN = "hidden"


def scoped(year, countries):
    """Rows for the selected year, limited to the chosen countries."""
    data = df[df["year"] == year]
    if countries:
        chosen = data[data["country"].isin(countries)]
        if not chosen.empty:
            return chosen
    return data


def mean_hdi(year, countries):
    data = df[df["year"] == year]
    if countries:
        data = data[data["country"].isin(countries)]
    return data["HDI"].mean() if not data.empty else None


# =========================================================
# MAIN CALLBACK: Apply / Reset
# =========================================================

@app.callback(
    Output("year-dropdown", "value"),
    Output("country-dropdown", "value"),
    Output("applied-filters", "data"),
    Output("view-pill", "children"),
    Output("view-pill", "className"),
    Output("filter-note", "children"),
    Output("kpi-avg-label", "children"),
    Output("kpi-avg", "children"),
    Output("kpi-avg-sub", "children"),
    Output("kpi-high-label", "children"),
    Output("kpi-high", "children"),
    Output("kpi-high-sub", "children"),
    Output("kpi-low-label", "children"),
    Output("kpi-low", "children"),
    Output("kpi-low-sub", "children"),
    Output("kpi-count-label", "children"),
    Output("kpi-count", "children"),
    Output("kpi-count-sub", "children"),
    Output("trend-chart", "figure"),
    Output("rankings-wrap", "children"),
    Output("life-chart", "figure"),
    Output("gni-chart", "figure"),
    Output("mean-school-chart", "figure"),
    Output("exp-school-chart", "figure"),
    Output("distribution-card", "className"),
    Output("distribution-img", "src"),
    Output("distribution-img", "alt"),
    Output("heatmap-card", "className"),
    Output("heatmap-img", "src"),
    Output("heatmap-img", "alt"),
    Input("apply-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    State("year-dropdown", "value"),
    State("country-dropdown", "value"),
)
def update_dashboard(apply_clicks, reset_clicks, year, countries):
    if ctx.triggered_id == "reset-btn" or year is None:
        year, countries = LATEST, []
    countries = sorted(countries or [])
    comparing = bool(countries)

    data = scoped(year, countries)
    high = data.loc[data["HDI"].idxmax()]
    low = data.loc[data["HDI"].idxmin()]

    # ---- KPI strip ---------------------------------------------------
    scope_word = "selected countries" if comparing else "all countries"
    avg_now = data["HDI"].mean()
    avg_first = mean_hdi(FIRST, countries)

    if year == FIRST or avg_first is None:
        avg_sub = f"Average of {scope_word}"
    else:
        avg_sub = f"{avg_now - avg_first:+.3f} since {FIRST}"

    if comparing:
        labels = ("Average HDI (selected)", "Highest HDI (selected)",
                  "Lowest HDI (selected)", "Countries selected")
        count_sub = f"of {TOTAL_COUNTRIES} in the dataset"
    else:
        labels = ("Average HDI", "Highest HDI", "Lowest HDI",
                  "Countries in dataset")
        count_sub = "Includes interpolated values"

    # ---- View status and note ---------------------------------------
    if comparing:
        pill = (f"Comparing {len(countries)} "
                f"{'country' if len(countries) == 1 else 'countries'}")
        pill_class = "pill comparing"
        note = (
            f"Showing the trend and the four indicator plots for the "
            f"selected countries. Rankings and the HDI distribution compare "
            f"all {TOTAL_COUNTRIES} countries, so they are hidden while "
            f"countries are selected. The correlation heatmap still uses all "
            f"{TOTAL_COUNTRIES} countries. Press Reset to bring everything back."
        )
    else:
        pill = f"Global view: all {TOTAL_COUNTRIES} countries, {year}"
        pill_class = "pill"
        note = (
            f"Showing all countries for {year}. The trend line always covers "
            f"{FIRST}–{LATEST}. Select countries to compare their HDI trends."
        )

    # ---- Charts ------------------------------------------------------
    trend = create_hdi_trend(df, countries, year)
    life = create_life_expectancy_scatter(df, year, countries)
    gni = create_gni_scatter(df, year, countries)
    mean_school = create_mean_schooling_scatter(df, year, countries)
    exp_school = create_expected_schooling_scatter(df, year, countries)
    heatmap_src = figure_to_base64(create_correlation_heatmap(df, year))
    heatmap_alt = f"Correlation heatmap of HDI indicators in {year}"

    if comparing:
        rankings = None
        dist_class = "hidden"
        dist_src = dist_alt = no_update
        heatmap_class = "chart-card wide centered"
    else:
        rankings = rankings_section(
            create_top10_chart(df, year), create_bottom10_chart(df, year)
        )
        dist_class = "chart-card"
        dist_src = figure_to_base64(create_hdi_distribution(df, year))
        dist_alt = f"Histogram of HDI values across countries in {year}"
        heatmap_class = "chart-card"

    return (
        year,
        countries,
        {"year": year, "countries": countries},
        pill,
        pill_class,
        note,
        labels[0], f"{avg_now:.3f}", avg_sub,
        labels[1], f"{high['HDI']:.3f}", high["country"],
        labels[2], f"{low['HDI']:.3f}", low["country"],
        labels[3], f"{data['country'].nunique()}", count_sub,
        trend,
        rankings,
        life,
        gni,
        mean_school,
        exp_school,
        dist_class,
        dist_src,
        dist_alt,
        heatmap_class,
        heatmap_src,
        heatmap_alt,
    )


# =========================================================
# HINT CALLBACK: filters changed but not applied yet
# =========================================================

@app.callback(
    Output("pending-hint", "className"),
    Input("year-dropdown", "value"),
    Input("country-dropdown", "value"),
    State("applied-filters", "data"),
)
def show_pending_hint(year, countries, applied):
    if not applied:
        return "pending hidden"
    same = (
        year == applied["year"]
        and sorted(countries or []) == sorted(applied["countries"])
    )
    return "pending hidden" if same else "pending"


if __name__ == "__main__":
    app.run(debug=True)