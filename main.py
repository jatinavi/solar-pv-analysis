import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import glob
from pathlib import Path


def process_folder(folder_path, param_name):
    data = []

    for month_folder in sorted(folder_path.glob("*")):
        if month_folder.is_dir():
            print(f"Processing {param_name} folder: {month_folder.name}")
            csv_files = sorted(month_folder.glob("*.csv"))
            print(f"Found {len(csv_files)} CSV files in {month_folder.name}")

            for csv_file in csv_files:
                try:
                    filename = csv_file.stem

                    if filename.endswith(f'_{param_name}'):
                        date_str = filename.replace(f'_{param_name}', '')
                    else:
                        date_str = filename

                    try:
                        date = pd.to_datetime(date_str, format='%Y-%m-%d')
                    except:
                        try:
                            if not date_str.startswith(month_folder.name[:7]):
                                date_str = f"{month_folder.name}-{date_str.split('-')[-1]}"
                            date = pd.to_datetime(date_str, format='%Y-%m-%d')
                        except:
                            print(f"Could not parse date from {filename}, skipping...")
                            continue

                    df = pd.read_csv(csv_file)

                    if len(df.columns) > 0:
                        for idx, row in df.iterrows():
                            numeric_cols = df.select_dtypes(include=[np.number]).columns
                            if len(numeric_cols) > 0:
                                value = row[numeric_cols[0]]
                            else:
                                try:
                                    value = pd.to_numeric(row.iloc[0], errors='coerce')
                                except:
                                    value = np.nan

                            if not pd.isna(value):
                                if idx == 0:
                                    row_date = date
                                else:
                                    row_date = date + timedelta(hours=idx)

                                data.append({
                                    'Date': row_date,
                                    param_name: value
                                })

                    print(f"Processed {csv_file.name}: extracted {len(df)} values")

                except Exception as e:
                    print(f"Error processing {csv_file}: {e}")
                    continue

    print(f"Total {param_name} data points collected: {len(data)}")
    return pd.DataFrame(data)


def load_data(data_path):
    print("Starting data preprocessing...")

    data_path = Path(data_path)

    ghi_path = data_path / "GHI"
    ghi_data = process_folder(ghi_path, "GHI")

    pr_path = data_path / "PR"
    pr_data = process_folder(pr_path, "PR")

    combined = pd.merge(ghi_data, pr_data, on='Date', how='outer')
    combined = combined.sort_values('Date').reset_index(drop=True)
    combined = combined.ffill().bfill()

    print(f"Data preprocessing completed. Total rows: {len(combined)}")
    return combined


def get_budget_line(start_date, end_date):
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    budget_values = []

    initial_value = 73.9
    yearly_reduction = 0.008
    first_year_start = datetime(2019, 7, 1)

    for date in dates:
        years_elapsed = (date - first_year_start).days / 365.25
        budget_value = initial_value * ((1 - yearly_reduction) ** years_elapsed)
        budget_values.append(budget_value)

    return dates, budget_values


def get_ghi_color(ghi_value):
    if ghi_value < 2:
        return 'navy'
    elif 2 <= ghi_value < 4:
        return 'lightblue'
    elif 4 <= ghi_value < 6:
        return 'orange'
    else:
        return 'brown'


def create_plot(data, output_file="pr_analysis_graph.png"):
    data['PR_30d_MA'] = data['PR'].rolling(window=30, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(15, 10))

    budget_dates, budget_values = get_budget_line(data['Date'].min(), data['Date'].max())

    ax.plot(budget_dates, budget_values, 'green', linewidth=2,
            label='Budget Line', linestyle='-', alpha=0.8)

    ax.plot(data['Date'], data['PR_30d_MA'], 'red', linewidth=2,
            label='30-day Moving Average')

    colors = [get_ghi_color(ghi) for ghi in data['GHI']]
    ax.scatter(data['Date'], data['PR'], c=colors, alpha=0.6, s=20)

    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Performance Ratio (PR)', fontsize=12)
    ax.set_title('Solar PV Performance Analysis\nPerformance Ratio vs Time with GHI Color Coding',
                 fontsize=14, fontweight='bold')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    ax.grid(True, alpha=0.3)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='navy', label='GHI < 2'),
        Patch(facecolor='lightblue', label='GHI 2-4'),
        Patch(facecolor='orange', label='GHI 4-6'),
        Patch(facecolor='brown', label='GHI > 6'),
        plt.Line2D([0], [0], color='red', linewidth=2, label='30-day Moving Average'),
        plt.Line2D([0], [0], color='green', linewidth=2, label='Budget Line')
    ]

    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98))

    last_7_days = data.tail(7)['PR'].mean() if len(data) >= 7 else data['PR'].mean()
    last_30_days = data.tail(30)['PR'].mean() if len(data) >= 30 else data['PR'].mean()
    last_60_days = data.tail(60)['PR'].mean() if len(data) >= 60 else data['PR'].mean()
    last_90_days = data.tail(90)['PR'].mean() if len(data) >= 90 else data['PR'].mean()

    stats_text = f"""Average PR:
Last 7 days: {last_7_days:.2f}%
Last 30 days: {last_30_days:.2f}%
Last 60 days: {last_60_days:.2f}%
Last 90 days: {last_90_days:.2f}%"""

    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8),
            verticalalignment='bottom', horizontalalignment='right', fontsize=10)

    budget_df = pd.DataFrame({'Date': budget_dates, 'Budget': budget_values})
    merged_budget = pd.merge_asof(data.sort_values('Date'), budget_df.sort_values('Date'),
                                  on='Date', direction='nearest')
    points_above_budget = (merged_budget['PR'] > merged_budget['Budget']).sum()

    ax.text(0.02, 0.02, f'Points above Target Budget PR: {points_above_budget}',
            transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8),
            verticalalignment='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.show()

    print(f"Visualization saved to {output_file}")


# Main execution
data_path = "/Users/jatinbalchandani/Documents/projects/pythonProject3/Data"

data = load_data(data_path)
data.to_csv("processed_solar_data.csv", index=False)
print("Processed data saved to processed_solar_data.csv")

create_plot(data, "pr_analysis_graph.png")