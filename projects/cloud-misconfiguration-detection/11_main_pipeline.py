"""
Complete ML Pipeline for Cloud Vulnerability Classification
Executes all scripts in correct dependency order
"""
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def print_header(step_num, description):
    """Print formatted step header"""
    print("\n" + "="*70)
    print(f"STEP {step_num}: {description}")
    print("="*70)

def run_script(script_name, description, step_num):
    """Run a Python script with error handling and timing"""
    print_header(step_num, description)
    
    # Check if file exists
    if not Path(script_name).exists():
        print(f"[ERROR] {script_name} not found!")
        return False
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["python", script_name],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("WARNING", result.stderr)
        
        elapsed = time.time() - start_time
        print(f"SUCCESS Completed in {elapsed:.2f} seconds")
        return True
        
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f" Failed after {elapsed:.2f} seconds")
        print("\nError output:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Execute complete pipeline"""
    start_time = datetime.now()
    
    print("\n" + "="*70)
    print("CLOUD VULNERABILITY CLASSIFICATION - COMPLETE PIPELINE")
    print("="*70)
    print(f"\nStarted at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Define pipeline in CORRECT dependency order
    pipeline = [
        # PHASE 1: Data Preparation
        ("01_transform_vulns.py", "Data Transformation & Feature Engineering", 1),
        
        # PHASE 2: Exploratory Analysis
        ("02_eda.py", "Exploratory Data Analysis & Visualizations", 2),
        ("03_preprocess.py", "Preprocessing Setup & Validation", 3),
        
        # PHASE 3: Baseline Models
        ("04_train_models.py", "Train Baseline Models (LogReg, RF, XGBoost)", 4),
        
        # PHASE 4: Model Optimization
        ("05_hyperparameter_tuning.py", "Hyperparameter Tuning", 5),
        
        # PHASE 5: Comprehensive Analysis
        ("06_model_comparison.py", "Compare Baseline vs Tuned Models", 6),
        ("07_misclassification_analysis.py", "Analyze Misclassification Patterns", 7),
        ("08_combined_roc_curves.py", "Generate Combined ROC Curves", 8),
        ("09_feature_importance_dashboard.py", "Feature Importance Analysis", 9),
        
    ]
    
    results = {}
    
    # Execute pipeline
    for script, description, step_num in pipeline:
        success = run_script(script, description, step_num)
        results[script] = success
        
        if not success:
            print("\n" + "="*70)
            print(f"PIPELINE STOPPED: Error in {script}")
            print("="*70)
            print("\nFix the error above and re-run the pipeline")
            
            # Show which steps completed
            print("\nProgress Report:")
            for s, status in results.items():
                icon = "OK" if status else "FAIL"
                print(f"  {icon} {s}")
            
            sys.exit(1)
        
        # Brief pause between steps (optional, helps with readability)
        time.sleep(0.5)
    
    # Success summary
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print("\n" + "="*70)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70)
    
    print(f"\nTotal execution time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
    print(f"Started:  {start_time.strftime('%H:%M:%S')}")
    print(f"Finished: {end_time.strftime('%H:%M:%S')}")
    
    print("\nGenerated Outputs:")
    print("   figures/                    - EDA visualizations")
    print("   results/                    - Baseline model files")
    print("   results/tuned_models/       - Optimized models")
    print("   results/comparison/         - Model comparison charts")
    print("   results/misclassification/  - Error analysis CSVs")
    print("   results/roc/                - ROC curves")
    print("   results/feature_importance/ - Feature analysis")
    print("   results/clustered_vulns.csv - Clustering results")
    
    print("\nNext Steps:")
    print("   1. Review visualizations in figures/")
    print("   2. Check model comparison in results/comparison/")
    print("   3. Analyze misclassifications in results/misclassification/")
    print("   4. Use best model from results/tuned_models/")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    # Pre-flight checks
    print("Pre-flight checks...")
    
    required_files = [
        "CLOUD_VULRABILITES_DATASET.jsonl",
        "03_preprocess.py"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f" MISSING {file}")
        else:
            print(f" OK {file}")
    
    if missing:
        print(f"\n Cannot start: Missing required files")
        print("Please ensure these files exist:")
        for f in missing:
            print(f"  - {f}")
        sys.exit(1)
    
    print("\n All checks passed. Starting pipeline...\n")
    time.sleep(1)
    
    main()