import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

df = pd.read_csv("expense_dataset_balanced_ocr.csv")

# input(description) and output (category)
X = df["Description"]
y = df["Category"]

#train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# pipeline: TF-IDF + Logistic Regression
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2), stop_words='english')),
    ("clf", LogisticRegression(max_iter=1000, class_weight='balanced'))
])

# train
pipeline.fit(X_train, y_train)

#evaluate
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

joblib.dump(pipeline, "category_pipeline.pkl")
print("model saved as category_pipeline.pkl")
