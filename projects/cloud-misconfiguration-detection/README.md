# Cloud Vulnerability Classification System

## 📋 Project Overview

This machine learning pipeline classifies cloud security vulnerabilities as misconfigurations or other vulnerability types using multiple classification algorithms (Logistic Regression, Random Forest, XGBoost).

**Author:** Parul Inamdar 
**Course:** CSS 581 A Machine Learning 
**Date:** 8 December 2025

---

## 🖥️ Technical Specifications

### System Requirements
- **Operating System:** Windows 10/11, macOS 10.15+, or Linux
- **Python Version:** 3.12.1
- **RAM:** Minimum 4GB (8GB recommended)
- **Disk Space:** ~500MB for dependencies and outputs

### Required Libraries
All dependencies are listed in `requirements.txt`:
```
pandas>=2.3.3
numpy>=2.3.3
scikit-learn>=1.7.2
xgboost>=3.1.2
imbalanced-learn>=0.14.0
matplotlib>=3.10.7
seaborn>=0.13.2
joblib>=1.5.2
shap>=0.50.0
```
---

## 📦 Installation Instructions

### Step 1: Extract the Submission Package
```bash
# Unzip the submission file
unzip cloud_vulnerability_classification.zip
cd cloud_vulnerability_classification
```

### Step 2: Set Up Python Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Screenshot:** Place screenshot here showing successful installation
```
![SCREENSHOT 1: Terminal showing pip install completing successfully](<Screenshots/Screenshot 1.png>)
```

---

## 📊 Dataset Information

### Required File
- **Filename:** `CLOUD_VULRABILITES_DATASET.jsonl`
- **Format:** JSON Lines 
- **Size:** 488 KB

### Dataset Location
**Dataset is included in this submission package:**
```
The dataset is included in this submission package as:
./CLOUD_VULRABILITES_DATASET.jsonl
Total Size: 1,200 cloud vulnerability records
```

### Dataset Schema
Each line contains a JSON object with fields:
- `id`: Unique vulnerability identifier (e.g., "VUL001")
- `description`: Detailed description of the vulnerability
- `category`: Vulnerability category (e.g., "Misconfiguration", "Exposure")
- `cloud_provider`: Cloud platform (AWS, Azure, GCP)
- `vulnerable_code`: Code snippet showing the vulnerability
- `poc`: Proof of concept / exploitation steps
- `source`: Object containing:
  - `cve`: CVE ID or "N/A" if not applicable
  - `link`: Reference link to vulnerability source
- `timestamp`: ISO 8601 timestamp of discovery/report date

---

## 🚀 How to Run the Complete Pipeline

### Quick Start (Automated Pipeline)
```bash
python 11_main_pipeline.py
```

This single command runs all 9 scripts in the correct order and generates all outputs.

```
![SCREENSHOT 2: Terminal showing pipeline running with progress indicators](<Screenshots/Screenshot 2.png>)
```

### Expected Console Output
Pre-flight checks...
 OK CLOUD_VULRABILITES_DATASET.jsonl
 OK 03_preprocess.py

 All checks passed. Starting pipeline...


======================================================================
CLOUD VULNERABILITY CLASSIFICATION - COMPLETE PIPELINE
======================================================================

Started at: 2025-12-07 16:52:41


======================================================================
STEP 1: Data Transformation & Feature Engineering
======================================================================
Saved: processed_vulns.csv
Total rows: 1200
Misconfiguration rate: 75.67%

SUCCESS Completed in 0.51 seconds

======================================================================
STEP 2: Exploratory Data Analysis & Visualizations
======================================================================
SUCCESS Completed in 2.52 seconds

[... continues for all 9 steps ...]

SUCCESS Completed in 3.85 seconds

======================================================================
PIPELINE COMPLETED SUCCESSFULLY!
======================================================================

Total execution time: 55.8 seconds (0.9 minutes)
Started:  16:52:41
Finished: 16:53:37

