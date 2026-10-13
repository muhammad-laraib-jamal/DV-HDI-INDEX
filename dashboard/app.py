import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dash import Dash, dcc, html, Input, Output, State, ctx

from src.visualization import (
    load_data, get_latest_year, figure_to_base64,
    create_hdi_trend, create_top10_chart, create_bottom10_chart,
    create_life_expectancy_scatter, create_gni_scatter,
    create_mean_schooling_scatter, create_expected_schooling_scatter,
    create_hdi_distribution, create_correlation_heatmap,
)

df = load_data()
LATEST = get_latest_year(df)
YEARS = sorted(df["year"].unique(), reverse=True)
COUNTRIES = sorted(df["country"].unique())

app = Dash(
    __name__,
    assets_folder=str(Path(__file__).resolve().parent / "assets"),
    title="HDI Dashboard",
)

GRAPH_CONFIG = {"displaylogo": False}


def graph(graph_id):
    return dcc.Graph(id=graph_id, config=GRAPH_CONFIG, className="graph")


def image(image_id):
    return html.Img(id=image_id, className="seaborn-img", alt="")


def card(child, wide=False):
    return html.Div(child, className="chart-card wide" if wide else "chart-card")


def kpi(label, value_id, sub_id):
    return html.Div(
        [
            html.Div(label, className="kpi-label"),
            html.Div(id=value_id, className="kpi-value"),
            html.Div(id=sub_id, className="kpi-sub"),
        ],
        className="kpi",
    )


app.layout = html.Div(
    [
        html.Header(
            [
                html.H1("Human Development Index Dashboard"),
                html.P(
                    "Human Development Report data for 195 countries, "
                    "1990–2023  |  DV Lab project"
                ),
            ],
            className="header",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Year", htmlFor="year-dropdown"),
                        dcc.Dropdown(
                            id="year-dropdown",
                            options=[{"label": str(y), "value": int(y)} for y in YEARS],
                            value=LATEST,
                            clearable=False,
                        ),
                    ],
                    className="filter year-filter",
                ),
                html.Div(
                    [
                        html.Label("Country (scatter plots)", htmlFor="country-dropdown"),
                        dcc.Dropdown(
                            id="country-dropdown",
                            options=[{"label": c, "value": c} for c in COUNTRIES],
                            value=[],
                            multi=True,
                            searchable=True,
                            placeholder="All countries (type to search)",
                        ),
                    ],
                    className="filter country-filter",
                ),
                html.Button("Apply", id="apply-btn", n_clicks=0, className="btn primary"),
                html.Button("Reset", id="reset-btn", n_clicks=0, className="btn"),
            ],
            className="filter-bar",
        ),
        html.Div(id="filter-note", className="filter-note"),
        html.Div(
            [
                kpi("Average HDI", "kpi-avg", "kpi-avg-sub"),
                kpi("Highest HDI", "kpi-high", "kpi-high-sub"),
                kpi("Lowest HDI", "kpi-low", "kpi-low-sub"),
                kpi("Countries in dataset", "kpi-count", "kpi-count-sub"),
            ],
            className="kpi-row",
        ),
        html.Main(
            [
                card(graph("trend-chart"), wide=True),
                card(graph("top10-chart")),
                card(graph("bottom10-chart")),
                card(graph("life-chart")),
                card(graph("gni-chart")),
                card(graph("mean-school-chart")),
                card(graph("exp-school-chart")),
                card(image("distribution-img")),
                card(image("heatmap-img")),
            ],
            className="chart-grid",
        ),
        html.Footer(
            "Source: UNDP Human Development Report. Some missing values in the "
            "source data were filled by interpolation during preprocessing.",
            className="footer",
        ),
    ],
    className="page",
)


@app.callback(
    Output("year-dropdown", "value"),
    Output("country-dropdown", "value"),
    Output("kpi-avg", "children"),
    Output("kpi-avg-sub", "children"),
    Output("kpi-high", "children"),
    Output("kpi-high-sub", "children"),
    Output("kpi-low", "children"),
    Output("kpi-low-sub", "children"),
    Output("kpi-count", "children"),
    Output("kpi-count-sub", "children"),
    Output("filter-note", "children"),
    Output("trend-chart", "figure"),
    Output("top10-chart", "figure"),
    Output("bottom10-chart", "figure"),
    Output("life-chart", "figure"),
    Output("gni-chart", "figure"),
    Output("mean-school-chart", "figure"),
    Output("exp-school-chart", "figure"),
    Output("distribution-img", "src"),
    Output("distribution-img", "alt"),
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
    countries = countries or []

    data = df[df["year"] == year]
    high = data.loc[data["HDI"].idxmax()]
    low = data.loc[data["HDI"].idxmin()]

    if countries:
        note = (
            f"Showing {len(countries)} selected "
            f"{'country' if len(countries) == 1 else 'countries'} in the four "
            f"scatter plots. Rankings, distribution and correlation use all "
            f"{data['country'].nunique()} countries for {year}."
        )
    else:
        note = (
            f"Showing all countries for {year}. The trend chart always covers "
            f"1990–2023."
        )

    dist_alt = f"Histogram of HDI values across countries in {year}"
    heat_alt = f"Correlation heatmap of HDI indicators in {year}"

    return (
        year,
        countries,
        f"{data['HDI'].mean():.3f}",
        f"All countries, {year}",
        f"{high['HDI']:.3f}",
        high["country"],
        f"{low['HDI']:.3f}",
        low["country"],
        f"{data['country'].nunique()}",
        "Includes interpolated values",
        note,
        create_hdi_trend(df),
        create_top10_chart(df, year),
        create_bottom10_chart(df, year),
        create_life_expectancy_scatter(df, year, countries),
        create_gni_scatter(df, year, countries),
        create_mean_schooling_scatter(df, year, countries),
        create_expected_schooling_scatter(df, year, countries),
        figure_to_base64(create_hdi_distribution(df, year)),
        dist_alt,
        figure_to_base64(create_correlation_heatmap(df, year)),
        heat_alt,
    )


if __name__ == "__main__":
    app.run(debug=True)