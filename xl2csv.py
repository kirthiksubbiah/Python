import pandas as pd

df = pd.read_excel("file1.xlsx")

df.to_csv("output.csv", index=False)

print("Converted input.xlsx to output.csv")
