# Model Specifications and Methods

## Overview

This document provides detailed specifications for each model configuration and the statistical methods used to evaluate them.

---

## Model Configurations

### Model 1: Fully Matched Baseline (M1)

**Configuration**:
```
EUR GWAS + EUR LD → EUR weights
EAS GWAS + EAS LD → EAS weights
```

**Rationale**: Gold standard—each population gets its own matched LD reference.

**Expected Performance**: Best overall; highest R² and lowest variance.

**Parameters**:
- LD reference: EUR for EUR GWAS; EAS for EAS GWAS
- Shrinkage prior (φ): 1e-2
- MCMC iterations: 1000
- Burn-in: 500
- Thinning: 5

---

### Model 2: Single-Ancestry Mismatch (M2)

**Configuration**:
```
EUR GWAS + EUR LD → EUR weights
EAS GWAS + EUR LD → EAS weights (MISMATCHED)
```

**Rationale**: Common in practice when LD reference from EAS ancestry unavailable.

**Expected Performance**: Degraded for EAS target; lower R² due to LD mismatch.

**Key Contrast**: M2 (EAS) vs M1 (EAS) demonstrates vulnerability to LD mismatch.

**Parameters**: Same as M1, except:
- LD reference: EUR for both EUR and EAS GWAS

---

### Model 3: Partial Multi-Ancestry with LD Anchor (M3)

**Configuration**:
```
EUR GWAS + {EUR, EAS} LD → EUR weights
EAS GWAS + {EUR, EAS} LD → EAS weights
```

**Rationale**: Both populations have access to matched LD; multi-ancestry LD stabilizes inference.

**Expected Performance**: Comparable to M1; robust to mismatch due to LD anchor.

**Main Hypothesis Test**: M3 (EAS) vs M2 (EAS)
- **Null hypothesis**: LD anchoring provides no benefit
- **Expected finding**: M3 >> M2 (ΔR² ≈ 0.16, p < 0.001)

**Parameters**: Same as M1

---

### Model 4: Unified Fallback (AMR LD) (M4)

**Configuration**:
```
EUR GWAS + AMR LD → EUR weights
EAS GWAS + AMR LD → EAS weights
```

**Rationale**: When matched LD unavailable, use pan-continental fallback (AMR = Americas ancestry).

**Expected Performance**: Lower than M1-M3 but better than M2 alone.

**Use Case**: Resource-limited settings where only one LD panel available.

**Parameters**: Same as M1, except:
- LD reference: AMR for both populations

---

### Model 5: Unified Fallback (SAS LD) (M5)

**Configuration**:
```
EUR GWAS + SAS LD → EUR weights
EAS GWAS + SAS LD → EAS weights
```

**Rationale**: Alternative unified fallback using SAS (South Asian) LD.

**Expected Performance**: Competitive with M1-M3 in this study (unexpectedly strong).

**Mechanism**: SAS LD structure may better capture architecture relevant to EUR and EAS.

**Parameters**: Same as M1, except:
- LD reference: SAS for both populations

---

## Statistical Methods

### Bayesian PRS Inference (MCMC)

**Method**: Continuous shrinkage prior (PRS-CSx)

**Prior Distribution**:
- Spike-and-slab: p(β_j) = (1 - π) δ(β_j) + π N(0, σ_j²)
- Shrinkage: σ_j² ~ Exponential(φ) or Inverse-Gaussian(φ)

**Posterior Inference**: Gibbs sampling MCMC
- Sample β_j from conditional posterior
- Sample τ_j (variance component)
- Update global hyperparameter

**Chain Parameters**:
- Iterations: 1,000
- Burn-in: 500 (discarded)
- Thinning: 5 (every 5th sample retained)
- Final draws: 100 posterior samples per SNP

---

### Polygenic Risk Score Calculation

**Formula**:
```
PRS_i = Σ_j (β̂_j × G_ij)
```

