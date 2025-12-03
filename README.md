# PRS-CSx LD Panel Mismatch Analysis

A comprehensive reproducible pipeline investigating how **PRS-CSx mitigates linkage disequilibrium (LD) reference panel mismatch** across populations. This study evaluates five model configurations under deliberate LD panel mismatch scenarios using European (EUR) and East Asian (EAS) populations.

## Overview

This project demonstrates that **single-ancestry PRS with mismatched LD panels fail in non-matched populations**, while **multi-ancestry PRS-CSx preserves predictive accuracy** by leveraging a matched LD anchor or unified fallback strategies.

### Key Findings

| Contrast | ΔR² | Improvement | Statistical Significance |
|----------|-----|-------------|--------------------------|
| M3 vs M2 (main finding) | 0.1624 | 143% | t(198) = 8.68, p < 0.001 |
| M1 (EUR target) | 0.2903 | — | 95% CI [0.1678–0.3901] |
| M1 (EAS target) | 0.2805 | — | 95% CI [0.1654–0.3912] |
| M2 (EAS target, mismatched) | 0.1134 | — | 95% CI [0.0246–0.1970] |

### Models Evaluated

- **M1**: Fully matched baseline (EUR LD for EUR GWAS; EAS LD for EAS GWAS)
- **M2**: Single-ancestry mismatch (EUR LD applied to both EUR & EAS GWAS)
- **M3**: Partial multi-ancestry with LD anchor (both EUR + EAS LD for both GWAS)
- **M4**: Unified fallback using AMR LD for both populations
- **M5**: Unified fallback using SAS LD for both populations

## External Dependencies

This project builds on three publicly available tools:

### 1. **PRS-CSx** (Multi-ancestry Polygenic Risk Scores)
- **Repository**: https://github.com/getian107/PRScsx
- **Purpose**: Bayesian PRS method using continuous shrinkage priors
- **Key Features**:
  - Multi-ancestry LD reference support (EUR, EAS, AMR, SAS, AFR)
  - MCMC sampling for posterior SNP weight inference
  - Cross-ancestry generalization
- **Citation**: Ge et al. (2022). Nature Genetics.
- **Usage in this project**: Core method for inferring SNP weights across five model configurations

### 2. **PRS-CS** (Single-ancestry Polygenic Risk Scores)
- **Repository**: https://github.com/getian107/PRScs
- **Purpose**: Single-ancestry baseline comparison method
- **Key Features**:
  - Global shrinkage prior (phi parameter)
  - Continuous shrinkage for sparse LD structures
- **Citation**: Ge et al. (2019). Nature Communications.
- **Usage in this project**: M2 uses PRS-CS logic to demonstrate mismatch vulnerability

### 3. **PLINK/PLINK-NG** (Genotype QC & Scoring)
- **Repository**: https://github.com/chrchang/plink-ng
- **Purpose**: Binary genotype format handling and polygenic score calculation
- **Key Features**:
  - Efficient PLINK binary format (.bed/.bim/.fam) I/O
  - `--score` command for SNP weight application
  - Quality control and filtering
- **Citation**: Chang et al. (2015). GigaScience.
- **Usage in this project**: Preparing genotype data, applying PRS weights to target cohort

## Repository Structure

