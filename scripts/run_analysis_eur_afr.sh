#!/usr/bin/env bash

#############################################
# PRScsx Analysis Plan 2: EUR + AFR
# Populations: EUR and AFR
# Output: EUR and AFR specific weights + META weights
#############################################

set -euo pipefail

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_ROOT"

# Configuration
REF_DIR="./prs_reference"
BIM_PREFIX="test_data/test"

# GWAS summary statistics
SST_EUR="group_input/EUR_sumstats.txt"
SST_AFR="group_input/AFR_sumstats.txt"

# Sample sizes (update if you know actual values)
N_EUR="10000"
N_AFR="10000"

# Output settings
OUT_DIR="results_eur_afr"
OUT_NAME="eur_afr"
PHI="1e-2"
N_JOBS=4

# Setup environment
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1

mkdir -p "$OUT_DIR"

echo "=================================================="
echo "PRScsx Analysis 2: EUR + AFR Multi-Population PRS"
echo "=================================================="
echo ""
echo "Input:"
echo "  EUR summary stats: $(wc -l < "$SST_EUR") SNPs"
echo "  AFR summary stats: $(wc -l < "$SST_AFR") SNPs"
echo ""
echo "Reference panels:"
echo "  EUR: prs_reference/ldblk_1kg_eur/"
echo "  AFR: prs_reference/ldblk_1kg_afr/"
echo ""
echo "Output directory: $OUT_DIR"
echo "Output prefix: $OUT_NAME"
echo ""
echo "Running PRScsx for chromosomes 1-22..."
echo ""

jobcount=0
for chr in {1..22}; do
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Processing chromosome ${chr}..."
  
  python3 PRScsx.py \
    --ref_dir="$REF_DIR" \
    --bim_prefix="$BIM_PREFIX" \
    --sst_file="$SST_EUR,$SST_AFR" \
    --n_gwas="$N_EUR,$N_AFR" \
    --pop=EUR,AFR \
    --chrom="$chr" \
    --phi="$PHI" \
    --meta=True \
    --out_dir="$OUT_DIR" \
    --out_name="$OUT_NAME" &
  
  jobcount=$((jobcount+1))
  if [ $jobcount -ge $N_JOBS ]; then
    wait
    jobcount=0
  fi
done
wait

echo ""
echo "✓ PRScsx completed for all chromosomes"
echo ""
echo "=================================================="
echo "Post-processing: Concatenating results..."
echo "=================================================="
echo ""

# Concatenate META weights
META_WEIGHTS="${OUT_DIR}/${OUT_NAME}_META_weights.txt"
if ls ${OUT_DIR}/${OUT_NAME}_META_pst_eff_a1_b0.5_phi${PHI}_chr*.txt 1>/dev/null 2>&1; then
  cat ${OUT_DIR}/${OUT_NAME}_META_pst_eff_a1_b0.5_phi${PHI}_chr*.txt > "$META_WEIGHTS"
  echo "✓ META weights: $META_WEIGHTS ($(wc -l < "$META_WEIGHTS") SNPs)"
else
  echo "⚠ No META weights found"
fi

# Concatenate EUR weights
EUR_WEIGHTS="${OUT_DIR}/${OUT_NAME}_EUR_weights.txt"
if ls ${OUT_DIR}/${OUT_NAME}_EUR_pst_eff_a1_b0.5_phi${PHI}_chr*.txt 1>/dev/null 2>&1; then
  cat ${OUT_DIR}/${OUT_NAME}_EUR_weights.txt > "$EUR_WEIGHTS"
  echo "✓ EUR weights: $EUR_WEIGHTS ($(wc -l < "$EUR_WEIGHTS") SNPs)"
else
  echo "⚠ No EUR weights found"
fi

# Concatenate AFR weights
AFR_WEIGHTS="${OUT_DIR}/${OUT_NAME}_AFR_weights.txt"
if ls ${OUT_DIR}/${OUT_NAME}_AFR_pst_eff_a1_b0.5_phi${PHI}_chr*.txt 1>/dev/null 2>&1; then
  cat ${OUT_DIR}/${OUT_NAME}_AFR_pst_eff_a1_b0.5_phi${PHI}_chr*.txt > "$AFR_WEIGHTS"
  echo "✓ AFR weights: $AFR_WEIGHTS ($(wc -l < "$AFR_WEIGHTS") SNPs)"
else
  echo "⚠ No AFR weights found"
fi

echo ""
echo "=================================================="
echo "Analysis 2 Complete!"
echo "=================================================="
echo ""
echo "Output files in: $OUT_DIR/"
echo ""
echo "To calculate PRS for your study samples:"
echo "  plink --bfile YOUR_DATA --score $META_WEIGHTS 2 4 6 header sum --out prs_eur_afr"
echo ""
