#!/usr/bin/env python3
"""
Model 5 Runner: Multi-Ancestry with SAS LD Alternative (Both Populations)
EUR GWAS + SAS LD (alternative) + EAS GWAS + SAS LD (alternative)
Tests if unified alternative ancestry LD can serve as fallback for both populations
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Paths
PROJECT_DIR = "/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx"
REF_DIR = f"{PROJECT_DIR}/prs_reference"
MODEL_INPUT = f"{PROJECT_DIR}/../assignment/Model_input"
MODEL5_OUTPUT = f"{PROJECT_DIR}/output/05_SAS_LD"

# Create temporary LD reference where both EUR and EAS use SAS LD
TEMP_REF_DIR = f"{PROJECT_DIR}/prs_reference_model5_temp"

def setup_model5_ld():
    """Create temporary LD reference structure for Model 5 (both EUR and EAS use SAS LD)"""
    print("Setting up Model 5 LD reference (SAS LD as unified alternative for both EUR and EAS)...")
    
    # Create temp directory
    temp_path = Path(TEMP_REF_DIR)
    if temp_path.exists():
        shutil.rmtree(temp_path)
    temp_path.mkdir(parents=True, exist_ok=True)
    
    # Copy snpinfo file
    shutil.copy(
        f"{REF_DIR}/snpinfo_mult_1kg_hm3",
        f"{TEMP_REF_DIR}/snpinfo_mult_1kg_hm3"
    )
    
    # Copy SAS LD blocks for EUR (alternative proxy)
    sas_ld_src = Path(f"{REF_DIR}/ldblk_1kg_sas")
    eur_ld_dst = Path(f"{TEMP_REF_DIR}/ldblk_1kg_eur")
    shutil.copytree(sas_ld_src, eur_ld_dst)
    print(f"  ✓ Copied SAS LD blocks for EUR (alternative proxy): {eur_ld_dst}")
    
    # Copy SAS LD blocks for EAS (alternative proxy)
    eas_ld_dst = Path(f"{TEMP_REF_DIR}/ldblk_1kg_eas")
    shutil.copytree(sas_ld_src, eas_ld_dst)
    print(f"  ✓ Copied SAS LD blocks for EAS (alternative proxy): {eas_ld_dst}")
    
    return TEMP_REF_DIR

def cleanup_model5_ld(temp_ref):
    """Remove temporary LD reference"""
    if Path(temp_ref).exists():
        shutil.rmtree(temp_ref)
        print(f"✓ Cleaned up temporary reference: {temp_ref}")

def run_model5(chromosome, temp_ref):
    """Run Model 5 with SAS LD for both EUR and EAS"""
    print(f"\nRunning Model 5 (SAS LD Alternative - Unified) for chromosome {chromosome}...")
    print("Configuration:")
    print("  - EUR GWAS → SAS LD (alternative proxy)")
    print("  - EAS GWAS → SAS LD (alternative proxy)")
    print("  - Scenario: Both populations using same alternative ancestry LD")
    print()
    
    os.makedirs(MODEL5_OUTPUT, exist_ok=True)
    
    # Model 5: Multi-ancestry with both populations using SAS LD
    cmd = [
        "python3",
        f"{PROJECT_DIR}/PRScsx.py",
        f"--ref_dir={temp_ref}",
        f"--bim_prefix={MODEL_INPUT}/EUR_plink_5k",
        f"--sst_file={MODEL_INPUT}/EUR_sumstats.txt,{MODEL_INPUT}/EAS_sumstats.txt",
        "--n_gwas=10000,200",
        "--pop=EUR,EAS",
        f"--chrom={chromosome}",
        "--phi=1e-2",
        f"--out_dir={MODEL5_OUTPUT}",
        "--out_name=model5"
    ]
    
    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    return result.returncode == 0

def main():
    chromosome = "1"  # Run for chromosome 1 only
    
    print("=" * 70)
    print("Model 5: Multi-Ancestry with Unified SAS LD Alternative (PRS-CSx)")
    print("=" * 70)
    print()
    
    # Setup temporary LD reference
    temp_ref = setup_model5_ld()
    
    try:
        # Run Model 5
        success = run_model5(chromosome, temp_ref)
        
        if success:
            print()
            print("=" * 70)
            print("✓ Model 5 Completed Successfully")
            print("=" * 70)
            print()
            print("Output files:")
            import glob
            output_files = sorted(glob.glob(f"{MODEL5_OUTPUT}/model5_*_chr{chromosome}.txt"))
            for f in output_files:
                if Path(f).exists():
                    size_kb = Path(f).stat().st_size / 1024
                    print(f"  {Path(f).name} ({size_kb:.0f} KB)")
            print()
            return 0
        else:
            print("✗ Model 5 failed")
            return 1
    
    finally:
        # Cleanup
        cleanup_model5_ld(temp_ref)

if __name__ == "__main__":
    sys.exit(main())
