# Machine Learning Framework for Cloud Misconfiguration Detection

Technical Overview  
Parul Inamdar

## Project Overview

This project presents a machine learning framework for automated cloud misconfiguration detection across AWS, Azure, and GCP. Instead of relying only on static rule-based tools, the framework learns from historical vulnerability records and predicts whether a cloud configuration represents a misconfiguration.

The system uses supervised classification, security-focused feature engineering, class balancing, and model interpretability to support CI/CD-friendly cloud security review.

## Research Objective

Cloud misconfigurations are a leading cause of security incidents, including exposed storage, overly permissive IAM policies, missing encryption, and weak logging controls. Traditional tools such as AWS Config, Azure Policy, and CSPM products are useful, but they depend heavily on predefined rules.

This project explores whether machine learning can complement rule-based detection by learning patterns from cloud vulnerability data.

## Dataset

The framework uses 1,200 cloud vulnerability records spanning AWS, Azure, and GCP.

Each record includes:

- Vulnerability description
- Vulnerability category
- Cloud provider
- Vulnerable code snippet
- Proof-of-concept or exploitation details
- Source reference
- Timestamp

Class distribution:

| Class | Count | Share |
| --- | ---: | ---: |
| Misconfiguration | 908 | 75.7% |
| Non-misconfiguration | 292 | 24.3% |

The dataset had a 3.1:1 class imbalance, so SMOTE was applied to the training data.

## Feature Engineering

The pipeline extracts security-relevant features from vulnerability records while explicitly avoiding target leakage.

Engineered binary features:

- `public_exposure`
- `privilege_escalation`
- `data_exposure`
- `dos`
- `unencrypted`
- `iam`
- `s3_bucket`
- `ssrf_rce`

Numerical feature:

- `severity`, a weighted risk score from 0 to 100

Categorical features:

- `cloud_provider`
- `category`

The final encoded feature space contains 37 dimensions after standardization and one-hot encoding.

## Pipeline Design

```text
Raw JSONL vulnerability records
        |
        v
Feature engineering
Security keywords, severity score, provider/category features
        |
        v
Preprocessing
Deduplication, standardization, one-hot encoding, stratified split
        |
        v
Class balancing
SMOTE applied to the training set
        |
        v
Model training
Logistic Regression, Random Forest, XGBoost
        |
        v
Evaluation and interpretability
Accuracy, precision, recall, F1, ROC-AUC, false negatives, SHAP
```

The full orchestration pipeline executes the analysis steps in dependency order, generating trained models, performance metrics, visualizations, and interpretability outputs.

## Models Evaluated

| Model | Purpose |
| --- | --- |
| Logistic Regression | Interpretable linear baseline |
| Random Forest | Ensemble model optimized for lower false negatives |
| XGBoost | Gradient boosting model optimized for strong ranking performance |

Hyperparameter tuning used randomized search with stratified cross-validation, but the results showed that feature engineering had more impact than tuning.

## Key Results

Baseline model performance:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Logistic Regression | 84.0% | 0.86 | 0.84 | 0.85 | 0.9069 |
| Random Forest | 90.0% | 0.90 | 0.90 | 0.90 | 0.9138 |
| XGBoost | 89.0% | 0.89 | 0.89 | 0.89 | 0.9344 |

Security-critical false negative analysis:

| Model | False Positives | False Negatives | False Negative Rate |
| --- | ---: | ---: | ---: |
| Random Forest baseline | 14 | 9 | 4.9% |
| XGBoost baseline | 12 | 15 | 8.2% |
| Tuned Random Forest | 12 | 16 | 8.8% |
| Tuned XGBoost | 13 | 18 | 9.9% |
| Tuned Logistic Regression | 8 | 27 | 14.8% |
| Logistic Regression baseline | 10 | 28 | 15.4% |

XGBoost achieved the highest ROC-AUC, while baseline Random Forest had the lowest false negative rate and was the strongest candidate for production security use.

## Interpretability

SHAP analysis showed that the model learned security-relevant patterns instead of relying on arbitrary artifacts.

Top influential features:

| Feature | SHAP Importance |
| --- | ---: |
| Severity | 28.3% |
| Public exposure | 19.7% |
| Unencrypted | 15.2% |
| Privilege escalation | 12.8% |
| IAM | 8.4% |
| Data exposure | 7.1% |

The strongest predictors aligned with cloud security best practices: public exposure, encryption status, severity, privilege escalation, and IAM risk.

## Technical Challenges and Solutions

### Target Leakage Prevention

Misconfiguration-specific label hints were excluded from the feature set so the model learned from security characteristics instead of direct target words.

### Class Imbalance

The dataset was dominated by misconfiguration examples. SMOTE balanced the training set and improved sensitivity to the minority class.

### Security-Oriented Evaluation

The project emphasized false negatives because missed misconfigurations are more dangerous than false alarms in cloud security operations.

### CI/CD Suitability

All models trained in under 3 seconds, and the full pipeline completed in about 34 seconds, making the approach practical for automated security workflows.

## Outcomes

- Built an automated nine-stage machine learning pipeline for cloud misconfiguration detection.
- Achieved 0.9344 ROC-AUC with baseline XGBoost.
- Identified baseline Random Forest as production-suitable with only 9 missed misconfigurations and a 4.9% false negative rate.
- Demonstrated that feature engineering and class balancing had greater impact than hyperparameter tuning.
- Used SHAP explanations to validate that model decisions aligned with security best practices.

## Technology Stack

| Category | Tools and Technologies |
| --- | --- |
| Languages and Data | Python, pandas, JSONL, CSV |
| Machine Learning | scikit-learn, XGBoost, imbalanced-learn, SMOTE |
| Models | Logistic Regression, Random Forest, XGBoost |
| Evaluation | ROC-AUC, F1, precision, recall, confusion matrices |
| Interpretability | SHAP, feature importance |
| Security Domain | Cloud misconfiguration detection, IAM, S3, encryption, public exposure |
