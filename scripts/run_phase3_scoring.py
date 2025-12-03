#!/usr/bin/env python3
"""
Phase 3: PLINK Scoring Pipeline
Applies posterior SNP weights to target EAS genotypes to calculate polygenic risk scores
"""

import os
import subprocess
import sys
from pathlib import Path

# Paths
PROJECT_ROOT = "/Users/enockniyonkuru/Desktop/Biostats/Project"
ASSIGNMENT_DIR = os.path.join(PROJECT_ROOT, "assignment")
WEIGHT_DIR = os.path.join(ASSIGNMENT_DIR, "Model_output")
SCORING_OUTPUT_DIR = os.path.join(ASSIGNMENT_DIR, "Phase3_Scores")

# Target genotype file (EAS)
TARGET_BFILE = os.path.join(ASSIGNMENT_DIR, "Model_input/EAS_plink_5k")

# PLINK executable - try common locations
PLINK_PATHS = [
    "/usr/local/bin/plink",
    "/opt/homebrew/bin/plink",
    "/Users/enockniyonkuru/Desktop/Biostats/Project/plink-ng/bin/plink",
    "plink"  # Fallback to PATH
]

def find_plink():
    """Find PLINK executable"""
    for path in PLINK_PATHS:
        if os.path.exists(path):
            print(f"✓ Found PLINK at: {path}")
            return path
    print("⚠ PLINK not found at expected locations. Attempting to use 'plink' from PATH...")
    return "plink"

def setup_output_dir():
    """Create Phase 3 output directory"""
    os.makedirs(SCORING_OUTPUT_DIR, exist_ok=True)
    print(f"✓ Output directory ready: {SCORING_OUTPUT_DIR}")

def run_plink_score(plink_cmd, bfile, weight_file, model_name, pop_label, out_name):
    """Run PLINK scoring command"""
    cmd = [
        plink_cmd,
        "--bfile", bfile,
        "--score", weight_file, "1 2 6",  # CHR SNP BETA columns
        "--out", out_name,
        "--allow-no-sex"
    ]
    
    print(f"\n{'='*80}")
    print(f"Model: {model_name} | Population: {pop_label}")
    print(f"Weight File: {os.path.basename(weight_file)}")
    print(f"Output: {os.path.basename(out_name)}.profile")
    print(f"{'='*80}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Scoring completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Scoring failed with error:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"✗ PLINK executable not found")
        return False

def main():
    print("\n" + "="*80)
    print("PHASE 3: PLINK SCORING PIPELINE")
    print("="*80)
    
    # Setup
    setup_output_dir()
    plink_cmd = find_plink()
    
    # Verify target genotype file exists
    if not os.path.exists(f"{TARGET_BFILE}.bed"):
        print(f"✗ Error: Target genotype file not found: {TARGET_BFILE}")
        sys.exit(1)
    
    print(f"\n✓ Target genotype (EAS): {TARGET_BFILE}")
    
    # Define models and their weight files
    models = {
        "Model 1: Baseline (Fully Matched)": {
            "EUR": os.path.join(WEIGHT_DIR, "Model1_CSx_Matched/model1_EUR_pst_eff_a1_b0.5_phi1e-02_chr1.txt"),
            "EAS": os.path.join(WEIGHT_DIR, "Model1_CSx_Matched/model1_EAS_pst_eff_a1_b0.5_phi1e-02_chr1.txt"),
        },
        "Model 2: Single-Ancestry Mismatch": {
            "EAS": os.path.join(WEIGHT_DIR, "Model2_CS_Single_Mismatch/model2_eas_eur_ld_EAS_pst_eff_a1_b0.5_phi1e-02_chr1.txt"),
        },
        "Model 3: Partial Mismatch (Multi-Ancestry)": {
            "EUR": os.path.join(WEIGHT_DIR, "Model3_CSx_Partial_Mismatch/model3_EUR_pst_eff_a1_b0.5_phi1e-02_chr1.txt"),
            "EAS": os.path.join(WEIGHT_DIR, "Model3_CSx_Partial_Mismatch/model3_EAS_pst_eff_a1_b0.5_phi1e-02_chr1.txt"),
        },
        "Model 4: Unified Fallback (AMR LD)": {
            "EUR": os.path.join(WEIGHT_DIR, "Model4_AMR_LD/model4_EUR_pst_eff_a1_b0.5_phi1e-02_chr1.txt"),
            "EAS": os.path.join(WEIGHT_DIR, "Model4_AMR_LD/model4_EAS_pst_eff_a1_b0.5_phi1e-02_chr1.txt"),
        },
        "Model 5: Unified Fallback (SAS LD)": {
            "EUR": os.path.join(WEIGHT_DIR, "Model5_SAS_LD/model5_EUR_pst_eff_a1_b0.5_phi1e-02_chr1.txt"),
            "EAS": os.path.join(WEIGHT_DIR, "Model5_SAS_LD/model5_EAS_pst_eff_a1_b0.5_phi1e-02_chr1.txt"),
        },
    }
    
    # Track results
    results = {
        "successful": [],
        "failed": []
    }
    
    # Run scoring for each model
    for model_name, weights in models.items():
        for pop, weight_file in weights.items():
            # Check weight file exists
            if not os.path.exists(weight_file):
                print(f"\n✗ Weight file not found: {weight_file}")
                results["failed"].append(f"{model_name} ({pop})")
                continue
            
            # Create output name
            model_id = model_name.split(":")[0].lower().replace(" ", "")
            out_name = os.path.join(SCORING_OUTPUT_DIR, f"{model_id}_{pop.lower()}")
            
            # Run scoring
            success = run_plink_score(plink_cmd, TARGET_BFILE, weight_file, model_name, pop, out_name)
            
            if success:
                results["successful"].append({
                    "model": model_name,
                    "pop": pop,
                    "profile": f"{out_name}.profile"
                })
            else:
                results["failed"].append(f"{model_name} ({pop})")
    
    # Summary
    print("\n" + "="*80)
    print("PHASE 3 SUMMARY")
    print("="*80)
    
    print(f"\n✓ Successful Scores: {len(results['successful'])}")
    for result in results["successful"]:
        print(f"  • {result['model']} ({result['pop']}): {result['profile']}")
    
    if results["failed"]:
        print(f"\n✗ Failed Scores: {len(results['failed'])}")
        for failed in results["failed"]:
            print(f"  • {failed}")
    
    print(f"\n{'='*80}")
    print("Next Step: Phase 4 - Statistical Analysis")
    print("Parse .profile files, merge with phenotype data, and calculate R²")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
