#!/usr/bin/env bash
#############################################
# Model 1: Baseline (Fully Matched PRS-CSx)
# Purpose: Generate posterior SNP weights from EUR + EAS GWAS with matched LD panels
# Usage: bash run_model1_baseline.sh
#############################################

set -euo pipefail

# Configuration
REF_DIR="./prs_reference"
BIM_PREFIX="/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx/Model_input/EUR_plink_5k"
SST_EUR="/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx/Model_input/EUR_sumstats.txt"
SST_EAS="/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx/Model_input/EAS_sumstats.txt"
N_EUR="10000"
N_EAS="10000"
OUT_DIR="/Users/enockniyonkuru/Desktop/Biostats/Project/PRScsx/Model_output/Model1_CSx_Matched"
OUT_NAME="model1"
PHI="1e-2"

# MCMC Parameters (default from PRScsx)
N_ITER="1000"
N_BURNIN="500"
THIN="5"

# Parallelization
N_JOBS=4

# Limit math libraries to avoid oversubscribing
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1

# Create output directory
mkdir -p "${OUT_DIR}"

echo "============================================"
echo "Model 1: Baseline (Fully Matched PRS-CSx)"
echo "============================================"
echo ""
echo "Configuration:"
echo "  Reference Dir: ${REF_DIR}"
echo "  EUR GWAS: ${SST_EUR}"
echo "  EAS GWAS: ${SST_EAS}"
echo "  EUR Sample Size: ${N_EUR}"
echo "  EAS Sample Size: ${N_EAS}"
echo "  Global Shrinkage (phi): ${PHI}"
echo "  Output Dir: ${OUT_DIR}"
echo "  Parallelization: ${N_JOBS} jobs"
echo ""

# Function to run PRS-CSx for a single chromosome
run_chr() {
    local CHR=$1
    echo "  [$(date +'%Y-%m-%d %H:%M:%S')] Running chromosome ${CHR}..."
    
    python3 PRScsx.py \
        --ref_dir="${REF_DIR}" \
        --bim_prefix="${BIM_PREFIX}" \
        --sst_file="${SST_EUR},${SST_EAS}" \
        --n_gwas="${N_EUR},${N_EAS}" \
        --pop=EUR,EAS \
        --chrom="${CHR}" \
        --phi="${PHI}" \
        --n_iter="${N_ITER}" \
        --n_burnin="${N_BURNIN}" \
        --thin="${THIN}" \
        --meta=False \
        --out_dir="${OUT_DIR}" \
        --out_name="${OUT_NAME}" \
        2>&1 | sed "s/^/[chr${CHR}] /"
    
    echo "  [$(date +'%Y-%m-%d %H:%M:%S')] Chromosome ${CHR} completed."
}

export -f run_chr
export REF_DIR BIM_PREFIX SST_EUR SST_EAS N_EUR N_EAS OUT_DIR OUT_NAME PHI N_ITER N_BURNIN THIN

# Run all chromosomes (1-22) with parallel processing
echo "Starting Model 1 analysis across chromosomes 1-22..."
echo ""

seq 1 22 | xargs -P "${N_JOBS}" -I {} bash -c 'run_chr "$@"' _ {}

echo ""
echo "============================================"
echo "Model 1 Analysis Complete"
echo "============================================"
echo ""
echo "Output Files Generated:"
echo "  EUR weights: ${OUT_DIR}/${OUT_NAME}_EUR_pst_eff_a1_b0.5_phi${PHI}_chr*.txt"
echo "  EAS weights: ${OUT_DIR}/${OUT_NAME}_EAS_pst_eff_a1_b0.5_phi${PHI}_chr*.txt"
echo ""
echo "Next Steps:"
echo "  1. Verify output files have been generated for all chromosomes"
echo "  2. Prepare weights for PLINK scoring (concatenate chromosome files)"
echo "  3. Apply EUR and EAS weights to target validation genotypes using PLINK"
echo ""
