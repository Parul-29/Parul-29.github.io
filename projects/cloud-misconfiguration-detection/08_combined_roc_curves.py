import joblib
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import importlib.util
from sklearn.metrics import roc_curve, roc_auc_score

# Import from 03_preprocess.py using importlib
spec = importlib.util.spec_from_file_location("preprocess", Path("03_preprocess.py"))
preprocess_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preprocess_module)
preprocessor = preprocess_module.preprocessor
X_test = preprocess_module.X_test
y_test = preprocess_module.y_test

OUT = Path("results/roc")
OUT.mkdir(parents=True, exist_ok=True)

models = {
    "LogReg (base)": joblib.load("results/logreg.joblib"),
    "RandomForest (base)": joblib.load("results/rf.joblib"),
    "XGBoost (base)": joblib.load("results/xgb.joblib"),

    "LogReg (tuned)": joblib.load("results/tuned_models/logreg_tuned.joblib"),
    "RandomForest (tuned)": joblib.load("results/tuned_models/random_forest_tuned.joblib"),
    "XGBoost (tuned)": joblib.load("results/tuned_models/xgb_tuned.joblib"),
}

X_test_enc = preprocessor.transform(X_test)

plt.figure(figsize=(10, 7))

for name, model in models.items():
    y_proba = model.predict_proba(X_test_enc)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)

    plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})", linewidth=2)

plt.plot([0,1], [0,1], "k--", label="Random Classifier")

plt.title("Combined ROC Curves (Baseline vs Tuned Models)", fontsize=14)
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT / "combined_roc_curves.png")
plt.close()

print("Combined ROC Curves saved!")
