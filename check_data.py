import pandas as pd

file_path = "data/agriculture_risk_dataset.csv"

df = pd.read_csv(file_path)

print("\nDATASET LOADED SUCCESSFULLY")
print("-" * 40)

print("Shape:", df.shape)

print("\nColumn names:")
for column in df.columns:
    print("-", column)

print("\nFirst five rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum().sort_values(ascending=False).head(10))

print("\nRisk category distribution:")
if "risk_category" in df.columns:
    print(df["risk_category"].value_counts())