Generated Outputs:
   figures/                    - EDA visualizations
   results/                    - Baseline model files
   results/tuned_models/       - Optimized models
   results/comparison/         - Model comparison charts
   results/misclassification/  - Error analysis CSVs
   results/roc/                - ROC curves
   results/feature_importance/ - Feature analysis
   results/clustered_vulns.csv - Clustering results

Next Steps:
   1. Review visualizations in figures/
   2. Check model comparison in results/comparison/
   3. Analyze misclassifications in results/misclassification/
   4. Use best model from results/tuned_models/
```
```
![SCREENSHOT 3: Terminal showing "PIPELINE COMPLETED SUCCESSFULLY"](<Screenshots/Screenshot 3.png>)
```

---

## 📂 Generated Outputs

After running the pipeline, the following directory structure is created:

```
project_root/
├── processed_vulns.csv              # Processed dataset with features
├── figures/                         # EDA visualizations
│   ├── class_distribution.png
│   ├── provider_vulnerability.png
│   └── correlation.png
├── results/
│   ├── logreg.joblib               # Baseline Logistic Regression
│   ├── rf.joblib                   # Baseline Random Forest
│   ├── xgb.joblib                  # Baseline XGBoost
│   ├── *_cm.png                    # Confusion matrices
│   ├── tuned_models/               # Optimized models
│   │   ├── logreg_tuned.joblib
│   │   ├── random_forest_tuned.joblib
│   │   └── xgb_tuned.joblib
│   ├── comparison/
│   │   ├── model_comparison.csv
│   │   └── model_comparison.png
│   ├── misclassification/
│   │   └── [6 CSV files with error analysis]
│   ├── roc/
│   │   └── combined_roc_curves.png
│   └── feature_importance/
│       ├── rf_feature_importance.png
│       ├── xgb_feature_importance.png
│       └── shap_feature_importance.png
```

---

## 📸 Results Demonstration

### 1. Data Distribution
```
![Class Distribution](figures/class_distribution.png)
Shows balanced/imbalanced class distribution
```

### 2. Model Performance Comparison
```
![Model Comparison](image.png)
Bar chart comparing Accuracy, Precision, Recall, F1, ROC-AUC
```

### 3. ROC Curves
```
![Combined ROC Curves](image-1.png)
ROC curves for all 6 models (baseline + tuned)
```

### 4. Feature Importance
```
![Feature Importance Example](image-2.png)
Top 15 features driving predictions
```

### 5. Confusion Matrix Example
```
![Confusion Matrix example](image-3.png)
Shows True Positives, False Positives, True Negatives, False Negatives
```

---

## 🔧 Running Individual Scripts (Optional)

If you need to run scripts individually:

```bash
# Step 1: Transform raw data
python 01_transform_vulns.py

# Step 2: Exploratory analysis
python 02_eda.py

# Step 3: Preprocessing setup
python 03_preprocess.py

# Step 4: Train baseline models
python 04_train_models.py

# Step 5: Hyperparameter tuning
python 05_hyperparameter_tuning.py

# Step 6: Compare models
python 06_model_comparison.py

# Step 7: Misclassification analysis
python 07_misclassification_analysis.py

# Step 8: ROC curves
python 08_combined_roc_curves.py

