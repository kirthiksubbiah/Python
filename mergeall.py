import pandas as pd
import glob

excel_files = glob.glob("*.xlsx")

dfs = []

for file in excel_files:
    print("Reading:", file)
    df = pd.read_excel(file)
    df["source_file"] = file  
    dfs.append(df)

merged = pd.concat(dfs, ignore_index=True)
merged.to_excel("all_merged.xlsx", index=False)

print("Merged all .xlsx to all_merged.xlsx")
