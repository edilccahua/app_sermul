import pandas as pd
import glob
import os

print("--- EXCEL FILES ---")
for file in glob.glob("memory/excel ejemplos/*.xlsx"):
    print(f"\n--- FILE: {os.path.basename(file)} ---")
    try:
        xl = pd.ExcelFile(file)
        print("Sheets:", xl.sheet_names)
        for sheet in xl.sheet_names:
            print(f"\nSheet: {sheet}")
            df = xl.parse(sheet, nrows=20)
            print(df.to_string())
    except Exception as e:
        print("Error reading file:", e)
