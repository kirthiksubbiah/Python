import pandas as pd

df1 = pd.read_excel("file1.xlsx")
df2 = pd.read_excel("file2.xlsx")

merged = pd.concat([df1, df2], ignore_index=True)
merged.to_excel("merged.xlsx", index=False)

print("Merged file saved as merged.xlsx")
