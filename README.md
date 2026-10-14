# Analysis and Visualisation of the Human Development Index (DV-HDI-INDEX)

An interactive Python dashboard for exploring global human development, built from United Nations Development Programme (UNDP) Human Development Report data for 195 countries from 1990 to 2023.

**Course context:** Data Visualization Lab (DV Lab), Week 8–9, Topic 5: Dashboard Creation.

---

## Abstract

The Human Development Index (HDI) Analysis Project presents a comprehensive examination of global human development trends using data obtained from the United Nations Development Programme (UNDP). The dataset incorporates HDI values along with its core components: life expectancy, educational attainment (mean and expected years of schooling), and Gross National Income (GNI) per capita. This enables a multidimensional assessment of development across countries. The primary objective of this project is to design and implement an interactive data visualization dashboard that gives users an intuitive platform to explore, compare, and interpret global HDI statistics.

The dashboard combines nine linked visualizations: a line chart for the long-run trend, bar charts for cross-country rankings, scatter plots for investigating the relationship between HDI and each of its indicators, a histogram for the distribution of HDI, and a correlation heatmap. Interactive year and country filters, hover details, and real-time updates support dynamic analysis.

By transforming a complex dataset into clear, accessible visuals, the project makes it easier to see global development disparities, progress over time, and the factors most closely associated with human well-being. Ultimately, it demonstrates how data visualization converts raw numerical information into actionable knowledge that can support evidence-based discussion of sustainable human development.

---

## Key features

- **Nine charts, all interactive or filter-aware** (see the table below).
- **Year filter:** choose any year from 1990 to 2023. It updates the summary figures, rankings, the four scatter plots, the distribution, and the heatmap.
- **Country comparison:** search and select any number of countries. The trend chart then shows one line per selected country against the dashed all-country average, and the scatter plots show only the selected countries with their names labelled.
- **Context-aware view:** while countries are selected, the Top 10, Bottom 10, and HDI Distribution charts are hidden, because they rank or describe all 195 countries and would be misleading for a subset. Press **Reset** to restore them.
- **Summary figures:** average, highest, and lowest HDI, plus the country count. They are calculated from the data and follow the selected scope.
- **Clear filter feedback:** Apply and Reset buttons, a status label showing the current view, and a hint when filters have been changed but not yet applied.
- **Accessible design:** colour-blind-safe palette, plain white chart areas, visible keyboard focus, alt text on the Seaborn images, and a responsive layout.

---

## Tech stack

| Layer | Technology | Used for |
|---|---|---|
| Language | Python 3.10 | All code |
| Data handling | Pandas | Loading, cleaning, reshaping, filtering, aggregation |
| Spreadsheet I/O | openpyxl | Reading the raw `.xlsx` and writing the cleaned `.xlsx` |
| Dashboard framework | Dash (Flask-based) | Layout, filters, and callbacks |
| Interactive charts | Plotly Express / Plotly Graph Objects | Charts 1–7 |
| Statistical charts | Seaborn + Matplotlib | Charts 8–9 |
| Styling | CSS (`dashboard/assets/style.css`) | Layout, filter bar, focus states, responsive design |
| Development | Visual Studio Code, PowerShell, pip | Editing, running, package management |
| Data source | UNDP Human Development Report | Raw dataset |

## Visualization tools and the nine charts

| # | Chart | Type | Library | Responds to |
|---|---|---|---|---|
| 1 | Average HDI Trend, 1990–2023 | Line | Plotly | Country filter (per-country lines); year shown as a marker |
| 2 | Top 10 Countries by HDI | Horizontal bar | Plotly | Year |
| 3 | Bottom 10 Countries by HDI | Horizontal bar | Plotly | Year |
| 4 | Life Expectancy vs HDI | Scatter | Plotly | Year, countries |
| 5 | GNI Per Capita vs HDI | Scatter | Plotly | Year, countries |
| 6 | Mean Years of Schooling vs HDI | Scatter | Plotly | Year, countries |
| 7 | Expected Years of Schooling vs HDI | Scatter | Plotly | Year, countries |
| 8 | HDI Distribution | Histogram with density curve | Seaborn + Matplotlib | Year |
| 9 | Correlation Heatmap | Heatmap | Seaborn + Matplotlib | Year |

Charts 1–7 are interactive in the browser (hover, zoom, pan). Charts 8 and 9 are drawn with Seaborn on a Matplotlib figure and shown in the dashboard as images that are regenerated whenever the filters change.

---

## Dataset

- **Source:** UNDP Human Development Report data (`data/raw/hdr-data (3).xlsx`).
- **Cleaned file:** `data/processed/HDI_cleaned.csv` (also saved as `.xlsx`).
- **Size:** 6,630 rows = 195 countries × 34 years (1990–2023), one row per country per year, with no duplicate country-year rows.

