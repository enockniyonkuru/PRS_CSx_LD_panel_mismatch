import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textwrap import dedent

sns.set(context="talk", style="whitegrid")

MODEL_DEFS = {
    "M1": "PRS-CSx (matched LD anchor)",
    "M2": "PRS-CS (single-ancestry; mismatch risk)",
    "M3": "PRS-CSx (single mismatch with LD anchor)",
    "M4": "PRS-CSx (AMR fallback)",
    "M5": "PRS-CSx (SAS fallback)",
}

PALETTE = {
    "EUR": "#1f77b4",  # blue
    "EAS": "#9467bd",  # purple
}


def parse_args():
    p = argparse.ArgumentParser(description="Generate Figure 4: Population-Stratified PRS-CSx performance")
    p.add_argument("--input", required=True, help="Path to input CSV with columns: population, model, r2, r2_low, r2_high")
    p.add_argument("--output", required=True, help="Path to write the output PNG figure")
    p.add_argument("--width", type=float, default=12.0, help="Figure width in inches")
    p.add_argument("--height", type=float, default=8.0, help="Figure height in inches")
    return p.parse_args()


def validate_df(df: pd.DataFrame):
    required = {"population", "model", "r2", "r2_low", "r2_high"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input CSV missing required columns: {sorted(missing)}")
    # Basic sanity: models present
    if not set(["M1","M2","M3","M4","M5"]).issubset(set(df["model"].unique())):
        pass  # allow partial but warn
    # Force categorical ordering
    df["model"] = pd.Categorical(df["model"], categories=["M1","M2","M3","M4","M5"], ordered=True)
    df["population"] = pd.Categorical(df["population"], categories=["EUR","EAS"], ordered=True)
    return df


def panel_bar_with_ci(ax, df_pop: pd.DataFrame, title: str, color: str):
    # Bars
    sns.barplot(ax=ax, data=df_pop, x="model", y="r2", color=color)
    # Error bars (95% CI)
    for i, row in enumerate(df_pop.sort_values("model").itertuples(index=False)):
        ax.errorbar(i, row.r2, yerr=[[row.r2 - row.r2_low], [row.r2_high - row.r2]], fmt="none", ecolor="black", capsize=3, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel("Model")
    ax.set_ylabel("R²")
    ax.set_ylim(0, max(0.35, df_pop["r2_high"].max() + 0.05))


def panel_comparison(ax, df: pd.DataFrame):
    # Comparison panel: juxtapose EUR vs EAS per model
    pivot = df.pivot_table(index="model", columns="population", values="r2")
    # Plot grouped bars
    pivot = pivot.loc[["M1","M2","M3","M4","M5"]]
    x = range(len(pivot))
    w = 0.4
    ax.bar([xi - w/2 for xi in x], pivot["EUR"], width=w, color=PALETTE["EUR"], label="EUR")
    ax.bar([xi + w/2 for xi in x], pivot["EAS"], width=w, color=PALETTE["EAS"], label="EAS")
    ax.set_xticks(list(x))
    ax.set_xticklabels(list(pivot.index))
    ax.set_ylabel("R²")
    ax.set_title("C. EUR vs EAS comparison (R²)")
    ax.legend(frameon=True)
    ax.set_ylim(0, max(0.35, df["r2_high"].max() + 0.05))


def panel_model_defs(ax):
    txt = "\n".join([f"{m}: {MODEL_DEFS[m]}" for m in ["M1","M2","M3","M4","M5"]])
    ax.text(0.01, 0.99, dedent(f"""
    D. Model definitions
    {txt}
    """), va="top", ha="left")
    ax.axis("off")


def main():
    args = parse_args()
    df = pd.read_csv(args.input)
    df = validate_df(df)

    fig, axes = plt.subplots(2, 2, figsize=(args.width, args.height))
    axA, axB, axC, axD = axes[0,0], axes[0,1], axes[1,0], axes[1,1]

    # Panel A: EUR
    df_eur = df[df["population"] == "EUR"].copy()
    panel_bar_with_ci(axA, df_eur, "A. EUR performance (R² with 95% CI)", PALETTE["EUR"]) 

    # Panel B: EAS
    df_eas = df[df["population"] == "EAS"].copy()
    panel_bar_with_ci(axB, df_eas, "B. EAS performance (R² with 95% CI)", PALETTE["EAS"]) 

    # Panel C: Comparison
    panel_comparison(axC, df)

    # Panel D: Model definitions
    panel_model_defs(axD)

    plt.tight_layout()
    fig.savefig(args.output, dpi=300)
    print(f"Saved figure to {args.output}")


if __name__ == "__main__":
    main()
