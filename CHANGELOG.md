# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-12-03

### Project Title
**PRS-CSx LD Panel Mismatch Analysis**: Evaluating multi-ancestry polygenic risk score robustness under linkage disequilibrium reference panel mismatch.

### Added
- Complete analysis pipeline for evaluating 5 PRS-CSx model configurations (M1-M5)
- M1: Fully matched baseline (EUR & EAS LD)
- M2: Single-ancestry mismatch (EUR LD only) - demonstrates vulnerability
- M3: Partial multi-ancestry with LD anchor - core hypothesis test
- M4: Unified fallback using AMR LD
- M5: Unified fallback using SAS LD
- All analysis scripts (PRScsx core + model runners)
- Population-stratified figure generation
- Comprehensive reproducibility documentation
- Statistical testing framework (bootstrap, t-tests, confidence intervals)
- MIT License and contributing guidelines

### Key Results
- **Main Finding**: ΔR² = 0.1624 (143% improvement, M3 vs M2, p < 0.001)
- EUR target (M1): R² = 0.2903 [95% CI: 0.1678-0.3901]
- EAS target (M1): R² = 0.2805 [95% CI: 0.1654-0.3912]
- EAS target (M2, mismatched): R² = 0.1134 [95% CI: 0.0246-0.1970]
- M5 (SAS fallback) competitive or superior to matched baseline in EUR

### Scope
- **Chromosomes**: Chromosome 1 only (computational efficiency)
- **SNPs**: 5,000 SNPs per population
- **Sample Size**: 10,000 EUR GWAS, 10,000 EAS GWAS, 200 EAS targets
- **Populations**: EUR (European), EAS (East Asian)
- **LD Panels**: EUR, EAS, AMR (Americas), SAS (South Asian) from 1000 Genomes Phase 3

### Scripts Included
- `PRScsx.py` - Core Bayesian PRS inference (MCMC)
- `run_model1_baseline.sh` - Model 1 inference
- `run_model2.py, run_model3.py, run_model4.py, run_model5.py` - Model 2-5 inference
- `run_phase3_scoring.py` - Apply weights to target genotypes
- `run_phase4_analysis.py` - Compute R² with bootstrap CIs
- `run_phase5_visualization.py` - Generate publication figure
- `generate_population_stratified_figure.py` - Standalone figure utility
- Supporting utilities: `parse_genet.py`, `mcmc_gtb.py`, `gigrnd.py`

### Documentation
- README.md: Overview, methods, external dependencies (PRScsx, PRScs, PLINK)
- REPRODUCIBILITY.md: Step-by-step commands to recreate full analysis
- docs/model_definitions.md: Detailed model specs, statistical methods, assumptions
- LICENSE: MIT license for academic use

### External Dependencies Documented
- **PRS-CSx** (https://github.com/getian107/PRScsx): Multi-ancestry Bayesian PRS
- **PRS-CS** (https://github.com/getian107/PRScs): Single-ancestry baseline
- **PLINK-NG** (https://github.com/chrchang/plink-ng): Genotype QC and scoring
- **1000 Genomes Phase 3**: LD reference panels

### Testing & Validation
- Sample data provided for quick validation (data/sample_results.csv)
- Generate figure in <1 minute with sample data
- All scripts include error checking and logging
- Makefile provides convenient command shortcuts

