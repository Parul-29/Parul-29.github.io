import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import importlib.util

# Import from 03_preprocess.py using importlib
spec = importlib.util.spec_from_file_location("preprocess", Path("03_preprocess.py"))
preprocess_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preprocess_module)
preprocessor = preprocess_module.preprocessor
X_train = preprocess_module.X_train
df = preprocess_module.df

import shap

OUT = Path("results/feature_importance")
OUT.mkdir(parents=True, exist_ok=True)

# Define features (same as in 03_preprocess.py)
features = [
    'severity', 'public_exposure', 'privilege_escalation', 'data_exposure', 
    'dos', 'unencrypted', 'iam', 's3_bucket', 'ssrf_rce'
]
features = [f for f in features if f in df.columns]
cat_cols = ['cloud_provider', 'category']

# ---------------------------------------
# 1. Prepare Encoded Feature Names
# ---------------------------------------

# Get transformed column names from ColumnTransformer
ohe = preprocessor.named_transformers_["cat"]
cat_feature_names = ohe.get_feature_names_out(cat_cols)
all_feature_names = list(features) + list(cat_feature_names)

# ---------------------------------------
# Load Tuned Models
# ---------------------------------------

rf = joblib.load("results/tuned_models/random_forest_tuned.joblib")
xgb = joblib.load("results/tuned_models/xgb_tuned.joblib")

X_train_enc = preprocessor.transform(X_train)

print("\nGenerating Feature Importance Dashboard...")

# 2. Random Forest Feature Importance
# ---------------------------------------

rf_imp = pd.DataFrame({
    "Feature": all_feature_names,
    "Importance": rf.feature_importances_
}).sort_values("Importance", ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(y="Feature", x="Importance", data=rf_imp.head(15), palette="viridis")
plt.title("Random Forest - Top 15 Feature Importances")
plt.tight_layout()
plt.savefig(OUT / "rf_feature_importance.png")
plt.close()

# 3. XGBoost Feature Importance
# ---------------------------------------

xgb_imp = pd.DataFrame({
    "Feature": all_feature_names,
    "Importance": xgb.feature_importances_
}).sort_values("Importance", ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(y="Feature", x="Importance", data=xgb_imp.head(15), palette="magma")
plt.title("XGBoost - Top 15 Feature Importances")
plt.tight_layout()
plt.savefig(OUT / "xgb_feature_importance.png")
plt.close()

# 4. SHAP Summary Plot (Top 20 Features)
# ---------------------------------------

explainer = shap.TreeExplainer(xgb)

# Sample 400 rows for faster SHAP computation
sample_idx = np.random.choice(X_train_enc.shape[0], min(400, X_train_enc.shape[0]), replace=False)
X_sample = X_train_enc[sample_idx]

shap_values = explainer.shap_values(X_sample)

plt.figure(figsize=(10,6))
shap.summary_plot(shap_values, X_sample, feature_names=all_feature_names, max_display=20, show=False)
plt.title("SHAP Summary Plot (XGBoost) - Top 20 Features")
plt.tight_layout()
plt.savefig(OUT / "shap_feature_importance.png")
plt.close()

print("\n Feature Importance Dashboard saved in:", OUT)