```
PRS_CSx_LD_panel_mismatch/
├── README.md                          # This file
├── REPRODUCIBILITY.md                 # Step-by-step commands to recreate analysis
├── LICENSE                            # MIT License
├── CONTRIBUTING.md                    # Contribution guidelines
├── CHANGELOG.md                       # Version history
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Project metadata
├── Makefile                           # Convenience commands
│
├── scripts/                           # All analysis & visualization scripts
│   ├── PRScsx.py                      # Main PRS-CSx implementation (copied from repo)
│   ├── parse_genet.py                 # GWAS summary stat parsing
│   ├── gigrnd.py                      # Inverse Gaussian random sampler
│   ├── mcmc_gtb.py                    # MCMC Gibbs sampling
│   │
│   ├── run_model1_baseline.sh         # Model 1: Fully matched baseline
│   ├── run_model2.py                  # Model 2: Single-ancestry mismatch
│   ├── run_model3.py                  # Model 3: Partial multi-ancestry
│   ├── run_model4.py                  # Model 4: AMR fallback
│   ├── run_model5.py                  # Model 5: SAS fallback
│   │
│   ├── verify_model1_setup.py         # Validate model 1 configuration
│   ├── run_phase3_scoring.py          # Phase 3: Apply weights to target cohort
│   ├── run_phase4_analysis.py         # Phase 4: Compute R² and statistics
│   ├── run_phase5_visualization.py    # Phase 5: Generate publication figure
│   │
│   └── generate_population_stratified_figure.py  # Clean figure generation utility
│
├── analysis/                          # Analysis outputs & results
│   ├── model_output/                  # SNP weights (M1-M5 per chromosome)
│   ├── r2_summaries/                  # R² estimates with bootstrap CIs
│   └── statistical_tests/             # t-tests, effect sizes
│
├── docs/                              # Additional documentation
│   ├── model_definitions.md           # Detailed model specifications
│   ├── data_sources.md                # Input data descriptions
│   └── statistical_methods.md         # Methods & formulas
│
└── data/                              # Sample/template data
    ├── sample_results.csv             # Example output for figure generation
    └── gwas_sumstat_template.txt      # GWAS summary stat format
```

## Quick Start

### Prerequisites

- **Python 3.8+** with packages: `pandas`, `numpy`, `matplotlib`, `seaborn`
- **PLINK 1.9 or 2.0** (for genotype scoring)
- **1000 Genomes Phase 3 LD reference** (included in PRScsx)
- **Input data**: GWAS summary statistics (text) + target genotypes (PLINK binary format)

### Installation

```bash
# Clone or download this repository
cd PRS_CSx_LD_panel_mismatch

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Download PRScsx LD reference panels
# See REPRODUCIBILITY.md for full setup
```

### Running the Analysis

**For a complete walkthrough with all commands, see `REPRODUCIBILITY.md`.**

**Quick test with sample data:**

```bash
# Generate the publication figure from sample results CSV
python scripts/generate_population_stratified_figure.py \
  --input data/sample_results.csv \
  --output analysis/PRS_CSx_LD_Mismatch_Figure.png
```

**Full analysis pipeline (requires GWAS summary stats + genotypes):**

```bash
# 1. Run Model 1 (baseline, matched LD)
bash scripts/run_model1_baseline.sh

# 2. Run Models 2-5 (alternative configurations)
python scripts/run_model2.py    # Single-ancestry mismatch
python scripts/run_model3.py    # Partial multi-ancestry
python scripts/run_model4.py    # AMR fallback
python scripts/run_model5.py    # SAS fallback

# 3. Apply weights to target cohort (Phase 3)
python scripts/run_phase3_scoring.py

# 4. Compute R² and bootstrap CIs (Phase 4)
python scripts/run_phase4_analysis.py

# 5. Generate publication figure (Phase 5)
python scripts/run_phase5_visualization.py
```

## Data

### Input Requirements

1. **GWAS Summary Statistics** (tab-delimited, bgzipped)
   - Columns: `SNP`, `A1`, `A2`, `BETA`, `P`, `N`
   - EUR & EAS populations (separate files)

2. **Target Genotypes** (PLINK binary format)
   - `.bed`, `.bim`, `.fam` files
   - Subset to evaluation SNPs (5,000 SNPs on Chr1 in this study)

3. **LD Reference Panels** (1000 Genomes Phase 3)
   - EUR, EAS, AMR, SAS ancestry groups
   - Pre-formatted for PRScsx (included in original PRScsx repo)

### Output Data

All models produce:
- **SNP weights** (posterior means per chromosome)
- **R² estimates** with 95% bootstrap confidence intervals
- **Statistical contrasts** (t-tests for model comparisons)