Where:
- β̂_j = posterior mean SNP effect
- G_ij = dosage of effect allele for individual i, SNP j
- Summation over all SNPs

**Standardization**:
```
PRS_standardized = (PRS - mean(PRS)) / sd(PRS)
```

---

### Accuracy Metric: R²

**Definition**:
```
R² = (cor(PRS, phenotype))²
```

**Interpretation**:
- Proportion of phenotypic variance explained
- Range: 0 to 1
- Higher is better

**Calculation in Practice**:
```python
# 1. Compute Pearson correlation
r = np.corrcoef(prs, phenotype)[0, 1]
# 2. Square to get R²
r2 = r ** 2
```

---

### Bootstrap Confidence Intervals (95% CI)

**Method**: Non-parametric bootstrap

**Procedure**:
1. Original sample size: N = 200 EAS individuals
2. Resample with replacement: 1,000 bootstrap samples
3. For each replicate:
   - Compute PRS
   - Fit linear regression
   - Calculate R²
4. Extract quantiles: 2.5th and 97.5th percentiles

**Code Example**:
```python
n_bootstrap = 1000
r2_samples = []

for _ in range(n_bootstrap):
    idx = np.random.choice(n_individuals, size=n_individuals, replace=True)
    prs_boot = prs[idx]
    pheno_boot = phenotype[idx]
    r2_boot = np.corrcoef(prs_boot, pheno_boot)[0, 1] ** 2
    r2_samples.append(r2_boot)

ci_lower = np.percentile(r2_samples, 2.5)
ci_upper = np.percentile(r2_samples, 97.5)
```

---

### Statistical Testing: Model Contrasts

**Contrast**: M3 vs M2 (EAS target)

**Null Hypothesis** (H₀): No difference in R²
- H₀: μ(R²_M3) = μ(R²_M2)

**Alternative Hypothesis** (H₁): M3 > M2
- H₁: μ(R²_M3) > μ(R²_M2)

**Test**: Welch's t-test (unequal variances)

**Formula**:
```
t = (R̄_M3 - R̄_M2) / √(s²_M3/n + s²_M2/n)

degrees of freedom ≈ (s²_M3/n + s²_M2/n)² / 
                     [(s²_M3/n)²/(n-1) + (s²_M2/n)²/(n-1)]
```

**Expected Result**:
- Observed ΔR² ≈ 0.1624
- t(198) ≈ 8.68
- p-value < 0.001 (highly significant)

---

### Effect Size: ΔR² (Change in Variance Explained)

**Definition**:
```
ΔR² = R²_M3 - R²_M2
```

**Interpretation**:
- Absolute improvement in variance explained
- **143% relative improvement**: (0.2758 - 0.1134) / 0.1134 ≈ 1.43

**Practical Significance**:
- Difference > 0.10 is considered substantial in PRS literature
- Observed 0.1624 is large and clinically meaningful

---

## Key Assumptions

1. **Linkage Disequilibrium Constancy**: LD structure in reference panel matches target population
2. **GWAS Validity**: Summary statistics unbiased; no hidden confounding
3. **Polygenicity**: Many variants contribute (sparse effects, continuous shrinkage justified)
4. **No Gene-by-Environment Interaction**: Across validation environments
5. **Linear Genetic Effect**: Additivity of allele effects (no dominance/epistasis)

---

## Deviations from Standard Practice

1. **Chromosome 1 Only**: Reduced computational burden; isolates LD mismatch effect
2. **5,000 SNPs**: Manageable set; demonstrates principle without whole-genome complexity
3. **Simulated Phenotypes**: Removes real-world confounders (comorbidities, linkage)
4. **Small Sample (N=200)**: Larger CIs but sufficient to detect strong contrasts

---

## References

- Ge et al. (2022). Nature Genetics 54: 1659-1667. [PRS-CSx method]
- Ge et al. (2019). Nature Communications 10: 1776. [PRS-CS method]
- Makalic & Schmidt (2016). [Inverse-Gaussian shrinkage priors]

