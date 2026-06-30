"""
Centralized preprocessing module for all downstream scripts
Can be run standalone for validation OR imported by other scripts
"""
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split

# Load data
DATA = Path("processed_vulns.csv")
df = pd.read_csv(DATA)

# Define features (NO 'misconfiguration' to prevent leakage!)
features = [
    'severity', 'public_exposure', 'privilege_escalation', 'data_exposure', 
    'dos', 'unencrypted', 'iam', 's3_bucket', 'ssrf_rce'
]
features = [f for f in features if f in df.columns]
cat_cols = ['cloud_provider', 'category']

# Split data
X = df[features + cat_cols]
y = df['is_misconfiguration']

# Create preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
    ]
)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Fit preprocessor on training data
preprocessor.fit(X_train)

# This runs when imported OR when run directly
print(" Preprocessing module loaded")
print(f"  Features: {len(features)} numeric + {len(cat_cols)} categorical")
print(f"  Train size: {len(X_train)}, Test size: {len(X_test)}")

# Additional validation info when run as standalone script
if __name__ == "__main__":
    print("\n" + "="*60)
    print("PREPROCESSING VALIDATION")
    print("="*60)
    
    print("\n Dataset Info:")
    print(f"   Total samples: {len(df)}")
    print(f"   Features: {features}")
    print(f"   Categorical columns: {cat_cols}")
    
    print(f"\n Target Distribution:")
    print(f"   Class 0 (Non-Misconfiguration): {(y==0).sum()} ({(y==0).mean()*100:.1f}%)")
    print(f"   Class 1 (Misconfiguration): {(y==1).sum()} ({(y==1).mean()*100:.1f}%)")
    
    print(f"\n Train/Test Split:")
    print(f"   Train: {len(X_train)} samples")
    print(f"   Test:  {len(X_test)} samples")
    print(f"   Split ratio: {len(X_test)/(len(X_train)+len(X_test))*100:.0f}% test")
    
    print(f"\n Preprocessor Info:")
    print(f"   Numeric features: {len(features)}")
    print(f"   Categorical features: {len(cat_cols)}")
    
    # Show categorical encoding details
    ohe = preprocessor.named_transformers_["cat"]
    X_train_enc = preprocessor.transform(X_train)
    print(f"   Total encoded features: {X_train_enc.shape[1]}")
    
    print("\n Preprocessing validation complete!")