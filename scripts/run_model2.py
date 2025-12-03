#!/usr/bin/env python3
"""
Model 2 Runner: Single-Ancestry Mismatched PRS-CS
Uses EAS GWAS with EUR LD reference (simulates missing EAS LD panel)
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
MODEL2_OUTPUT = f"{PROJECT_DIR}/output/02_Single_Mismatch"

# Create temporary LD reference where only EUR is available
TEMP_REF_DIR = f"{PROJECT_DIR}/prs_reference_model2_temp"

def setup_model2_ld():
    """Create temporary LD reference structure for Model 2 (EUR LD for EAS)"""
    print("Setting up Model 2 LD reference (EUR LD for EAS GWAS - single ancestry mismatch)...")
    
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
    
    # For Model 2, EAS population uses EUR LD (mismatch scenario)
    eas_ld_dst = Path(f"{TEMP_REF_DIR}/ldblk_1kg_eas")
    shutil.copytree(eur_ld_src, eas_ld_dst)
    print(f"  ✓ Created EAS LD as copy of EUR (mismatch scenario): {eas_ld_dst}")
    
    return TEMP_REF_DIR

def cleanup_model2_ld(temp_ref):
    """Remove temporary LD reference"""
    if Path(temp_ref).exists():
        shutil.rmtree(temp_ref)
        print(f"✓ Cleaned up temporary reference: {temp_ref}")

def run_model2(chromosome, temp_ref):
    """Run Model 2 with EUR LD reference for EAS GWAS (single-ancestry mismatch)"""
    print(f"\nRunning Model 2 (Single-Ancestry Mismatch) for chromosome {chromosome}...")
    print("Configuration:")
    print("  - Single population: EAS GWAS")
    print("  - LD Reference: EUR (mismatched ancestry)")
    print("  - Scenario: Simulates researcher lacking matched EAS LD panel")
    print()
    
    os.makedirs(MODEL2_OUTPUT, exist_ok=True)
    
    # Model 2 uses single population (EAS) with EUR LD
    cmd = [
        "python3",
        f"{PROJECT_DIR}/PRScsx.py",
        f"--ref_dir={temp_ref}",
        f"--bim_prefix={MODEL_INPUT}/EAS_plink_5k",
        f"--sst_file={MODEL_INPUT}/EAS_sumstats.txt",
        "--n_gwas=200",
        "--pop=EAS",
        f"--chrom={chromosome}",
        "--phi=1e-2",
        f"--out_dir={MODEL2_OUTPUT}",
        "--out_name=model2_eas_eur_ld"
    ]
    
    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    return result.returncode == 0

def main():
    chromosome = "1"  # Run for chromosome 1 only
    
    print("=" * 70)
    print("Model 2: Single-Ancestry Mismatched PRS-CS")
    print("=" * 70)
    print()
    
    # Setup temporary LD reference
    temp_ref = setup_model2_ld()
    
    try:
        # Run Model 2
        success = run_model2(chromosome, temp_ref)
        
        if success:
            print()
            print("=" * 70)
            print("✓ Model 2 Completed Successfully")
            print("=" * 70)
            print()
            print("Output files:")
            import glob
            output_files = sorted(glob.glob(f"{MODEL2_OUTPUT}/model2_eas_eur_ld_*_chr{chromosome}.txt"))
            for f in output_files:
                if Path(f).exists():
                    size_kb = Path(f).stat().st_size / 1024
                    print(f"  {Path(f).name} ({size_kb:.0f} KB)")
            print()
            return 0
        else:
            print("✗ Model 2 failed")
            return 1
    
    finally:
        # Cleanup
        cleanup_model2_ld(temp_ref)

if __name__ == "__main__":
    sys.exit(main())