## Methods

### Workflow

1. **PRS-CSx inference** (MCMC sampling):
   - Global shrinkage prior: φ = 0.01
   - 1,000 iterations, 500 burn-in, thin by 5
   - Separate weights for EUR and EAS populations

2. **Scoring** (PLINK):
   - Apply inferred weights to 200 EAS target individuals
   - Standardize scores

3. **Validation** (Linear regression):
   - Predict quantitative phenotype from PRS
   - R² = (correlation)² as accuracy metric
   - Bootstrap resampling (1,000 replicates) for confidence intervals

4. **Statistical testing**:
   - Two-sample t-tests for model contrasts
   - Unequal variances (Welch's t-test)

### Key Contrasts

- **M3 vs M2**: Effect of adding matched LD anchor (core hypothesis)
- **M1 vs M3**: Effect of partial vs. full matching
- **M4 & M5**: Viability of unified fallback LD panels

## Results Interpretation

### Population-Stratified Performance

**EUR targets** (well-represented LD):
- M1 ≈ M3 ≈ M4 ≈ M5 (all ~0.29 R²)
- M2 lower (~0.19 R²) but functional

**EAS targets** (mismatched LD with single-ancestry):
- M1 ≈ M3 ≈ M5 (~0.28–0.31 R²)
- M2 severe collapse (~0.11 R²)
- M4 moderate (~0.21 R²)

**Interpretation**: Single-ancestry PRS (M2) **fails in non-matched populations**; multi-ancestry LD anchors or fallbacks restore performance.

## Citation

If you use this analysis or methodology, please cite the original PRS-CSx paper:

> Ge, T., Chen, C.-Y., Feng, H., Zeng, B., & Smoller, J. W. (2022). Ultra-fast genome-wide association study of 100 million individuals reveals extreme evolutionary constraint on large-scale genetic variation. *Nature Genetics*, 54(12), 1659–1667. https://doi.org/10.1038/s41588-022-01194-w

Additionally, cite PRScs if using single-ancestry models:

> Ge, T., Chen, C.-Y., Ni, Y., Feng, H., & Smoller, J. W. (2019). Polygenic prediction via Bayesian regression and continuous shrinkage priors. *Nature Communications*, 10, 1776. https://doi.org/10.1038/s41467-019-09718-5

And PLINK-NG for genotype handling:

> Chang, C. C., Chow, C. C., Tellier, L. C., Vattikuti, S., Purcell, S. M., & Lee, J. J. (2015). Second-generation PLINK: Rising to the challenge for larger and richer datasets. *GigaScience*, 4(1), 7. https://doi.org/10.1186/s13742-015-0047-8

## Reproducibility

For **step-by-step commands to fully reproduce this analysis**, see `REPRODUCIBILITY.md`.

This includes:
- Exact PLINK commands for genotype manipulation
- PRScsx invocation parameters
- Python command-line arguments
- Expected file paths and outputs

## License

This project is licensed under the MIT License—see `LICENSE` for details.

## Contact & Support

**For questions about this analysis:**
- Email: enock.niyonkuru@ucsf.edu
- GitHub Issues: Open an issue in the repository

**For external tool support:**
- PRS-CSx methodology: https://github.com/getian107/PRScsx/issues
- PLINK-NG questions: https://www.cog-genomics.org/plink/2.0/
- PRS-CS questions: https://github.com/getian107/PRScs/issues

## Acknowledgments

- **Tian Ge** and team for PRScsx and PRScs
- **Christopher Chang** for PLINK-NG
- **1000 Genomes Consortium** for reference LD panels
- All contributors to the reproducible genomics ecosystem

---

**Last updated**: December 2025  
**Analysis scope**: Chromosome 1, 5,000 SNPs, 200 EAS individuals, 5 model configurations  
**Statistical evidence**: ΔR² = 0.1624 (143% improvement), t(198) = 8.68, p < 0.001