| Column | Meaning |
|---|---|
| `countryIsoCode`, `country` | Country identifiers |
| `year` | Observation year |
| `HDI` | Human Development Index (0 to 1) |
| `Life_Expectancy` | Life expectancy at birth (years) |
| `Mean_Years_Schooling` | Mean years of schooling |
| `Expected_Years_Schooling` | Expected years of schooling |
| `GNI_Per_Capita` | Gross national income per capita |
| `HDI_Rank` | Official rank (mostly empty; not used by the dashboard) |

### Preprocessing summary

`src/preprocessin.py` removes unused columns and exact duplicates, converts values to numbers, sets impossible values to missing (for example an HDI outside 0 to 1), pivots the long-format source into one row per country-year, renames the indicators, and fills gaps by linear interpolation within each country (any remaining gaps use the indicator's median).

### Data notes and limitations

- **Interpolated values:** because gaps were filled during preprocessing and the cleaned file does not flag which values were filled, every country appears in every year. The dashboard footer and the country-count card state this.
- **Rwanda, 1994:** the lowest life expectancy (12.158 years) is a genuine historical value and was deliberately left unchanged.
- **Descriptive only:** the scatter plots and correlations show association, not causation. HDI is itself calculated from life expectancy, schooling, and income, so strong correlations are expected.
- **No regional grouping:** the cleaned dataset contains countries only, so there are no regional or income-group views.

---

## Project structure

```text
DV-HDI-INDEX/
│
├── .vscode/
│   └── settings.json
│
├── data/
│   ├── raw/
│   │   └── hdr-data (3).xlsx          # original UNDP dataset
│   └── processed/
│       ├── HDI_cleaned.csv            # dataset used by the dashboard
│       └── HDI_cleaned.xlsx
│
├── src/
│   ├── __init__.py
│   ├── preprocessin.py                # data cleaning workflow
│   └── visualization.py               # the nine chart functions
│
├── dashboard/
│   ├── app.py                         # Dash layout and callbacks
│   └── assets/
│       └── style.css                  # dashboard styling
│
├── tests/
│   ├── __init__.py
│   └── test_charts.py                 # chart and filter checks
│
├── docs/                              # AI critique log (see Deliverables)
├── evidence/                          # before / after / testing screenshots
├── outputs/                           # PNGs saved by src/visualization.py
├── requirements.txt
└── README.md
```

---

## Getting started

### 1. Install dependencies

From the project root in PowerShell:

```powershell
pip install -r requirements.txt
```

### 2. Run the chart tests (optional)

```powershell
python -m tests.test_charts
```

You should see `ALL CHART TESTS PASSED`.

### 3. Launch the dashboard

```powershell
python dashboard\app.py
```

Open **http://127.0.0.1:8050** in your browser. Stop the server with `Ctrl+C`.

> Run the app from the terminal with the command above rather than the editor's Run button, so that project paths resolve correctly.

### Previewing the charts without the dashboard

```powershell
python src\visualization.py
```

This opens charts 1–7 in your browser and saves the two Seaborn charts to `outputs/`.

### Re-running preprocessing

`src/preprocessin.py` currently reads the raw file from a hard-coded path and saves its output in the folder it is run from. Update the input path, and move the output files into `data/processed/`, before re-running it.

---

## How to use the dashboard

1. Choose a **Year** and press **Apply** to update the rankings, scatter plots, distribution, heatmap, and summary figures.
2. Open **Countries to compare**, type to search, and add one or more countries. Press **Apply** to see their HDI trends against the all-country average.
3. Hover over any point or bar for exact values. Use the chart toolbar to zoom, pan, or download a chart.
4. Press **Reset** to return to the latest year with all countries.

---

## Deliverables and evidence (Week 8–9)

| Deliverable | Location | Status |
|---|---|---|
| Interactive dashboard with all nine charts and working filters | `dashboard/` | Done |
| "Before" screenshots of the initial dashboard | `evidence/before/` | To add |
| AI design critique against four criteria: data-ink ratio, colour accessibility, layout hierarchy, interactivity affordances | `docs/AI_critique_log.md` | To add |
| "After" screenshots of the improved dashboard | `evidence/after/` | To add |
| Functional testing evidence | `evidence/testing/` | To add |

Update the status column as each item is completed.

---

## AI assistance

This project was developed with assistance from an AI assistant (Claude by Anthropic) for refactoring the chart code into reusable functions, building the Dash application and its styling, and design critique. All suggestions were reviewed, tested locally, and accepted or rejected by the author. Accepted and rejected suggestions are recorded in `docs/AI_critique_log.md`.

---

## Data source and credits

- UNDP Human Development Report data: <https://hdr.undp.org/data-center>
- Built with [Dash](https://dash.plotly.com/), [Plotly](https://plotly.com/python/), [Seaborn](https://seaborn.pydata.org/), [Matplotlib](https://matplotlib.org/), and [Pandas](https://pandas.pydata.org/).

**Author:** [Your name] | **Course:** Data Visualization Lab
