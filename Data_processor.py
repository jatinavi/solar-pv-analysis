import pandas as pd
import os
from pathlib import Path


def diagnose_data_structure(data_path):
    """
    Diagnose the structure of your solar data
    """
    data_path = Path(data_path)

    print("=== SOLAR DATA DIAGNOSTIC ===\n")

    # Check GHI folder
    ghi_path = data_path / "GHI"
    pr_path = data_path / "PR"

    print("📁 FOLDER STRUCTURE:")
    print(f"GHI Path exists: {ghi_path.exists()}")
    print(f"PR Path exists: {pr_path.exists()}")

    total_files = 0
    sample_files_checked = 0

    for param_name, param_path in [("GHI", ghi_path), ("PR", pr_path)]:
        if param_path.exists():
            print(f"\n📊 {param_name} ANALYSIS:")

            # Count folders and files
            folders = list(param_path.glob("*"))
            folders = [f for f in folders if f.is_dir()]
            print(f"Number of month folders: {len(folders)}")

            folder_file_count = 0
            for folder in sorted(folders)[:3]:  # Check first 3 folders
                csv_files = list(folder.glob("*.csv"))
                folder_file_count += len(csv_files)
                print(f"  {folder.name}: {len(csv_files)} CSV files")

                # Sample first CSV file from first folder
                if csv_files and sample_files_checked < 2:
                    sample_file = csv_files[0]
                    print(f"\n🔍 SAMPLE FILE: {sample_file.name}")
                    try:
                        df = pd.read_csv(sample_file)
                        print(f"    Shape: {df.shape}")
                        print(f"    Columns: {list(df.columns)}")
                        print(f"    Data types: {dict(df.dtypes)}")
                        print(f"    First few values:")
                        print(f"    {df.head().to_string()}")
                        sample_files_checked += 1
                    except Exception as e:
                        print(f"    Error reading file: {e}")

            # Estimate total files
            if folders:
                avg_files_per_folder = folder_file_count / min(3, len(folders))
                estimated_total = avg_files_per_folder * len(folders)
                total_files += estimated_total
                print(f"Estimated total {param_name} files: {estimated_total:.0f}")

    print(f"\n📈 SUMMARY:")
    print(f"Estimated total CSV files: {total_files:.0f}")
    print(f"Expected rows in final dataset: {total_files:.0f}")

    # Check if each CSV contains multiple rows
    print("\n💡 RECOMMENDATIONS:")
    if total_files < 500:
        print("- Your CSV files might contain multiple rows of data per file")
        print("- Each row could represent different time measurements")
        print("- Consider processing all rows within each CSV file")
    else:
        print("- Data structure looks normal")
        print("- Each CSV file likely contains one measurement")


if __name__ == "__main__":
    data_path = "/Users/jatinbalchandani/Documents/projects/pythonProject3/Data"
    diagnose_data_structure(data_path)