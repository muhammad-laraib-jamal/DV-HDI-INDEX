"""
HDI chart functions.

Charts 1-7 : Plotly Express (interactive)
Charts 8-9 : Seaborn + Matplotlib (rendered as images)

Importing this module does not display anything.
Run it directly (python src/visualization.py) to preview all charts.
"""

import base64
import io
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from matplotlib.figure import Figure


# =========================================================
# 1. DATA LOADING
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

file_path = BASE_DIR / "data" / "processed" / "HDI_cleaned.csv"

CORRELATION_COLUMNS = [
    "HDI",
    "Life_Expectancy",
    "Mean_Years_Schooling",
    "Expected_Years_Schooling",
    "GNI_Per_Capita",
]


def load_data() -> pd.DataFrame:
    """Read the cleaned HDI dataset."""
    return pd.read_csv(file_path)


def get_latest_year(df: pd.DataFrame) -> int:
    return int(df["year"].max())


# =========================================================
# 2. HELPERS
# =========================================================

def _year_slice(df: pd.DataFrame, year: int) -> pd.DataFrame:
    return df[df["year"] == year].copy()


def _empty_plotly_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font={"size": 14},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _apply_white_layout(fig)


def _apply_white_layout(fig: go.Figure) -> go.Figure:
    """Plain white plot area with dark, readable text."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"color": "#1f2933"},
        margin={"l": 60, "r": 20, "t": 60, "b": 50},
    )
    return fig


def figure_to_base64(fig: Figure, dpi: int = 150) -> str:
    """Convert a Matplotlib figure to a PNG data URI for Dash html.Img."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight",
                facecolor="white")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def _empty_matplotlib_figure(message: str) -> Figure:
    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    ax.set_axis_off()
    return fig


# =========================================================
# 3. CHART 1 - AVERAGE HDI TREND (PLOTLY, FULL 1990-2023)
# =========================================================

def create_hdi_trend(df: pd.DataFrame) -> go.Figure:
    yearly_hdi = df.groupby("year", as_index=False)["HDI"].mean()

    fig = px.line(
        yearly_hdi,
        x="year",
        y="HDI",
        markers=True,
        title="Average HDI Trend (1990–2023)",
        labels={"year": "Year", "HDI": "Average HDI"},
    )

    fig.update_traces(
        hovertemplate="Year: %{x}<br>Average HDI: %{y:.3f}<extra></extra>"
    )

    return _apply_white_layout(fig)


# =========================================================
# 4. CHARTS 2-3 - TOP / BOTTOM 10 (PLOTLY)
# =========================================================
# Always ranked across ALL countries for the selected year.

def create_top10_chart(df: pd.DataFrame, year: int) -> go.Figure:
    data = _year_slice(df, year)

    if data.empty:
        return _empty_plotly_figure(f"No data available for {year}")

    top10 = data.nlargest(10, "HDI").sort_values("HDI")

    fig = px.bar(
        top10,
        x="HDI",
        y="country",
        orientation="h",
        title=f"Top 10 Countries by HDI ({year})",
        labels={"HDI": "Human Development Index", "country": "Country"},
        hover_name="country",
    )

    fig.update_traces(
        hovertemplate="Country: %{y}<br>HDI: %{x:.3f}<extra></extra>"
    )

    return _apply_white_layout(fig)


def create_bottom10_chart(df: pd.DataFrame, year: int) -> go.Figure:
    data = _year_slice(df, year)

    if data.empty:
        return _empty_plotly_figure(f"No data available for {year}")

    bottom10 = data.nsmallest(10, "HDI").sort_values("HDI")

    fig = px.bar(
        bottom10,
        x="HDI",
        y="country",
        orientation="h",
        title=f"Bottom 10 Countries by HDI ({year})",
        labels={"HDI": "Human Development Index", "country": "Country"},
        hover_name="country",
    )

    fig.update_traces(
        hovertemplate="Country: %{y}<br>HDI: %{x:.3f}<extra></extra>"
    )

    return _apply_white_layout(fig)


# =========================================================
# 5. CHARTS 4-7 - INDICATOR VS HDI SCATTER PLOTS (PLOTLY)
# =========================================================

def _create_indicator_scatter(
    df: pd.DataFrame,
    year: int,
    x_column: str,
    x_label: str,
    title: str,
    x_hover_format: str,
    unit_suffix: str = "",
    countries=None,
) -> go.Figure:
    data = _year_slice(df, year)

    if countries:
        data = data[data["country"].isin(countries)]

    if data.empty:
        return _empty_plotly_figure("No data for the selected filters")

    fig = px.scatter(
        data,
        x=x_column,
        y="HDI",
        hover_name="country",
        title=f"{title} ({year})",
        labels={x_column: x_label, "HDI": "Human Development Index"},
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            f"{x_label}: %{{x:{x_hover_format}}}{unit_suffix}<br>"
            "HDI: %{y:.3f}"
            "<extra></extra>"
        )
    )

    return _apply_white_layout(fig)


