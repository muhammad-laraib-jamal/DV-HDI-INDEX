import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


# =========================================================
# 1. LOAD DATA
# =========================================================

df = pd.read_csv("HDI_cleaned.csv")

print("Dataset Shape:", df.shape)
print(df.head())


# =========================================================
# 2. GET LATEST YEAR
# =========================================================

latest_year = df["year"].max()

latest = df[df["year"] == latest_year].copy()

print("\nLatest Year:", latest_year)
print("Number of Countries:", latest["country"].nunique())


# =========================================================
# 3. AVERAGE HDI TREND - PLOTLY
# =========================================================

yearly_hdi = (
    df.groupby("year", as_index=False)["HDI"]
    .mean()
)

fig = px.line(
    yearly_hdi,
    x="year",
    y="HDI",
    markers=True,
    title="Average HDI Trend (1990–2023)",
    labels={
        "year": "Year",
        "HDI": "Average HDI"
    }
)

fig.update_traces(
    hovertemplate="Year: %{x}<br>Average HDI: %{y:.3f}<extra></extra>"
)

fig.show()


# =========================================================
# 4. TOP 10 COUNTRIES BY HDI - PLOTLY
# =========================================================

top10 = (
    latest
    .nlargest(10, "HDI")
    .sort_values("HDI")
)

fig = px.bar(
    top10,
    x="HDI",
    y="country",
    orientation="h",
    title=f"Top 10 Countries by HDI ({latest_year})",
    labels={
        "HDI": "Human Development Index",
        "country": "Country"
    },
    hover_name="country"
)

fig.update_traces(
    hovertemplate=
    "Country: %{y}<br>"
    "HDI: %{x:.3f}<extra></extra>"
)

fig.show()


# =========================================================
# 5. BOTTOM 10 COUNTRIES BY HDI - PLOTLY
# =========================================================

bottom10 = (
    latest
    .nsmallest(10, "HDI")
    .sort_values("HDI")
)

fig = px.bar(
    bottom10,
    x="HDI",
    y="country",
    orientation="h",
    title=f"Bottom 10 Countries by HDI ({latest_year})",
    labels={
        "HDI": "Human Development Index",
        "country": "Country"
    },
    hover_name="country"
)

fig.update_traces(
    hovertemplate=
    "Country: %{y}<br>"
    "HDI: %{x:.3f}<extra></extra>"
)

fig.show()


# =========================================================
# 6. LIFE EXPECTANCY VS HDI - PLOTLY
# =========================================================

fig = px.scatter(
    latest,
    x="Life_Expectancy",
    y="HDI",
    hover_name="country",
    title=f"Life Expectancy vs HDI ({latest_year})",
    labels={
        "Life_Expectancy": "Life Expectancy (years)",
        "HDI": "Human Development Index"
    }
)

fig.update_traces(
    hovertemplate=
    "<b>%{hovertext}</b><br>"
    "Life Expectancy: %{x:.2f} years<br>"
    "HDI: %{y:.3f}"
    "<extra></extra>"
)

fig.show()


# =========================================================
# 7. GNI PER CAPITA VS HDI - PLOTLY
# =========================================================

fig = px.scatter(
    latest,
    x="GNI_Per_Capita",
    y="HDI",
    hover_name="country",
    title=f"GNI Per Capita vs HDI ({latest_year})",
    labels={
        "GNI_Per_Capita": "GNI Per Capita",
        "HDI": "Human Development Index"
    }
)

fig.update_traces(
    hovertemplate=
    "<b>%{hovertext}</b><br>"
    "GNI Per Capita: %{x:,.2f}<br>"
    "HDI: %{y:.3f}"
    "<extra></extra>"
)

fig.show()


# =========================================================
# 8. MEAN YEARS OF SCHOOLING VS HDI - PLOTLY
# =========================================================

fig = px.scatter(
    latest,
    x="Mean_Years_Schooling",
    y="HDI",
    hover_name="country",
    title=f"Mean Years of Schooling vs HDI ({latest_year})",
    labels={
        "Mean_Years_Schooling": "Mean Years of Schooling",
        "HDI": "Human Development Index"
    }
)

fig.update_traces(
    hovertemplate=
    "<b>%{hovertext}</b><br>"
    "Mean Years of Schooling: %{x:.2f}<br>"
    "HDI: %{y:.3f}"
    "<extra></extra>"
)

fig.show()


# =========================================================
# 9. EXPECTED YEARS OF SCHOOLING VS HDI - PLOTLY
# =========================================================

fig = px.scatter(
    latest,
    x="Expected_Years_Schooling",
    y="HDI",
    hover_name="country",
    title=f"Expected Years of Schooling vs HDI ({latest_year})",
    labels={
        "Expected_Years_Schooling": "Expected Years of Schooling",
        "HDI": "Human Development Index"
    }
)

fig.update_traces(
    hovertemplate=
    "<b>%{hovertext}</b><br>"
    "Expected Years of Schooling: %{x:.2f}<br>"
    "HDI: %{y:.3f}"
    "<extra></extra>"
)

fig.show()


# =========================================================
# 10. HDI DISTRIBUTION - SEABORN
# =========================================================

plt.figure(figsize=(10, 6))

sns.histplot(
    latest["HDI"],
    bins=15,
    kde=True
)

plt.title(f"HDI Distribution ({latest_year})")
plt.xlabel("Human Development Index")
plt.ylabel("Number of Countries")

plt.tight_layout()
plt.show()


# =========================================================
# 11. CORRELATION HEATMAP - SEABORN
# =========================================================

corr_columns = [
    "HDI",
    "Life_Expectancy",
    "Mean_Years_Schooling",
    "Expected_Years_Schooling",
    "GNI_Per_Capita"
]

correlation = latest[corr_columns].corr()

plt.figure(figsize=(10, 7))

sns.heatmap(
    correlation,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    linewidths=0.5
)

plt.title(
    f"Correlation Between HDI Indicators ({latest_year})"
)

plt.tight_layout()
plt.show()


# =========================================================
# 12. PRINT CORRELATION VALUES
# =========================================================

print("\nCorrelation Matrix:")
print(correlation)

print("\n======================================")
print("All visualizations completed!")
print("======================================")