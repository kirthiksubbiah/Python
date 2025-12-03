import pandas as pd

students = pd.read_excel("students.xlsx")
marks = pd.read_excel("marks.xlsx")

merged = pd.merge(students, marks, on="id", how="inner")
merged.to_excel("students_with_marks.xlsx", index=False)

print("Saved as students_with_marks.xlsx")
