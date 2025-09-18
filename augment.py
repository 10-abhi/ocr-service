import random
import pandas as pd

balanced_df = pd.read_csv("expense_dataset_balanced.csv")

def augment_ocr_style(text):
    # random spaces around commas
    text = text.replace(",", random.choice([",", ", ", ",  "]))
    #random remove/keep currency symbol
    text = text.replace("₹", random.choice(["", "₹"]))
    #random capitalization
    text = "".join(c.upper() if random.random() < 0.1 else c for c in text)
    # typos
    if random.random() < 0.05:
        text = text.replace("i", "l").replace("o", "0").replace("a", "@")
    return text

#augmented(noisy) version data 
augmented_df = balanced_df.copy()
augmented_df['Description'] = augmented_df['Description'].apply(augment_ocr_style)

# combine original + augmented
final_df = pd.concat([balanced_df, augmented_df], ignore_index=True)

final_df.to_csv("expense_dataset_balanced_ocr.csv", index=False)
print("Final dataset size:", len(final_df))
