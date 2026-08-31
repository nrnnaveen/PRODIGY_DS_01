
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set clean styling for plots
sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


def load_data():
    """
    Load population data and country metadata, merge them, and clean up non-country rows.
    """
    pop_path = os.path.join(os.path.dirname(__file__), "API_SP.POP.TOTL_DS2_en_csv_v2_38144.csv")
    meta_path = os.path.join(os.path.dirname(__file__), "Metadata_Country_API_SP.POP.TOTL_DS2_en_csv_v2_38144.csv")

    # The World Bank population CSV has 4 header metadata rows before the actual table
    pop_df = pd.read_csv(pop_path, skiprows=4)
    meta_df = pd.read_csv(meta_path)

    # Merge region and income group into the population dataframe
    merged = pd.merge(
        pop_df,
        meta_df[["Country Code", "Region", "IncomeGroup"]],
        on="Country Code",
        how="left",
    )

    # Filter out regional aggregates (like "World", "Arab World") by keeping only rows with a valid Region
    clean_df = merged[merged["Region"].notna()].copy()

    # Drop any rows missing 2024 population data
    clean_df = clean_df.dropna(subset=["2024"])

    return clean_df


def plot_population_histogram(df):
    """
    Plot the distribution of country populations in 2024 using a Histogram and KDE line.
    Includes both linear scale (in millions) and log scale for better readability.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Population in millions
    pop_millions = df["2024"] / 1e6

    # 1. Linear scale histogram
    sns.histplot(
        pop_millions,
        kde=True,
        bins=30,
        color="#2b5c8f",
        edgecolor="white",
        ax=ax1,
    )
    ax1.set_title("Country Population Distribution (2024) - Linear Scale", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Population (Millions)", fontsize=10)
    ax1.set_ylabel("Count of Countries", fontsize=10)

    # Add vertical lines for median and mean
    median_val = pop_millions.median()
    mean_val = pop_millions.mean()
    ax1.axvline(median_val, color="red", linestyle="--", linewidth=1.5, label=f"Median: {median_val:.1f}M")
    ax1.axvline(mean_val, color="orange", linestyle=":", linewidth=1.5, label=f"Mean: {mean_val:.1f}M")
    ax1.legend()

    # 2. Log scale histogram
    sns.histplot(
        df["2024"],
        kde=True,
        log_scale=True,
        bins=25,
        color="#2e7d32",
        edgecolor="white",
        ax=ax2,
    )
    ax2.set_title("Country Population Distribution (2024) - Log Scale", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Population (Log Scale)", fontsize=10)
    ax2.set_ylabel("Count of Countries", fontsize=10)

    plt.tight_layout()
    output_file = os.path.join(PLOTS_DIR, "fig1_population_histogram.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Saved: {output_file}")


def plot_region_barchart(df):
    """
    Plot a horizontal bar chart showing the count of countries in each region.
    """
    plt.figure(figsize=(10, 5))

    region_counts = df["Region"].value_counts().reset_index()
    region_counts.columns = ["Region", "Count"]

    ax = sns.barplot(
        data=region_counts,
        y="Region",
        x="Count",
        hue="Region",
        palette="viridis",
        legend=False,
    )

    # Add count labels on the bars
    for p in ax.patches:
        val = int(p.get_width())
        ax.annotate(
            str(val),
            (p.get_width() + 0.8, p.get_y() + p.get_height() / 2),
            va="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.title("Number of Countries by Region", fontsize=13, fontweight="bold")
    plt.xlabel("Number of Countries", fontsize=10)
    plt.ylabel("Region", fontsize=10)
    plt.xlim(0, region_counts["Count"].max() + 7)

    plt.tight_layout()
    output_file = os.path.join(PLOTS_DIR, "fig2_region_distribution_barchart.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Saved: {output_file}")


def plot_income_barchart(df):
    """
    Plot a bar chart showing the count of countries by income level.
    """
    plt.figure(figsize=(9, 5))

    order = ["Low income", "Lower middle income", "Upper middle income", "High income"]
    income_counts = df["IncomeGroup"].value_counts().reindex(order).dropna().reset_index()
    income_counts.columns = ["IncomeGroup", "Count"]

    ax = sns.barplot(
        data=income_counts,
        x="IncomeGroup",
        y="Count",
        hue="IncomeGroup",
        palette="Blues_r",
        legend=False,
    )

    # Add count labels on top of the bars
    for p in ax.patches:
        val = int(p.get_height())
        ax.annotate(
            str(val),
            (p.get_x() + p.get_width() / 2, p.get_height() + 1.2),
            ha="center",
            fontsize=10,
            fontweight="bold",
        )

    plt.title("Number of Countries by Income Group", fontsize=13, fontweight="bold")
    plt.xlabel("Income Group", fontsize=10)
    plt.ylabel("Number of Countries", fontsize=10)
    plt.ylim(0, income_counts["Count"].max() + 9)

    plt.tight_layout()
    output_file = os.path.join(PLOTS_DIR, "fig3_income_group_barchart.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Saved: {output_file}")


def plot_top_countries_barchart(df):
    """
    Plot a horizontal bar chart of the top 15 most populated countries in 2024.
    """
    plt.figure(figsize=(11, 6))

    top15 = df.nlargest(15, "2024").sort_values("2024", ascending=True)

    ax = sns.barplot(
        data=top15,
        y="Country Name",
        x="2024",
        hue="Country Name",
        palette="magma",
        legend=False,
    )

    # Format numbers into Millions or Billions on the bars
    for p in ax.patches:
        val = p.get_width()
        txt = f"{val/1e9:.2f} B" if val >= 1e9 else f"{val/1e6:.1f} M"
        ax.annotate(
            txt,
            (val + 1.5e7, p.get_y() + p.get_height() / 2),
            va="center",
            fontsize=9.5,
            fontweight="bold",
        )

    plt.title("Top 15 Most Populated Countries (2024)", fontsize=13, fontweight="bold")
    plt.xlabel("Population", fontsize=10)
    plt.ylabel("Country", fontsize=10)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M" if x < 1e9 else f"{x/1e9:.1f}B"))
    plt.xlim(0, top15["2024"].max() * 1.15)

    plt.tight_layout()
    output_file = os.path.join(PLOTS_DIR, "fig4_top15_countries_population.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Saved: {output_file}")


def plot_summary_dashboard(df):
    """
    Create a clean 2x2 dashboard combining all visual findings.
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle("World Population & Demographics Overview (Task 01)", fontsize=15, fontweight="bold", y=0.98)

    # 1. Histogram (Log Scale)
    sns.histplot(df["2024"], kde=True, log_scale=True, bins=25, color="#1f77b4", edgecolor="white", ax=axes[0, 0])
    axes[0, 0].set_title("A. Population Distribution (Log Scale)", fontsize=11, fontweight="bold")
    axes[0, 0].set_xlabel("Population", fontsize=9)
    axes[0, 0].set_ylabel("Count of Countries", fontsize=9)

    # 2. Countries per Region
    reg = df["Region"].value_counts().reset_index()
    reg.columns = ["Region", "Count"]
    sns.barplot(data=reg, y="Region", x="Count", hue="Region", palette="viridis", legend=False, ax=axes[0, 1])
    axes[0, 1].set_title("B. Countries by Region", fontsize=11, fontweight="bold")
    axes[0, 1].set_xlabel("Number of Countries", fontsize=9)
    axes[0, 1].set_ylabel("")
    for p in axes[0, 1].patches:
        w = int(p.get_width())
        axes[0, 1].annotate(str(w), (w + 0.8, p.get_y() + p.get_height() / 2), va="center", fontsize=9, fontweight="bold")
    axes[0, 1].set_xlim(0, reg["Count"].max() + 7)

    # 3. Countries by Income Group
    order = ["Low income", "Lower middle income", "Upper middle income", "High income"]
    inc = df["IncomeGroup"].value_counts().reindex(order).dropna().reset_index()
    inc.columns = ["IncomeGroup", "Count"]
    sns.barplot(data=inc, x="IncomeGroup", y="Count", hue="IncomeGroup", palette="Blues_r", legend=False, ax=axes[1, 0])
    axes[1, 0].set_title("C. Countries by Income Group", fontsize=11, fontweight="bold")
    axes[1, 0].set_xlabel("Income Level", fontsize=9)
    axes[1, 0].set_ylabel("Number of Countries", fontsize=9)
    for p in axes[1, 0].patches:
        h = int(p.get_height())
        axes[1, 0].annotate(str(h), (p.get_x() + p.get_width() / 2, h + 1.2), ha="center", fontsize=9, fontweight="bold")
    axes[1, 0].set_ylim(0, inc["Count"].max() + 9)

    # 4. Top 10 Countries
    top10 = df.nlargest(10, "2024").sort_values("2024", ascending=True)
    sns.barplot(data=top10, y="Country Name", x="2024", hue="Country Name", palette="magma", legend=False, ax=axes[1, 1])
    axes[1, 1].set_title("D. Top 10 Most Populated Countries (2024)", fontsize=11, fontweight="bold")
    axes[1, 1].set_xlabel("Population", fontsize=9)
    axes[1, 1].set_ylabel("")
    axes[1, 1].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M" if x < 1e9 else f"{x/1e9:.1f}B"))
    for p in axes[1, 1].patches:
        w = p.get_width()
        txt = f"{w/1e9:.2f}B" if w >= 1e9 else f"{w/1e6:.1f}M"
        axes[1, 1].annotate(txt, (w + 1.5e7, p.get_y() + p.get_height() / 2), va="center", fontsize=8.5, fontweight="bold")
    axes[1, 1].set_xlim(0, top10["2024"].max() * 1.15)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    output_file = os.path.join(PLOTS_DIR, "fig5_summary_dashboard.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Saved: {output_file}")


def main():
    print("Loading and preparing data...")
    df = load_data()
    print(f"Ready. Working with {len(df)} countries.\n")

    print("Key Summary Statistics (2024):")
    print(f"- Total World Population: {df['2024'].sum():,.0f}")
    print(f"- Average Population: {df['2024'].mean():,.0f}")
    print(f"- Median Population: {df['2024'].median():,.0f}")
    print(f"- Most Populated: {df.loc[df['2024'].idxmax()]['Country Name']} ({df['2024'].max():,.0f})")
    print(f"- Least Populated: {df.loc[df['2024'].idxmin()]['Country Name']} ({df['2024'].min():,.0f})\n")

    print("Generating charts...")
    plot_population_histogram(df)
    plot_region_barchart(df)
    plot_income_barchart(df)
    plot_top_countries_barchart(df)
    plot_summary_dashboard(df)
    print("\nDone! All charts are saved in the 'plots/' folder.")


if __name__ == "__main__":
    main()
