# Getting Started

This guide walks you through setting up and using the PRS-CSx Figure 4 Analysis repository for submission.

## Step 1: Install Dependencies

```bash
cd /Users/enockniyonkuru/Desktop/Biostats/Project/assignment/PRS-CSx-Figure4-Analysis

# Install required packages
pip install -r requirements.txt
```

Or using Make:
```bash
make install
```

## Step 2: Generate Figure 4

### Option A: Using Sample Data (Quick Test)

```bash
python src/generate_figure4.py \
  --input data/sample_results.csv \
  --output outputs/Figure4_PopulationStratified_Extended.png
```

Or with Make:
```bash
make generate
```

### Option B: Using Your Own Data

First, prepare your data as a CSV with columns:
- `population`: EUR, EAS (or other)
- `model`: M1, M2, M3, M4, M5
- `r2`: variance explained
- `r2_low`: lower 95% CI bound
- `r2_high`: upper 95% CI bound

Then run:
```bash
python src/generate_figure4.py \
  --input path/to/your/results.csv \
  --output outputs/your_figure.png
```

### Options & Customization

Adjust figure size:
```bash
python src/generate_figure4.py \
  --input data/sample_results.csv \
  --output outputs/Figure4.png \
  --width 14 --height 9
```

Get help:
```bash
python src/generate_figure4.py --help
```

## Step 3: Initialize Git & Prepare for Submission

```bash
bash init_repo.sh
```

This will:
- Initialize a git repository
- Stage all files
- Create an initial commit

## Step 4: Customize for Your Submission

Edit these files:

### README.md
- Update citation information at the bottom
- Add any additional context about your analysis

### CONTRIBUTING.md
- Replace "Assignment Author" with your name
- Update email if needed

### src/generate_figure4.py
- Adjust colors, fonts, or layout if needed
- Modify model definitions in `MODEL_DEFS`

## File Structure

```
PRS-CSx-Figure4-Analysis/
├── README.md                  # Main documentation
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # Contribution guidelines
├── CHANGELOG.md               # Version history
├── Makefile                   # Convenient commands
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project metadata
├── init_repo.sh              # Git initialization
├── src/
│   └── generate_figure4.py   # Main script
├── data/
│   └── sample_results.csv    # Example input
└── outputs/                   # Generated figures
```

## Common Tasks

### Generate & View Figure
```bash
make generate
open outputs/Figure4_PopulationStratified_Extended.png
```

### Format & Lint Code
```bash
make format    # Auto-format with black
make lint      # Check style with flake8
```

### Clean Generated Files
```bash
make clean
```

### View All Available Commands
```bash
make help
```

## Reproducibility Checklist

- [ ] Installed all dependencies (`requirements.txt`)
- [ ] Generated Figure 4 with your data
- [ ] Verified output PNG looks correct
- [ ] Updated README with citation information
- [ ] Customized author information
- [ ] Run `init_repo.sh` to initialize git
- [ ] All changes committed to git

## Troubleshooting

### "python: command not found"
Use `python3` instead:
```bash
python3 src/generate_figure4.py --input data/sample_results.csv --output outputs/Figure4.png
```

### Missing CSV columns
Ensure your CSV has exactly these columns:
```
population,model,r2,r2_low,r2_high
EUR,M1,0.29,0.16,0.39
...
```

### Import errors
Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### Permission denied on init_repo.sh
Make it executable:
```bash
chmod +x init_repo.sh
./init_repo.sh
```

## Support

For questions or issues:
1. Check the README.md for detailed documentation
2. Review CONTRIBUTING.md for guidelines
3. Inspect `src/generate_figure4.py` for implementation details
4. Examine `data/sample_results.csv` for the expected data format

---

**Ready to submit?** Ensure all files are committed and push to your assignment repository!
