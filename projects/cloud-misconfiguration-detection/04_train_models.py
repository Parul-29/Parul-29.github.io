import joblib
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, cross_val_score

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
DATA = Path("processed_vulns.csv")
df = pd.read_csv(DATA)

# CRITICAL FIX: Remove 'misconfiguration' from features to prevent leakage
features = [
    'severity','public_exposure','privilege_escalation','data_exposure','dos',
    'unencrypted','iam','s3_bucket','ssrf_rce'  # NO 'misconfiguration'!
]
features = [f for f in features if f in df.columns]
cat_cols = ['cloud_provider','category']

X = df[features + cat_cols]
y = df['is_misconfiguration']

print(f"Dataset size: {len(df)}")
print(f"Features used: {features}")
print(f"Target distribution:\n{y.value_counts()}\n")

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
    ]
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

OUT = Path("results")
OUT.mkdir(exist_ok=True)

X_train_enc = preprocessor.fit_transform(X_train)
X_test_enc = preprocessor.transform(X_test)

# Apply SMOTE to handle class imbalance
sm = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X_train_enc, y_train)

print(f"After SMOTE - Training set size: {X_res.shape[0]}")
print(f"Class distribution: {pd.Series(y_res).value_counts()}\n")

models = {
    "logreg": LogisticRegression(max_iter=1000, random_state=42),
    "rf": RandomForestClassifier(n_estimators=200, random_state=42),
    "xgb": XGBClassifier(eval_metric='logloss', random_state=42)
}

for name, model in models.items():
    print(f"{'='*60}")
    print(f"Training: {name}")
    print(f"{'='*60}")
    
    # Train model
    model.fit(X_res, y_res)
    joblib.dump(model, OUT/f"{name}.joblib")

    # Make predictions
    y_pred = model.predict(X_test_enc)
    y_proba = model.predict_proba(X_test_enc)[:,1]

    # Evaluate
    print("\nTest Set Performance:")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.4f}")
    
    # Cross-validation on training data (before SMOTE)
    cv_scores = cross_val_score(model, X_train_enc, y_train, cv=5, scoring='roc_auc')
    print(f"\nCross-Validation ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"Confusion Matrix - {name}")
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(OUT/f"{name}_cm.png")
    plt.close()
    
    print()

print(f"\nModels saved to: {OUT}")