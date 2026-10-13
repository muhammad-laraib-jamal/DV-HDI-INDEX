import pandas as pd


# =========================================================
# 1. LOAD DATASET
# =========================================================

file_path = "C:/Users/larai/OneDrive/college/project/DV Lab/DV-HDI-INDEX/hdr-data (3).xlsx"

df = pd.read_excel(file_path)

print("Original Shape:", df.shape)


# =========================================================
# 2. REMOVE COMPLETELY EMPTY / UNNECESSARY COLUMNS
# =========================================================

columns_to_remove = [
    "dimension",
    "note",
    "indexCode",
    "index",
    "yearStr"
]

df = df.drop(columns=columns_to_remove, errors="ignore")


# =========================================================
# 3. REMOVE EXACT DUPLICATES
# =========================================================

before = len(df)

df = df.drop_duplicates()

after = len(df)

print("Duplicate rows removed:", before - after)


# =========================================================
# 4. CONVERT NUMERIC COLUMNS
# =========================================================

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["actualValue"] = pd.to_numeric(
    df["actualValue"],
    errors="coerce"
)


# =========================================================
# 5. CHECK MISSING VALUES
# =========================================================

print("\nMissing values before cleaning:")
print(df.isnull().sum())


# =========================================================
# 6. REMOVE INVALID VALUES
# =========================================================

# HDI must be between 0 and 1
df.loc[
    (df["indicatorCode"] == "hdi") &
    ((df["actualValue"] < 0) | (df["actualValue"] > 1)),
    "actualValue"
] = pd.NA


# HDI Rank must be positive
df.loc[
    (df["indicatorCode"] == "hdi_rank") &
    (df["actualValue"] <= 0),
    "actualValue"
] = pd.NA


# Life expectancy cannot be negative
df.loc[
    (df["indicatorCode"] == "le") &
    (df["actualValue"] < 0),
    "actualValue"
] = pd.NA


# Mean years of schooling cannot be negative
df.loc[
    (df["indicatorCode"] == "mys") &
    (df["actualValue"] < 0),
    "actualValue"
] = pd.NA


# Expected years of schooling cannot be negative
df.loc[
    (df["indicatorCode"] == "eys") &
    (df["actualValue"] < 0),
    "actualValue"
] = pd.NA


# GNI per capita cannot be negative
df.loc[
    (df["indicatorCode"] == "gnipc") &
    (df["actualValue"] < 0),
    "actualValue"
] = pd.NA


# =========================================================
# 7. CONVERT LONG FORMAT → WIDE FORMAT
# =========================================================

# One row = one country in one year
# Each indicator becomes a separate column

df = df.pivot_table(
    index=[
        "countryIsoCode",
        "country",
        "year"
    ],
    columns="indicatorCode",
    values="actualValue",
    aggfunc="first"
).reset_index()

df.columns.name = None


# =========================================================
# 8. RENAME INDICATORS
# =========================================================

df = df.rename(columns={
    "hdi": "HDI",
    "hdi_rank": "HDI_Rank",
    "le": "Life_Expectancy",
    "mys": "Mean_Years_Schooling",
    "eys": "Expected_Years_Schooling",
    "gnipc": "GNI_Per_Capita"
})


# =========================================================
# 9. SORT DATA
# =========================================================

df = df.sort_values(
    ["countryIsoCode", "year"]
).reset_index(drop=True)


# =========================================================
# 10. HANDLE MISSING VALUES
# =========================================================

indicator_columns = [
    "HDI",
    "Life_Expectancy",
    "Mean_Years_Schooling",
    "Expected_Years_Schooling",
    "GNI_Per_Capita"
]

# Interpolate only within the same country
# This preserves the actual units and meaning.

df[indicator_columns] = (
    df.groupby("countryIsoCode")[indicator_columns]
      .transform(
          lambda x: x.interpolate(
              method="linear",
              limit_direction="both"
          )
      )
)


# =========================================================
# 11. HANDLE ANY REMAINING MISSING VALUES
# =========================================================

# If some values are still missing after interpolation,
# use the median of that indicator.

for column in indicator_columns:

    if df[column].isna().any():

        df[column] = df[column].fillna(
            df[column].median()
        )


# =========================================================
# 12. FINAL DATA VALIDATION
# =========================================================

print("\nFinal Shape:", df.shape)

print("\nMissing values after cleaning:")
print(df.isnull().sum())

print("\nData types:")
print(df.dtypes)

print("\nFinal dataset preview:")
print(df.head())


# =========================================================
# 13. CHECK VALID RANGES
# =========================================================

print("\nHDI range:")
print(df["HDI"].min(), "to", df["HDI"].max())

print("\nLife Expectancy range:")
print(
    df["Life_Expectancy"].min(),
    "to",
    df["Life_Expectancy"].max()
)

print("\nExpected Years of Schooling range:")
print(
    df["Expected_Years_Schooling"].min(),
    "to",
    df["Expected_Years_Schooling"].max()
)

print("\nMean Years of Schooling range:")
print(
    df["Mean_Years_Schooling"].min(),
    "to",
    df["Mean_Years_Schooling"].max()
)

print("\nGNI Per Capita range:")
print(
    df["GNI_Per_Capita"].min(),
    "to",
    df["GNI_Per_Capita"].max()
)


# =========================================================
# 14. SAVE CLEANED DATASET
# =========================================================

df.to_csv(
    "HDI_cleaned.csv",
    index=False
)

df.to_excel(
    "HDI_cleaned.xlsx",
    index=False
)

print("\n======================================")
print("HDI DATA PREPROCESSING COMPLETED")
print("======================================")
print("Saved: HDI_cleaned.csv")
print("Saved: HDI_cleaned.xlsx")