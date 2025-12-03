#!/usr/bin/env python3

"""
Model 1 Setup Verification Script
Purpose: Verify all inputs are present and correctly formatted before running Model 1

Usage:
    python3 verify_model1_setup.py
"""

import os
import sys
from pathlib import Path
import pandas as pd


def check_file_exists(path, description):
    """Check if a file exists and report status."""
    path = Path(path)
    if path.exists():
        size_kb = path.stat().st_size / 1024
        print(f"  ✓ {description}: {path}")
        print(f"    Size: {size_kb:.1f} KB")
        return True
    else:
        print(f"  ✗ {description}: {path} NOT FOUND")
        return False


def check_directory_exists(path, description):
    """Check if a directory exists and report status."""
    path = Path(path)
    if path.is_dir():
        print(f"  ✓ {description}: {path}")
        return True
    else:
        print(f"  ✗ {description}: {path} NOT FOUND")
        return False


def check_plink_files(prefix, description):
    """Check for PLINK binary files (.bed, .bim, .fam)."""
    bed = Path(f"{prefix}.bed")
    bim = Path(f"{prefix}.bim")
    fam = Path(f"{prefix}.fam")
    
    all_present = bed.exists() and bim.exists() and fam.exists()
    
    print(f"  {'✓' if all_present else '✗'} {description}")
    print(f"    {prefix}.bed: {'✓' if bed.exists() else '✗'}")
    print(f"    {prefix}.bim: {'✓' if bim.exists() else '✗'}")
    print(f"    {prefix}.fam: {'✓' if fam.exists() else '✗'}")
    
    if bim.exists():
        bim_size = len(pd.read_csv(bim, sep='\s+', header=None))
        print(f"    SNPs in .bim: {bim_size}")
    
    return all_present


def check_gwas_format(filepath, population):
    """Check GWAS summary stats file format."""
    print(f"  Checking {population} GWAS format...")
    
    try:
        # Read first few lines to check format
        df = pd.read_csv(filepath, sep='\s+', nrows=5)
        
        print(f"    Columns: {', '.join(df.columns)}")
        print(f"    Rows in file: {sum(1 for _ in open(filepath)) - 1}")  # -1 for header
        
        # Check for required columns (flexible naming)
        required_cols = {'snp', 'a1', 'a2', 'beta', 'p', 'chr', 'pos'}
        df_cols_lower = {col.lower() for col in df.columns}
        
        has_required = required_cols.issubset(df_cols_lower)
        
        if has_required:
            print(f"    ✓ Has all required columns")
            return True
        else:
            missing = required_cols - df_cols_lower
            print(f"    ⚠ Missing columns: {', '.join(missing)}")
            return False
    
    except Exception as e:
        print(f"    ✗ Error reading file: {e}")
        return False


def check_ld_reference(ldblk_dir, population):
    """Check LD reference panel structure."""
    ldblk_path = Path(ldblk_dir)
    
    if not ldblk_path.is_dir():
        print(f"  ✗ LD directory not found: {ldblk_dir}")
        return False
    
    print(f"  ✓ LD reference directory exists: {ldblk_dir}")
    
    # Check for chromosome files
    chr_files = sorted(ldblk_path.glob("chr*.txt"))
    
    print(f"    Chromosome blocks found: {len(chr_files)}")
    
    if len(chr_files) >= 22:
        print(f"    ✓ All 22 chromosomes present")
        return True
    else:
        print(f"    ⚠ Only {len(chr_files)} chromosomes found (expected 22)")
        return False


def main():
    print("=" * 70)
    print("Model 1: Baseline (Fully Matched PRS-CSx) - Setup Verification")
    print("=" * 70)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # 1. Check GWAS Summary Statistics
    print("1. GWAS SUMMARY STATISTICS")
    print("-" * 70)
    
    eur_stats = "/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx/Model_input/EUR_sumstats.txt"
    eas_stats = "/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx/Model_input/EAS_sumstats.txt"
    
    checks_total += 2
    if check_file_exists(eur_stats, "EUR GWAS"):
        checks_passed += 1
        if check_gwas_format(eur_stats, "EUR"):
            checks_passed += 0.5
    
    if check_file_exists(eas_stats, "EAS GWAS"):
        checks_passed += 1
        if check_gwas_format(eas_stats, "EAS"):
            checks_passed += 0.5
    
    print()
    
    # 2. Check PLINK Validation Genotypes
    print("2. VALIDATION GENOTYPES (PLINK FORMAT)")
    print("-" * 70)
    
    eur_bim = "/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx/Model_input/EUR_plink_5k"
    checks_total += 1
    if check_plink_files(eur_bim, "EUR validation genotypes"):
        checks_passed += 1
    
    print()
    
    # 3. Check LD Reference Panels
    print("3. LD REFERENCE PANELS (1000 GENOMES)")
    print("-" * 70)
    
    ref_base = "./prs_reference"
    eur_ldblk = f"{ref_base}/ldblk_1kg_eur"
    eas_ldblk = f"{ref_base}/ldblk_1kg_eas"
    
    checks_total += 2
    if check_ld_reference(eur_ldblk, "EUR"):
        checks_passed += 1
    if check_ld_reference(eas_ldblk, "EAS"):
        checks_passed += 1
    
    print()
    
    # 4. Check Output Directory
    print("4. OUTPUT DIRECTORY")
    print("-" * 70)
    
    out_dir = "/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx/Model_output/Model1_CSx_Matched"
    out_path = Path(out_dir)
    
    checks_total += 1
    if out_path.exists():
        print(f"  ✓ Output directory exists: {out_dir}")
        existing_files = list(out_path.glob("*.txt"))
        if existing_files:
            print(f"    Warning: {len(existing_files)} existing output files found")
            print(f"    These will be overwritten if you re-run Model 1")
        checks_passed += 1
    else:
        print(f"  ℹ Output directory will be created: {out_dir}")
        checks_passed += 1
    
    print()
    
    # 5. Check Python Dependencies
    print("5. PYTHON DEPENDENCIES")
    print("-" * 70)
    
    required_modules = ['pandas', 'numpy', 'scipy']
    checks_total += len(required_modules)
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {module} is installed")
            checks_passed += 1
        except ImportError:
            print(f"  ✗ {module} is NOT installed")
            print(f"    Install with: pip install {module}")
    
    print()
    
    # 6. Check PRScsx.py script
    print("6. PRSCSX SCRIPT")
    print("-" * 70)
    
    prscsx_script = "PRScsx.py"
    checks_total += 1
    
    if check_file_exists(prscsx_script, "PRScsx.py"):
        checks_passed += 1
    
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Checks passed: {int(checks_passed)}/{int(checks_total)}")
    print()
    
    if checks_passed >= checks_total - 1:
        print("✓ Setup verification PASSED")
        print()
        print("You can now run Model 1 with:")
        print("  bash run_model1_baseline.sh")
        print()
        print("Or run a single chromosome for testing with:")
        print("  python3 PRScsx.py \\")
        print('    --ref_dir="./prs_reference" \\')
        print('    --bim_prefix="Model_input/EUR_plink_5k" \\')
        print('    --sst_file="Model_input/EUR_sumstats.txt,Model_input/EAS_sumstats.txt" \\')
        print('    --n_gwas=10000,10000 \\')
        print('    --pop=EUR,EAS \\')
        print('    --chrom=1 \\')
        print('    --phi=1e-2 \\')
        print('    --out_dir="Model_output/Model1_CSx_Matched" \\')
        print('    --out_name="model1"')
        print()
        return 0
    else:
        print("✗ Setup verification FAILED")
        print()
        print("Please fix the issues above before running Model 1")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
