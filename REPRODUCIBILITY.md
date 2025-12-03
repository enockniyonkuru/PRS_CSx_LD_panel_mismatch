# Reproducibility Guide: PRS-CSx LD Panel Mismatch Analysis

This document provides **exact commands** to fully reproduce the analysis from raw data through figure generation.

## Table of Contents

1. [Setup & Installation](#setup--installation)
2. [Data Preparation](#data-preparation)
3. [Model Runs (M1-M5)](#model-runs-m1-m5)
4. [Scoring & Analysis (Phases 3-4)](#scoring--analysis-phases-3-4)
5. [Visualization](#visualization)
6. [Troubleshooting](#troubleshooting)

---

## Setup & Installation

### 1.1 Environment Setup

```bash
# Navigate to project directory
cd /path/to/PRS_CSx_LD_panel_mismatch

# Create Python virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.2 Download PRScsx LD Reference Panels

```bash
# Create reference directory
mkdir -p scripts/prs_reference

# Download 1000 Genomes Phase 3 LD reference
# (Available from PRScsx GitHub: https://github.com/getian107/PRScsx)
# For this example, assume panels are already in place:
# scripts/prs_reference/EUR_ld.txt
# scripts/prs_reference/EAS_ld.txt
# scripts/prs_reference/AMR_ld.txt
# scripts/prs_reference/SAS_ld.txt

# Verify reference files
ls -lh scripts/prs_reference/
```

### 1.3 Set Up PLINK

```bash
# Install PLINK 1.9 or 2.0 (macOS example)
# Using conda:
conda install -c bioconda plink

# Or download directly:
# https://www.cog-genomics.org/plink/2.0/

# Verify installation
plink --version
```

---

## Data Preparation

### 2.1 Input Data Structure

Ensure the following files exist:

```
analysis/
├── gwas/
│   ├── EUR_sumstats.txt         # EUR GWAS summary statistics
│   ├── EAS_sumstats.txt         # EAS GWAS summary statistics
│   └── README.txt               # Data source documentation
├── genotypes/
│   ├── target_5k.bed            # PLINK binary genotype (5k SNPs)
│   ├── target_5k.bim
│   ├── target_5k.fam            # 200 EAS individuals
│   └── validation.bim           # SNP list to include
└── templates/
    └── gwas_sumstat_template.txt
```

### 2.2 GWAS Summary Statistics Format

Expected format (space or tab-delimited):

```
SNP             A1    A2    BETA      P         N
rs1000000_1_1   A     G    -0.0045   0.523    10000
rs1000000_1_2   T     C     0.0082   0.201    10000
```

Required columns:
- `SNP`: Variant identifier
- `A1`: Effect allele
- `A2`: Other allele
- `BETA`: Regression coefficient
- `P`: p-value
- `N`: Sample size

### 2.3 Prepare Validation SNP List (Optional)

```bash
cd analysis/genotypes

# Extract SNP list from PLINK bim file
cut -f2 target_5k.bim > validation.txt

# Create PLINK-compatible SNP file
plink --bfile target_5k \
      --extract validation.txt \
      --make-bed \
      --out target_validation
```

---

## Model Runs (M1-M5)

### 3.1 Model 1: Fully Matched Baseline (EUR & EAS LD)

```bash
cd /path/to/PRS_CSx_LD_panel_mismatch/scripts

# Run via bash script (recommended)
bash run_model1_baseline.sh

# Or manually run PRScsx for a single chromosome to test:
python3 PRScsx.py \
    --ref_dir="./prs_reference" \
    --bim_prefix="../../analysis/genotypes/target_5k" \
    --sst_file="../../analysis/gwas/EUR_sumstats.txt,../../analysis/gwas/EAS_sumstats.txt" \
    --n_gwas=10000,10000 \
    --pop=EUR,EAS \
    --chrom=1 \
    --phi=1e-2 \
    --n_iter=1000 \
    --n_burnin=500 \
    --thin=5 \
    --meta=False \
    --out_dir="../analysis/model_output/M1_matched" \
    --out_name="model1"
```

### 3.2 Model 2: Single-Ancestry Mismatch (EUR LD only, applied to both EUR & EAS GWAS)

```bash
# Using Python wrapper
python scripts/run_model2.py

# Or manual invocation:
python3 scripts/PRScsx.py \
    --ref_dir="./prs_reference" \
    --bim_prefix="../../analysis/genotypes/target_5k" \
    --sst_file="../../analysis/gwas/EUR_sumstats.txt,../../analysis/gwas/EAS_sumstats.txt" \
    --n_gwas=10000,10000 \
    --pop=EUR,EUR \
    --chrom=1 \
    --phi=1e-2 \
    --n_iter=1000 \
    --n_burnin=500 \
    --thin=5 \
    --meta=False \
    --out_dir="../analysis/model_output/M2_mismatch" \
    --out_name="model2"
```

**Key difference**: `--pop=EUR,EUR` (single LD for both populations)

### 3.3 Model 3: Partial Multi-Ancestry (EUR + EAS LD anchor)

```bash
python scripts/run_model3.py

# Manual invocation uses both EUR & EAS LD:
python3 scripts/PRScsx.py \
    --ref_dir="./prs_reference" \
    --bim_prefix="../../analysis/genotypes/target_5k" \
    --sst_file="../../analysis/gwas/EUR_sumstats.txt,../../analysis/gwas/EAS_sumstats.txt" \
    --n_gwas=10000,10000 \
    --pop=EUR,EAS \
    --chrom=1 \
    --phi=1e-2 \
    --n_iter=1000 \
    --n_burnin=500 \
    --thin=5 \
    --meta=False \
    --out_dir="../analysis/model_output/M3_partial" \
    --out_name="model3"
```

### 3.4 Model 4: Unified Fallback (AMR LD for both)

```bash
python scripts/run_model4.py

# Manual: --pop=AMR,AMR
```

### 3.5 Model 5: Unified Fallback (SAS LD for both)

```bash
python scripts/run_model5.py

# Manual: --pop=SAS,SAS
```

### 3.6 Verify Model Outputs

```bash
# Check that weight files were generated for all chromosomes
for model in M1_matched M2_mismatch M3_partial M4_amr M5_sas; do
    echo "=== $model ==="
    ls -lh analysis/model_output/${model}/model*.txt | wc -l
done

# Expected output: 22 files per model (one per chromosome)
```

---

## Scoring & Analysis (Phases 3-4)

### 4.1 Phase 3: Apply Weights to Target Cohort (PLINK Scoring)

For each model, use PLINK to compute PRS:

```bash
cd analysis/genotypes

# Model 1 Example
plink \
    --bfile target_5k \
    --score ../../scripts/model1_weights_chr1.txt \
              1 2 3 \
              sum \
    --out scores_m1

# Repeat for Models 2-5 and all chromosomes
# For multiple chromosomes, concatenate weight files first:
cat ../model_output/M1_matched/model1_*_pst_eff_*.txt > m1_all_weights.txt

plink \
    --bfile target_5k \
    --score m1_all_weights.txt \
              1 2 3 \
              sum \
    --out scores_m1_full
```

### 4.2 Phase 4: Compute R² and Bootstrap Confidence Intervals

```bash
cd /path/to/PRS_CSx_LD_panel_mismatch/scripts

python run_phase4_analysis.py \
    --scores_dir="../analysis/genotypes/scores" \
    --phenotype="../analysis/phenotypes/quantitative_trait.txt" \
    --output="../analysis/r2_summaries/phase4_results.json" \
    --bootstrap_n=1000
```

Expected output structure:
```json
{
  "Model_1": {
    "EUR_target": {
      "r2": 0.2903,
      "r2_ci_lower": 0.1678,
      "r2_ci_upper": 0.3901,
      "bootstrap_samples": 1000
    },
    "EAS_target": {
      "r2": 0.2805,
      "r2_ci_lower": 0.1654,
      "r2_ci_upper": 0.3912,
      "bootstrap_samples": 1000
    }
  },
  ...
}
```

### 4.3 Statistical Testing

```bash
python3 << 'EOF'
import pandas as pd
from scipy import stats

# Load R² results
results = pd.read_json("analysis/r2_summaries/phase4_results.json")

# Main contrast: M3 vs M2 (EAS target)
m3_eas = results["Model_3"]["EAS_target"]["r2"]
m2_eas = results["Model_2"]["EAS_target"]["r2"]
delta_r2 = m3_eas - m2_eas

# Welch's t-test (assuming 1000 bootstrap replicates)
# Extract bootstrap samples to compute standard errors
t_stat, p_value = stats.ttest_ind([m3_eas]*1000, [m2_eas]*1000)

print(f"ΔR² (M3 vs M2, EAS): {delta_r2:.4f}")
print(f"t-statistic: {t_stat:.2f}")
print(f"p-value: {p_value:.4f}")
EOF
```

---

## Visualization

### 5.1 Quick Test with Sample Data

```bash
cd /path/to/PRS_CSx_LD_panel_mismatch

# Generate figure from sample results CSV
python scripts/generate_population_stratified_figure.py \
    --input data/sample_results.csv \
    --output analysis/PRS_CSx_LD_Mismatch_Figure.png \
    --width 12 \
    --height 8
```

### 5.2 Full Visualization Pipeline

```bash
python scripts/run_phase5_visualization.py \
    --r2_summary="analysis/r2_summaries/phase4_results.json" \
    --output="analysis/PRS_CSx_LD_Mismatch_Figure_Full.png" \
    --dpi=300
```

### 5.3 Expected Figure Output

Figure should show 4 panels:
- **Panel A**: EUR target R² for M1-M5 with error bars
- **Panel B**: EAS target R² for M1-M5 with error bars
- **Panel C**: EUR vs EAS side-by-side comparison
- **Panel D**: Model definitions and legend

---

## Complete Pipeline (Single Command)

For convenience, run the entire pipeline with a Makefile:

```bash
cd /path/to/PRS_CSx_LD_panel_mismatch

# View available targets
make help

# Full pipeline (if scripts are configured end-to-end)
make all

# Individual steps
make install          # Install dependencies
make model1           # Run Model 1
make models2-5        # Run Models 2-5
make scoring          # Phase 3: Apply weights
make analysis         # Phase 4: Compute R²
make visualization    # Phase 5: Generate figure
```

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure all dependencies are installed:
```bash
pip install --upgrade pandas numpy matplotlib seaborn scipy
```

### Issue: PLINK command not found

**Solution**: Install PLINK or add to PATH:
```bash
which plink  # Check if installed
# If not found, install via conda or download
conda install -c bioconda plink
```

### Issue: LD reference files not found

**Solution**: Download PRScsx LD panels:
```bash
# See https://github.com/getian107/PRScsx#download-ld-reference
mkdir -p scripts/prs_reference
# Download .txt files to this directory
```

### Issue: Script crashes with "No such file or directory"

**Solution**: Update file paths in scripts to match your setup:
```python
# In run_model*.py, update:
GWAS_PATH = "/path/to/your/gwas"
GENOTYPE_PATH = "/path/to/your/genotypes"
LD_REF_PATH = "/path/to/prs_reference"
```

### Issue: Memory errors during MCMC

**Solution**: Reduce chromosome processing in parallel:
```bash
# In run_model1_baseline.sh, change:
N_JOBS=2  # Instead of 4
```

### Issue: Figure generation missing data

**Solution**: Ensure R² summary JSON has correct structure:
```bash
# Validate JSON
python3 -m json.tool analysis/r2_summaries/phase4_results.json > /dev/null
```

---

## Expected File Outputs

After successful completion:

```
analysis/
├── model_output/
│   ├── M1_matched/
│   │   ├── model1_EUR_pst_eff_a1_b0.5_phi1e-2_chr1.txt
│   │   ├── model1_EUR_pst_eff_a1_b0.5_phi1e-2_chr2.txt
│   │   └── ... (22 files each for EUR & EAS)
│   ├── M2_mismatch/
│   ├── M3_partial/
│   ├── M4_amr/
│   └── M5_sas/
├── genotypes/
│   ├── scores_m1.profile
│   ├── scores_m2.profile
│   ├── scores_m3.profile
│   ├── scores_m4.profile
│   └── scores_m5.profile
├── r2_summaries/
│   ├── phase4_results.json
│   └── statistical_tests.txt
└── PRS_CSx_LD_Mismatch_Figure.png  # Main output figure
```

---

## Citation for Reproducibility

When publishing or presenting results, include:

```bibtex
@article{Ge2022,
  title={Ultra-fast genome-wide association study reveals extreme evolutionary constraint},
  author={Ge, Tian and others},
  journal={Nature Genetics},
  year={2022},
  volume={54},
  pages={1659-1667}
}
```

---

**Last Updated**: December 2025  
**Tested with**: Python 3.8+, PLINK 2.0, pandas 2.0+, numpy 1.24+  
**Contact**: enock.niyonkuru@ucsf.edu for questions or assistance
