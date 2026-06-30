import joblib
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import importlib.util
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score
)

# Import from 03_preprocess.py using importlib
spec = importlib.util.spec_from_file_location("preprocess", Path("03_preprocess.py"))
preprocess_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preprocess_module)
preprocessor = preprocess_module.preprocessor
X_test = preprocess_module.X_test
y_test = preprocess_module.y_test

OUT = Path("results/comparison")
OUT.mkdir(parents=True, exist_ok=True)

X_test_enc = preprocessor.transform(X_test)

# Load all models
models = {
    "LogReg (base)": joblib.load("results/logreg.joblib"),
    "RandomForest (base)": joblib.load("results/rf.joblib"),
    "XGBoost (base)": joblib.load("results/xgb.joblib"),

    "LogReg (tuned)": joblib.load("results/tuned_models/logreg_tuned.joblib"),
    "RandomForest (tuned)": joblib.load("results/tuned_models/random_forest_tuned.joblib"),
    "XGBoost (tuned)": joblib.load("results/tuned_models/xgb_tuned.joblib"),
}

rows = []
for name, model in models.items():
    y_pred = model.predict(X_test_enc)
    y_proba = model.predict_proba(X_test_enc)[:,1]

    rows.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1 Score": f1_score(y_test, y_pred),
        "ROC-AUC": roc_auc_score(y_test, y_proba)
    })

df = pd.DataFrame(rows)
df.to_csv(OUT/"model_comparison.csv", index=False)

# ----------- BAR CHART -----------
df_plot = df.set_index("Model")

plt.figure(figsize=(12,6))
df_plot[["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]].plot(
    kind="bar", figsize=(14,6), rot=45
)

plt.title("Model Comparison (Baseline vs Tuned Models)", fontsize=14)
plt.ylabel("Score")
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig(OUT/"model_comparison.png")
plt.close()

print("Model comparison saved in:", OUT)
