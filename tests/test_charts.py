from plotly.graph_objects import Figure as PlotlyFigure
from matplotlib.figure import Figure as MplFigure

from src.visualization import (
    load_data, get_latest_year, figure_to_base64,
    create_hdi_trend, create_top10_chart, create_bottom10_chart,
    create_life_expectancy_scatter, create_gni_scatter,
    create_mean_schooling_scatter, create_expected_schooling_scatter,
    create_hdi_distribution, create_correlation_heatmap,
)

df = load_data()
year = get_latest_year(df)
two = ["India", "China"] if {"India", "China"} <= set(df["country"]) else list(df["country"].unique()[:2])

plotly_charts = {
    "1 HDI trend": create_hdi_trend(df),
    "2 Top 10": create_top10_chart(df, year),
    "3 Bottom 10": create_bottom10_chart(df, year),
    "4 Life expectancy": create_life_expectancy_scatter(df, year),
    "5 GNI": create_gni_scatter(df, year),
    "6 Mean schooling": create_mean_schooling_scatter(df, year),
    "7 Expected schooling": create_expected_schooling_scatter(df, year),
}
for name, fig in plotly_charts.items():
    assert isinstance(fig, PlotlyFigure), name
    print("OK Plotly  :", name)

for name, fig in {
    "8 Distribution": create_hdi_distribution(df, year),
    "9 Heatmap": create_correlation_heatmap(df, year),
}.items():
    assert isinstance(fig, MplFigure), name
    assert figure_to_base64(fig).startswith("data:image/png;base64,"), name
    print("OK Seaborn :", name)

# Filter checks
sc = create_life_expectancy_scatter(df, year, countries=two)
assert len(sc.data[0].x) == 2
print("Scatter points with 2 countries:", len(sc.data[0].x), "(expected 2)")

assert len(create_top10_chart(df, 1990).data[0].y) == 10
print("Top 10 rows for 1990:", len(create_top10_chart(df, 1990).data[0].y), "(expected 10)")

assert isinstance(create_top10_chart(df, 1800), PlotlyFigure)
print("Empty-year chart handled:", isinstance(create_top10_chart(df, 1800), PlotlyFigure))

# Trend with selected countries: one line per country + 1 average line
trend = create_hdi_trend(df, countries=two, year=year)
names = [t.name for t in trend.data]
assert len(trend.data) == len(two) + 1, names
assert "All-country average" in names
print("Trend lines with 2 countries:", len(trend.data), "(expected 3):", names)

# Trend without countries still has the single full-period average line
plain = create_hdi_trend(df)
assert len(plain.data) == 1
print("Trend lines with no countries:", len(plain.data), "(expected 1)")

# Data check
row = df.loc[df["Life_Expectancy"].idxmin(), ["country", "year", "Life_Expectancy"]]
print("\nLowest life expectancy row:\n", row.to_string())
print("\nALL CHART TESTS PASSED")