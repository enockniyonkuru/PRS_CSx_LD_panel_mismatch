#!/usr/bin/env python3
"""
Model 3 Runner with EUR LD Override
Forces both EUR and EAS GWAS to use EUR LD reference panels
(Simulates the partial mismatch scenario)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Paths
PROJECT_DIR = "/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx"
REF_DIR = f"{PROJECT_DIR}/prs_reference"
MODEL_INPUT = f"{PROJECT_DIR}/Model_input"
MODEL3_OUTPUT = f"{PROJECT_DIR}/Model_output/Model3_CSx_Partial_Mismatch"

# Create temporary LD reference where EAS points to EUR
TEMP_REF_DIR = f"{PROJECT_DIR}/prs_reference_model3_temp"

def setup_model3_ld():
    """Create temporary LD reference structure for Model 3 (EUR LD for both)"""
    print("Setting up Model 3 LD reference (EUR LD for both populations)...")
    
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
    
    # Copy EUR LD blocks
    eur_ld_src = Path(f"{REF_DIR}/ldblk_1kg_eur")
    eur_ld_dst = Path(f"{TEMP_REF_DIR}/ldblk_1kg_eur")
    shutil.copytree(eur_ld_src, eur_ld_dst)
    print(f"  ✓ Copied EUR LD blocks: {eur_ld_dst}")
    
    # Create EAS directory pointing to EUR (this is the mismatch)
    eas_ld_dst = Path(f"{TEMP_REF_DIR}/ldblk_1kg_eas")
    shutil.copytree(eur_ld_src, eas_ld_dst)
    print(f"  ✓ Created EAS LD as copy of EUR (mismatch scenario): {eas_ld_dst}")
    
    return TEMP_REF_DIR

def cleanup_model3_ld(temp_ref):
    """Remove temporary LD reference"""
    if Path(temp_ref).exists():
        shutil.rmtree(temp_ref)
        print(f"✓ Cleaned up temporary reference: {temp_ref}")

def run_model3(chromosome, temp_ref):
    """Run Model 3 with temporary EUR-only LD reference"""
    print(f"\nRunning Model 3 (Partial Mismatch) for chromosome {chromosome}...")
    print("Configuration:")
    print("  - EUR GWAS → EUR LD ✓ (matched)")
    print("  - EAS GWAS → EUR LD (mismatched, simulates missing EAS LD)")
    print()
    
    os.makedirs(MODEL3_OUTPUT, exist_ok=True)
    
    cmd = [
        "python3",
        f"{PROJECT_DIR}/PRScsx.py",
        f"--ref_dir={temp_ref}",
        f"--bim_prefix={MODEL_INPUT}/EUR_plink_5k",
        f"--sst_file={MODEL_INPUT}/EUR_sumstats.txt,{MODEL_INPUT}/EAS_sumstats.txt",
        "--n_gwas=10000,10000",
        "--pop=EUR,EAS",
        f"--chrom={chromosome}",
        "--phi=1e-2",
        f"--out_dir={MODEL3_OUTPUT}",
        "--out_name=model3"
    ]
    
    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    return result.returncode == 0

def main():
    chromosome = "1"  # Run for chromosome 1 only
    
    print("=" * 70)
    print("Model 3: Multi-Ancestry Partial Mismatch (PRS-CSx)")
    print("=" * 70)
    print()
    
    # Setup temporary LD reference
    temp_ref = setup_model3_ld()
    
    try:
        # Run Model 3
        success = run_model3(chromosome, temp_ref)
        
        if success:
            print()
            print("=" * 70)
            print("✓ Model 3 Completed Successfully")
            print("=" * 70)
            print()
            print("Output files:")
            import glob
            output_files = sorted(glob.glob(f"{MODEL3_OUTPUT}/model3_*_chr{chromosome}.txt"))
            for f in output_files:
                size_kb = Path(f).stat().st_size / 1024
                print(f"  {Path(f).name} ({size_kb:.0f} KB)")
            print()
            return 0
        else:
            print("✗ Model 3 failed")
            return 1
    
    finally:
        # Cleanup
        cleanup_model3_ld(temp_ref)

if __name__ == "__main__":
    sys.exit(main())
