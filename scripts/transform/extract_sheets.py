import pandas as pd
import argparse
import os

# ---------------------------
# 원본 파일 경로 (고정)
# ---------------------------
RAW_FILE = "/Users/hayoung/Documents/Portfolio/Tableau/Game_Dashboard_Project/data/raw/GameData_Raw.xlsx"

def extract_sheets(output_file, sheets_to_keep):
    """Extract selected sheets from raw Excel and save to output path."""
    dfs = pd.read_excel(RAW_FILE, sheet_name=sheets_to_keep)
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

# ---------------------------
# 명령줄 인자 처리
# ---------------------------
parser = argparse.ArgumentParser(
    description="Extract selected sheets from raw GameData_Raw.xlsx and save to processed folder.\n\n"
                "Usage examples:\n"
                "  python extract_sheets.py --output Game1_PlayerBehavior.xlsx --sheets Players Sessions Events\n"
                "  python extract_sheets.py --output Game2_RevenueMonetization.xlsx --sheets Players Items Payments Sessions Events\n"
                "  python extract_sheets.py --output Game3_EventPerformance.xlsx --sheets Players Sessions Events Payments Campaigns Campaign_Events Items",
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument("--output", required=True, help="Output Excel file name (saved in processed folder)")
parser.add_argument("--sheets", required=True, nargs="+", help="Sheets to extract (space separated)")

args = parser.parse_args()

# ---------------------------
# 출력 경로를 processed 폴더로 설정
# ---------------------------
output_path = os.path.join(
    "/Users/hayoung/Documents/Portfolio/Tableau/Game_Dashboard_Project/data/processed",
    args.output
)

extract_sheets(output_path, args.sheets)