# Step 9: Feature importance
python 09_feature_importance_dashboard.py
```

**Note:** Scripts must be run in this order due to dependencies.

---

## 📊 Key Results Summary

### Best Performing Model
- **Model:** XGBoost (Baseline)
- **ROC-AUC:** 0.9344
- **F1 Score:** 0.93
- **Accuracy:** 89.00%

### Dataset Statistics
- **Total Samples:** 1,200 vulnerabilities
- **Training Set:** 960 samples (80%)
- **Test Set:** 240 samples (20%)
- **Class Distribution:**
  - Non-Misconfiguration: 292 (24.3%)
  - Misconfiguration: 908 (75.7%)
- **After SMOTE Balancing:** 1,452 samples (726 per class)

### Feature Importance Insights
Top 3 most important features:
1. **severity** - Overall vulnerability severity score
2. **public_exposure** - Whether resource is publicly accessible
3. **unencrypted** - Encryption status

### Model Comparison
| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|-------|----------|-----------|--------|----------|---------|
| LogReg (base) | 84.00% | 0.86 | 0.84 | 0.85 | 0.9069 |
| RF (base) | 90.00% | 0.90 | 0.90 | 0.90 | 0.9138 |
| **XGBoost (base)** | **89.00%** | **0.89** | **0.89** | **0.89** | **0.9344** |
| LogReg (tuned) | 85.00% | 0.88 | 0.85 | 0.86 | 0.9231 |
| RF (tuned) | 88.00% | 0.89 | 0.88 | 0.88 | 0.9254 |
| XGBoost (tuned) | 87.00% | 0.88 | 0.87 | 0.87 | 0.9314 |

### Misclassification Analysis
Security-critical False Negatives (missed misconfigurations):
- **LogReg (base):** 28 missed
- **RF (base):** 9 missed ✓ Best
- **XGBoost (base):** 15 missed
- **LogReg (tuned):** 27 missed
- **RF (tuned):** 16 missed
- **XGBoost (tuned):** 18 missed

**Key Finding:** Random Forest (baseline) has the lowest false negative rate, making it most suitable for security applications where missing a misconfiguration is more costly than a false alarm.

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Module Not Found Error
```
ModuleNotFoundError: No module named 'xgboost'
```
**Solution:**
```bash
pip install -r requirements.txt
```

#### Issue 2: Dataset File Not Found
```
FileNotFoundError: CLOUD_VULRABILITES_DATASET.jsonl
```
**Solution:**
- Ensure the dataset file is in the project root directory
- Check filename spelling matches exactly (case-sensitive)

#### Issue 3: Memory Error
```
MemoryError: Unable to allocate array
```
**Solution:**
- Close other applications to free RAM
- Reduce sample size in `09_feature_importance_dashboard.py` (line 59)

#### Issue 4: Permission Denied (Windows)
```
PermissionError: [WinError 32]
```
**Solution:**
- Close any programs viewing output files
- Run terminal as Administrator

---

## 📝 Code Structure and Design

### Key Design Decisions

1. **No Data Leakage:** Removed 'misconfiguration' keyword from features to prevent target leakage
2. **Modular Preprocessing:** Centralized in `03_preprocess.py` for consistency
3. **SMOTE for Imbalance:** Applied SMOTE to handle class imbalance
4. **Comprehensive Evaluation:** Multiple metrics (Accuracy, Precision, Recall, F1, ROC-AUC)

### Script Purposes

| Script | Purpose |
|--------|---------|
| 01 | Transform JSONL to CSV with engineered features |
| 02 | Generate EDA visualizations |
| 03 | Set up preprocessing pipeline (imported by others) |
| 04 | Train baseline models |
| 05 | Perform hyperparameter tuning |
| 06 | Compare all models |
| 07 | Analyze misclassifications |
| 08 | Generate ROC curves |
| 09 | Feature importance analysis |
| 11 | Automated pipeline orchestrator |

---

## 📧 Contact Information

For questions or issues:
- **Name:** Parul Inamdar
- **Email:** paruluw@uw.edu
- **Student ID:** 2531158

---

## 📄 License

This project is submitted for academic purposes as part of CSS 581 A Machine Learning.

---

## ✅ Submission Checklist

- [x] All source code files (10 Python scripts)
- [x] requirements.txt with dependencies
- [x] README.md with complete instructions
- [x] Dataset or shareable link provided
- [x] Screenshots demonstrating execution
- [x] Results and outputs documented
- [x] Troubleshooting guide included
- [x] All files packaged in single .zip

---

**Last Updated:** December 8, 2025