def create_life_expectancy_scatter(df, year, countries=None):
    return _create_indicator_scatter(
        df, year,
        x_column="Life_Expectancy",
        x_label="Life Expectancy (years)",
        title="Life Expectancy vs HDI",
        x_hover_format=".2f",
        unit_suffix=" years",
        countries=countries,
    )


def create_gni_scatter(df, year, countries=None):
    return _create_indicator_scatter(
        df, year,
        x_column="GNI_Per_Capita",
        x_label="GNI Per Capita",
        title="GNI Per Capita vs HDI",
        x_hover_format=",.2f",
        countries=countries,
    )


def create_mean_schooling_scatter(df, year, countries=None):
    return _create_indicator_scatter(
        df, year,
        x_column="Mean_Years_Schooling",
        x_label="Mean Years of Schooling",
        title="Mean Years of Schooling vs HDI",
        x_hover_format=".2f",
        countries=countries,
    )


def create_expected_schooling_scatter(df, year, countries=None):
    return _create_indicator_scatter(
        df, year,
        x_column="Expected_Years_Schooling",
        x_label="Expected Years of Schooling",
        title="Expected Years of Schooling vs HDI",
        x_hover_format=".2f",
        countries=countries,
    )


# =========================================================
# 6. CHART 8 - HDI DISTRIBUTION (SEABORN + MATPLOTLIB)
# =========================================================

def create_hdi_distribution(df: pd.DataFrame, year: int) -> Figure:
    data = _year_slice(df, year)

    if data.empty:
        return _empty_matplotlib_figure(f"No data available for {year}")

    fig = Figure(figsize=(10, 6))
    ax = fig.subplots()

    sns.histplot(data["HDI"], bins=15, kde=True, ax=ax)

    ax.set_title(f"HDI Distribution ({year})")
    ax.set_xlabel("Human Development Index")
    ax.set_ylabel("Number of Countries")

    fig.tight_layout()
    return fig


# =========================================================
# 7. CHART 9 - CORRELATION HEATMAP (SEABORN + MATPLOTLIB)
# =========================================================

def get_correlation_matrix(df: pd.DataFrame, year: int) -> pd.DataFrame:
    data = _year_slice(df, year)
    return data[CORRELATION_COLUMNS].corr()


def create_correlation_heatmap(df: pd.DataFrame, year: int) -> Figure:
    data = _year_slice(df, year)

    if len(data) < 3:
        return _empty_matplotlib_figure(
            f"Not enough data for correlation in {year}"
        )

    correlation = data[CORRELATION_COLUMNS].corr()

    fig = Figure(figsize=(10, 7))
    ax = fig.subplots()

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        linewidths=0.5,
        ax=ax,
    )

    ax.set_title(f"Correlation Between HDI Indicators ({year})")

    fig.tight_layout()
    return fig


# =========================================================
# 8. STANDALONE PREVIEW
# =========================================================

if __name__ == "__main__":
    df = load_data()
    latest_year = get_latest_year(df)

    print("Dataset Path:", file_path)
    print("Dataset Shape:", df.shape)
    print(df.head())
    print("\nLatest Year:", latest_year)
    print("Number of Countries:", df[df["year"] == latest_year]["country"].nunique())

    create_hdi_trend(df).show()
    create_top10_chart(df, latest_year).show()
    create_bottom10_chart(df, latest_year).show()
    create_life_expectancy_scatter(df, latest_year).show()
    create_gni_scatter(df, latest_year).show()
    create_mean_schooling_scatter(df, latest_year).show()
    create_expected_schooling_scatter(df, latest_year).show()

    output_dir = BASE_DIR / "outputs"
    output_dir.mkdir(exist_ok=True)

    create_hdi_distribution(df, latest_year).savefig(
        output_dir / "hdi_distribution.png", dpi=150, bbox_inches="tight"
    )
    create_correlation_heatmap(df, latest_year).savefig(
        output_dir / "correlation_heatmap.png", dpi=150, bbox_inches="tight"
    )

    print("\nCorrelation Matrix:")
    print(get_correlation_matrix(df, latest_year))

    print("\n======================================")
    print("All visualizations completed!")
    print(f"Seaborn charts saved in: {output_dir}")
    print("======================================")