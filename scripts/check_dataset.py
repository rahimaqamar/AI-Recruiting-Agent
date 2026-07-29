import pandas as pd

df = pd.read_csv("data/dataset/Resume.csv")

print(df.columns.tolist())
print(df.head())