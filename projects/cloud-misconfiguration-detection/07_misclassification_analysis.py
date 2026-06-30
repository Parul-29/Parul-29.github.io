import joblib
import pandas as pd
from pathlib import Path
import importlib.util
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Import from 03_preprocess.py using importlib
spec = importlib.util.spec_from_file_location("preprocess", Path("03_preprocess.py"))
preprocess_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preprocess_module)
preprocessor = preprocess_module.preprocessor
X_test = preprocess_module.X_test
y_test = preprocess_module.y_test
df = preprocess_module.df

OUT = Path("results/misclassification")
OUT.mkdir(parents=True, exist_ok=True)

# ----------- LOAD MODELS -----------
models = {
    "LogReg (base)": joblib.load("results/logreg.joblib"),
    "RandomForest (base)": joblib.load("results/rf.joblib"),
    "XGBoost (base)": joblib.load("results/xgb.joblib"),

    "LogReg (tuned)": joblib.load("results/tuned_models/logreg_tuned.joblib"),
    "RandomForest (tuned)": joblib.load("results/tuned_models/random_forest_tuned.joblib"),
    "XGBoost (tuned)": joblib.load("results/tuned_models/xgb_tuned.joblib"),
}

X_test_enc = preprocessor.transform(X_test)

# Use titles & provider data for insights
meta = df.loc[X_test.index, ["title", "cloud_provider", "category"]]

# Store results for each model
for name, model in models.items():
    y_pred = model.predict(X_test_enc)
    y_proba = model.predict_proba(X_test_enc)[:, 1]

    misclassified = (y_pred != y_test).astype(int)

    result = pd.DataFrame({
        "True Label": y_test.values,
        "Predicted Label": y_pred,
        "Predicted Probability": y_proba,
        "Misclassified": misclassified,
        "Title": meta["title"].values,
        "Provider": meta["cloud_provider"].values,
        "Category": meta["category"].values,
    })

    result.to_csv(OUT / f"{name}_misclassifications.csv", index=False)

    # Print key failure counts
    fn = result[(result["True Label"] == 1) & (result["Predicted Label"] == 0)]
    fp = result[(result["True Label"] == 0) & (result["Predicted Label"] == 1)]

    print(f"\n===== {name} =====")
    print("False Positives:", len(fp))
    print("False Negatives:", len(fn), " <-- most important in security")

print("\nMisclassification analysis saved!")
