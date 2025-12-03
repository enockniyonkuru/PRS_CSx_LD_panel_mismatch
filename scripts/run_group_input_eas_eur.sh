#!/usr/bin/env bash
set -euo pipefail

#############################################
# Run PRScsx with group_input data
# Using only EAS and EUR populations (AFR reference not available)
#############################################

# Reference directory
REF_DIR="./prs_reference"

# BIM prefix (using test data for validation)
BIM_PREFIX="test_data/test"

# GWAS summary statistics from group_input (only EAS and EUR)
SST_EAS="group_input/EAS_sumstats.txt"
SST_EUR="group_input/EUR_sumstats.txt"

# Sample sizes (placeholder values - adjust if you know the actual sample sizes)
N_EAS="10000"
N_EUR="10000"

# Output folder/prefix
OUT_DIR="group_output"
OUT_NAME="group_run_eas_eur"

# Global shrinkage parameter
PHI="1e-2"

# Parallel settings
N_JOBS=4

# Limit math libraries to avoid oversubscribing cores
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1

#############################################
# RUN PRS-CSx (META) ACROSS CHR 1–22
#############################################
mkdir -p "${OUT_DIR}"

echo "Starting PRScsx with group_input data..."
echo "Populations: EAS, EUR (AFR reference not available)"
echo "Output directory: ${OUT_DIR}"
echo ""
echo "NOTE: The SNP IDs in your data (SNP_1, SNP_2, etc.) don't match"
echo "      the reference panel SNP IDs (rs IDs). This will result in"
echo "      0 common SNPs and no output. You need to either:"
echo "      1. Update your SNP IDs to match rs IDs, or"
echo "      2. Use a different reference panel that matches your data"
echo ""

# Run for all chromosomes with parallelization
jobcount=0
for chr in {1..22}; do
  echo "Processing chromosome ${chr}..."
  python PRScsx.py \
    --ref_dir="${REF_DIR}" \
    --bim_prefix="${BIM_PREFIX}" \
    --sst_file="${SST_EAS},${SST_EUR}" \
    --n_gwas="${N_EAS},${N_EUR}" \
    --pop=EAS,EUR \
    --chrom="${chr}" \
    --phi="${PHI}" \
    --meta=True \
    --out_dir="${OUT_DIR}" \
    --out_name="${OUT_NAME}" &

  jobcount=$((jobcount+1))
  if [ $jobcount -ge $N_JOBS ]; then
    wait
    jobcount=0
  fi
done
wait

echo ""
echo "✔ PRScsx finished for chromosomes 1-22"

#############################################
# CONCATENATE PER-CHR FILES → ONE WEIGHTS FILE
#############################################
echo ""
echo "Concatenating results..."

META_WEIGHTS="${OUT_DIR}/${OUT_NAME}_META_weights.txt"
if ls ${OUT_DIR}/${OUT_NAME}_META_pst_eff_a1_b0.5_phi${PHI}_chr*.txt >/dev/null 2>&1; then
  cat ${OUT_DIR}/${OUT_NAME}_META_pst_eff_a1_b0.5_phi${PHI}_chr*.txt > "${META_WEIGHTS}"
  echo "✔ Concatenated meta weights → ${META_WEIGHTS}"
else
  echo "⚠ No META output files found (likely due to SNP ID mismatch)"
fi

# Population-specific weights
EAS_WEIGHTS="${OUT_DIR}/${OUT_NAME}_EAS_weights.txt"
EUR_WEIGHTS="${OUT_DIR}/${OUT_NAME}_EUR_weights.txt"

if ls ${OUT_DIR}/${OUT_NAME}_EAS_pst_eff_a1_b0.5_phi${PHI}_chr*.txt >/dev/null 2>&1; then
  cat ${OUT_DIR}/${OUT_NAME}_EAS_pst_eff_a1_b0.5_phi${PHI}_chr*.txt > "${EAS_WEIGHTS}"
  echo "✔ EAS weights → ${EAS_WEIGHTS}"
fi

if ls ${OUT_DIR}/${OUT_NAME}_EUR_pst_eff_a1_b0.5_phi${PHI}_chr*.txt >/dev/null 2>&1; then
  cat ${OUT_DIR}/${OUT_NAME}_EUR_pst_eff_a1_b0.5_phi${PHI}_chr*.txt > "${EUR_WEIGHTS}"
  echo "✔ EUR weights → ${EUR_WEIGHTS}"
fi

echo ""
echo "All done! Output files are in ${OUT_DIR}/"
echo ""
echo "IMPORTANT: Your data has SNP IDs like 'SNP_1', 'SNP_2', etc."
echo "           but the reference panel expects rs IDs like 'rs12345'."
echo "           This mismatch means no SNPs were processed."
echo ""
echo "To fix this, you need to map your SNP IDs to rs IDs based on"
echo "chromosome and position information."
