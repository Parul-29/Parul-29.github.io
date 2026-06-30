import joblib
import numpy as np
from pathlib import Path
import importlib.util
import sys

from imblearn.over_sampling import SMOTE
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

# Import from 03_preprocess.py using importlib
spec = importlib.util.spec_from_file_location("preprocess", Path("03_preprocess.py"))
preprocess_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preprocess_module)
preprocessor = preprocess_module.preprocessor
X_train = preprocess_module.X_train
X_test = preprocess_module.X_test
y_train = preprocess_module.y_train
y_test = preprocess_module.y_test

OUT = Path("results/tuned_models")
OUT.mkdir(exist_ok=True, parents=True)

# Encode train/test
X_train_enc = preprocessor.transform(X_train)
X_test_enc = preprocessor.transform(X_test)

# Handle imbalance
sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X_train_enc, y_train)

print("\n Starting Hyperparameter Tuning...\n")

# ------------------ RANDOM FOREST ------------------ #
print("Tuning Random Forest...")
rf = RandomForestClassifier(random_state=42)

rf_grid = {
    'n_estimators': [150, 200, 300, 400],
    'max_depth': [8, 12, 15, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf_search = RandomizedSearchCV(
    rf, rf_grid, n_iter=10, cv=3, scoring="f1",
    n_jobs=-1, random_state=42, verbose=1
)

rf_search.fit(X_res, y_res)
best_rf = rf_search.best_estimator_
joblib.dump(best_rf, OUT/"random_forest_tuned.joblib")

print("\nBest RandomForest Params:", rf_search.best_params_)
print(f"Best CV F1 Score: {rf_search.best_score_:.4f}")


# ------------------ LOGISTIC REGRESSION ------------------ #
print("\nTuning Logistic Regression...")
log = LogisticRegression(max_iter=2000, random_state=42)

log_grid = {
    'C': np.logspace(-3, 3, 10),
    'penalty': ['l2']
}

log_search = RandomizedSearchCV(
    log, log_grid, n_iter=8, cv=3, scoring="f1",
    n_jobs=-1, random_state=42, verbose=1
)

log_search.fit(X_res, y_res)
best_log = log_search.best_estimator_
joblib.dump(best_log, OUT/"logreg_tuned.joblib")

print("\nBest Logistic Regression Params:", log_search.best_params_)
print(f"Best CV F1 Score: {log_search.best_score_:.4f}")


# ------------------ XGBOOST ------------------ #
print("\nTuning XGBoost...")
xgb = XGBClassifier(
    eval_metric="logloss",
    random_state=42,
    tree_method="hist"
)

xgb_grid = {
    'n_estimators': [200, 300, 400, 500],
    'max_depth': [3, 4, 5, 7],
    'learning_rate': [0.01, 0.05, 0.1],
    'subsample': [0.7, 0.8, 1.0],
    'colsample_bytree': [0.7, 0.8, 1.0]
}

xgb_search = RandomizedSearchCV(
    xgb, xgb_grid, n_iter=12, cv=3, scoring="f1",
    n_jobs=-1, random_state=42, verbose=1
)

xgb_search.fit(X_res, y_res)
best_xgb = xgb_search.best_estimator_
joblib.dump(best_xgb, OUT/"xgb_tuned.joblib")

print("\nBest XGB Params:", xgb_search.best_params_)
print(f"Best CV F1 Score: {xgb_search.best_score_:.4f}")


# ------------------ EVALUATE TUNED MODELS ------------------ #
print("\n" + "="*60)
print("EVALUATING TUNED MODELS ON TEST SET")
print("="*60)

models = {
    "RandomForest": best_rf,
    "LogisticRegression": best_log,
    "XGBoost": best_xgb
}

for name, model in models.items():
    y_pred = model.predict(X_test_enc)
    y_proba = model.predict_proba(X_test_enc)[:,1]

    print(f"\n===== {name} Tuned Model Performance =====")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")

print(f"\n Tuned models saved to: {OUT}")