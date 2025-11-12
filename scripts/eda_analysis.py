import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore

# Set folder paths
base_dir = "Raw&Processed-Data"
data_dir = os.path.join(base_dir, "data")
raw_data_dir = os.path.join(base_dir, "data", "raw")
#raw_data_dir = os.path.join(data_dir, "raw")
processed_data_dir = os.path.join(data_dir, "processed")
analysis_dir = os.path.join(base_dir, "analysis")
plots_dir = os.path.join(analysis_dir, "plots")
summary_dir = os.path.join(analysis_dir, "summary")
results_dir = os.path.join(base_dir, "results")

# Create directories if they don't exist
for folder in [data_dir, raw_data_dir, processed_data_dir, analysis_dir, plots_dir, summary_dir, results_dir]:
    os.makedirs(folder, exist_ok=True)

# Load datasets
files = ["benin-malanville.csv", "sierraleone-bumbuna.csv", "togo-dapaong_qc.csv"]
datasets = {}
for file in files:
    file_path = os.path.join(raw_data_dir, file)
    datasets[file.split(".")[0]] = pd.read_csv(file_path)

# Function to save plots

def save_plot(fig, filename):
    fig.savefig(os.path.join(plots_dir, filename), bbox_inches='tight')
    plt.close(fig)

# Function for summary statistics
def generate_summary_statistics(df, filename):
    summary = df.describe().T
    summary["missing"] = df.isnull().sum()
    summary.to_csv(os.path.join(summary_dir, filename))
    return summary

# Perform EDA on each dataset
for name, df in datasets.items():
    print(f"Processing dataset: {name}")

    # Summary statistics
    summary = generate_summary_statistics(df, f"summary_{name}.csv")
    print(summary)

    # Data quality check
    print("Checking for missing values...")
    missing_values = df.isnull().sum()
    print(missing_values)

    print("Checking for outliers...")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    z_scores = np.abs(zscore(df[numeric_cols].dropna()))
    outliers = (z_scores > 3).sum(axis=0)
    print(outliers)

    # Time Series Analysis
    time_cols = ["GHI", "DNI", "DHI", "Tamb"]
    time_cols = [col for col in time_cols if col in df.columns]
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        df[time_cols].plot(ax=ax, title=f"Time Series Analysis: {name}")
        save_plot(fig, f"time_series_{name}.png")

    # Correlation Analysis
    if not df[numeric_cols].empty:
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        ax.set_title(f"Correlation Matrix: {name}")
        save_plot(fig, f"correlation_matrix_{name}.png")

    # Wind Analysis
    if "WS" in df.columns and "WD" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 8))
        sns.histplot(df["WS"], kde=True, ax=ax)
        ax.set_title(f"Wind Speed Distribution: {name}")
        save_plot(fig, f"wind_speed_distribution_{name}.png")

    # Histograms
    fig, axes = plt.subplots(len(numeric_cols) // 3 + 1, 3, figsize=(15, 10))
    axes = axes.flatten()
    for i, col in enumerate(numeric_cols):
        sns.histplot(df[col], kde=True, ax=axes[i])
        axes[i].set_title(f"Histogram: {col}")
    save_plot(fig, f"histograms_{name}.png")

    # Bubble Chart
    bubble_vars = ["GHI", "Tamb", "WS", "RH"]
    bubble_vars = [col for col in bubble_vars if col in df.columns]
    if len(bubble_vars) >= 3:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            x=bubble_vars[0],
            y=bubble_vars[1],
            size=bubble_vars[2],
            hue=bubble_vars[2],
            sizes=(40, 400),
            data=df,
            ax=ax
        )
        ax.set_title(f"Bubble Chart: {name}")
        save_plot(fig, f"bubble_chart_{name}.png")

    # Data Cleaning
    if "Comments" in df.columns:
        df.drop(columns=["Comments"], inplace=True)
    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)
    df.to_csv(os.path.join(processed_data_dir, f"cleaned_{name}.csv"), index=False)

    print(f"Finished processing dataset: {name}\n")
