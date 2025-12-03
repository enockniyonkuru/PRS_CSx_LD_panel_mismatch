#!/usr/bin/env python3
"""
Phase 3: Pure Python PLINK Scoring Pipeline
Applies posterior SNP weights to target EAS genotypes to calculate polygenic risk scores
No external PLINK binary needed - pure Python implementation
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = "/Users/enockniyonkuru/Desktop/Biostats/Project"
ASSIGNMENT_DIR = os.path.join(PROJECT_ROOT, "assignment")
WEIGHT_DIR = os.path.join(ASSIGNMENT_DIR, "Model_output")
SCORING_OUTPUT_DIR = os.path.join(ASSIGNMENT_DIR, "Phase3_Scores")

def setup_output_dir():
    """Create Phase 3 output directory"""
    os.makedirs(SCORING_OUTPUT_DIR, exist_ok=True)
    print(f"✓ Output directory ready: {SCORING_OUTPUT_DIR}")

def read_bim_file(bim_path):
    """
    Read PLINK .bim file
    Format: CHR SNP PLINK_POS(cM) BP_POS A1 A2 (whitespace separated)
    Note: PLINK_POS is usually 0, we use BP_POS
    """
    bim = pd.read_csv(
        bim_path,
        sep='\s+',
        header=None,
        names=['CHR', 'SNP', 'PLINK_POS', 'BP_POS', 'A1', 'A2']
    )
    # Rename BP_POS to POS for consistency
    bim['POS'] = bim['BP_POS']
    return bim[['CHR', 'SNP', 'POS', 'A1', 'A2']]

def read_weight_file(weight_path):
    """
    Read PRS-CSx weight file
    Format: CHR SNP POS A1 A2 BETA
    """
    weights = pd.read_csv(
        weight_path,
        sep='\t',
        header=None,
        names=['CHR', 'SNP', 'POS', 'A1', 'A2', 'BETA']
    )
    return weights

def read_bed_file(bed_path, bim_df, fam_path):
    """
    Read PLINK .bed file (binary genotype format)
    Returns genotypes as numpy array [n_samples x n_snps]
    
    .bed file format (binary):
    - Bytes 0-2: Magic number (0x6c 0x1b 0x01 for SNP-major order)
    - Bytes 3+: Genotype data packed 2 bits per genotype
    """
    import struct
    
    # Read .fam to get number of samples
    with open(fam_path, 'r') as f:
        n_samples = sum(1 for _ in f)
    
    n_snps = len(bim_df)
    
    # Genotypes: 0=homozygous ref, 1=het, 2=homozygous alt, 3=missing
    genotypes = np.zeros((n_samples, n_snps), dtype=np.uint8)
    
    with open(bed_path, 'rb') as f:
        # Read and verify magic number
        magic = f.read(3)
        if magic != b'\x6c\x1b\x01':
            raise ValueError(f"Invalid .bed file magic number: {magic.hex()}")
        
        # SNP-major order: genotypes for one SNP across all samples
        bytes_per_snp = (n_samples + 3) // 4  # 4 genotypes per byte
        
        for snp_idx in range(n_snps):
            snp_bytes = f.read(bytes_per_snp)
            for sample_idx in range(n_samples):
                byte_idx = sample_idx // 4
                bit_idx = (sample_idx % 4) * 2
                geno_bits = (snp_bytes[byte_idx] >> bit_idx) & 0x03
                genotypes[sample_idx, snp_idx] = geno_bits
    
    return genotypes

def match_weights_to_genotypes(genotypes, bim_df, weights_df):
    """
    Match weight file SNPs to genotype SNPs.
    Returns matched genotypes and weights aligned by SNP ID and position.
    """
    # Create dual index from bim file (SNP ID and CHR:POS)
    snp_to_idx = {snp: idx for idx, snp in enumerate(bim_df['SNP'])}
    pos_to_idx = {(row['CHR'], row['POS']): idx for idx, (_, row) in enumerate(bim_df.iterrows())}
    
    # Match weights to genotypes
    matched_idx = []
    matched_weights = []
    
    for _, weight_row in weights_df.iterrows():
        snp_id = weight_row['SNP']
        chr_val = weight_row['CHR']
        pos_val = weight_row['POS']
        
        # Try SNP ID match first
        if snp_id in snp_to_idx:
            idx = snp_to_idx[snp_id]
            matched_idx.append(idx)
            matched_weights.append(weight_row['BETA'])
        # Try CHR:POS match as fallback
        elif (chr_val, pos_val) in pos_to_idx:
            idx = pos_to_idx[(chr_val, pos_val)]
            matched_idx.append(idx)
            matched_weights.append(weight_row['BETA'])
    
    # Select matching genotypes
    matched_genotypes = genotypes[:, matched_idx]
    matched_weights = np.array(matched_weights)
    
    print(f"  Matched {len(matched_weights)} SNPs out of {len(weights_df)} weights")
    
    return matched_genotypes, matched_weights

def calculate_scores(genotypes, weights):
    """
    Calculate PRS for each individual
    PRS = sum(genotype * weight)
    
    For missing genotypes (coded as 3), we impute as mean genotype
    """
    # Handle missing genotypes (3 -> NaN for imputation)
    geno_float = genotypes.astype(float)
    geno_float[geno_float == 3] = np.nan
    
    # Impute missing with column mean (allele frequency * 2)
    col_means = np.nanmean(geno_float, axis=0)
    for snp_idx in range(geno_float.shape[1]):
        mask = np.isnan(geno_float[:, snp_idx])
        geno_float[mask, snp_idx] = col_means[snp_idx]
    
    # Calculate PRS = sum(geno * weight) for each individual
    prs = np.dot(geno_float, weights)
    
    return prs

def write_profile_file(output_path, fam_df, prs_scores, model_name):
    """
    Write PLINK .profile-like output
    Format: FID IID PHENO CNT CNT2 SCORE
    """
    profile_df = pd.DataFrame({
        'FID': fam_df['FID'],
        'IID': fam_df['IID'],
        'PHENO': fam_df['PHENO'],
        'CNT': len(prs_scores) if len(prs_scores) > 0 else 0,  # n_SNPs in score
        'CNT2': len(prs_scores) if len(prs_scores) > 0 else 0,
        'SCORE': prs_scores
    })
    
    profile_df.to_csv(output_path, sep=' ', index=False)
    print(f"  ✓ Profile saved: {os.path.basename(output_path)}")
    
    # Print summary statistics
    print(f"    Score mean={prs_scores.mean():.4f}, std={prs_scores.std():.4f}")
    print(f"    Range=[{prs_scores.min():.4f}, {prs_scores.max():.4f}]")

def read_fam_file(fam_path):
    """Read PLINK .fam file"""
    fam = pd.read_csv(
        fam_path,
        sep='\s+',
        header=None,
        names=['FID', 'IID', 'PID', 'MID', 'SEX', 'PHENO']
    )
    return fam

def score_model(bfile_prefix, weight_file, model_name, pop_label, output_base):
    """
    Score a single model
    """
    # Check files exist
    bim_file = f"{bfile_prefix}.bim"
    bed_file = f"{bfile_prefix}.bed"
    fam_file = f"{bfile_prefix}.fam"
    
    for f in [bim_file, bed_file, fam_file, weight_file]:
        if not os.path.exists(f):
            print(f"  ✗ File not found: {f}")
            return False
    
    try:
        # Read files
        print(f"  Reading genotypes...")
        bim_df = read_bim_file(bim_file)
        fam_df = read_fam_file(fam_file)
        genotypes = read_bed_file(bed_file, bim_df, fam_file)
        
        print(f"  Reading weights...")
        weights_df = read_weight_file(weight_file)
        
        # Match and score
        print(f"  Matching and scoring...")
        matched_geno, matched_weights = match_weights_to_genotypes(
            genotypes, bim_df, weights_df
        )
        
        # Calculate PRS
        prs_scores = calculate_scores(matched_geno, matched_weights)
        
        # Write output
        output_file = f"{output_base}.profile"
        write_profile_file(output_file, fam_df, prs_scores, model_name)
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*80)
    print("PHASE 3: PLINK SCORING PIPELINE (Pure Python)")
    print("="*80)
    
    # Setup
    setup_output_dir()
    
    # Target genotype file (EAS)
    target_bfile = os.path.join(ASSIGNMENT_DIR, "Model_input/EAS_plink_5k")
    
    print(f"\n✓ Target genotype (EAS): {target_bfile}")
    
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
        print(f"\n{model_name}")
        print("-" * 80)
        
        for pop, weight_file in weights.items():
            print(f"\nPopulation: {pop}")
            
            # Create output name
            model_id = model_name.split(":")[0].lower().replace(" ", "")
            out_base = os.path.join(SCORING_OUTPUT_DIR, f"{model_id}_{pop.lower()}")
            
            # Score
            success = score_model(
                target_bfile,
                weight_file,
                model_name,
                pop,
                out_base
            )
            
            if success:
                results["successful"].append({
                    "model": model_name,
                    "pop": pop,
                    "profile": f"{out_base}.profile"
                })
            else:
                results["failed"].append(f"{model_name} ({pop})")
    
    # Summary
    print("\n" + "="*80)
    print("PHASE 3 SUMMARY")
    print("="*80)
    
    print(f"\n✓ Successful Scores: {len(results['successful'])}")
    for result in results["successful"]:
        profile_file = result['profile']
        if os.path.exists(profile_file):
            size = os.path.getsize(profile_file) / 1024
            print(f"  • {result['model']} ({result['pop']}): {os.path.basename(profile_file)} ({size:.1f} KB)")
    
    if results["failed"]:
        print(f"\n✗ Failed Scores: {len(results['failed'])}")
        for failed in results["failed"]:
            print(f"  • {failed}")
    
    print(f"\n{'='*80}")
    print("Scoring Output Location:")
    print(f"  {SCORING_OUTPUT_DIR}")
    print(f"{'='*80}")
    print("\nNext Step: Phase 4 - Statistical Analysis")
    print("Parse .profile files, merge with phenotype data, and calculate R²")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
