import pandas as pd
from generate_dataset import generate_dataset

df = pd.read_csv("expense_dataset.csv")

#coounting samples per category
counts = df['Category'].value_counts()
print("before balancing:\n", counts)

#finding max count
max_count = counts.max()

#generating new rows for smaller categories
balanced_rows = []

for category, count in counts.items():
    if count < max_count:
        # Number of synthetic rows needed
        rows_needed = max_count - count
        print(f"Generating {rows_needed} rows for category '{category}'")
        synthetic_df = generate_dataset(rows_needed, force_cat=category)
        balanced_rows.append(synthetic_df)

#combining original and synthetic data
if balanced_rows:
    df_balanced = pd.concat([df] + balanced_rows, ignore_index=True)
else:
    df_balanced = df.copy()

#shuffling dataset
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

df_balanced.to_csv("expense_dataset_balanced.csv", index=False)
print("After balancing:\n", df_balanced['Category'].value_counts())