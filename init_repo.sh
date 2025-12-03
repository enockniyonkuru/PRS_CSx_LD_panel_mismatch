#!/bin/bash

# Initialize git repository and prepare for submission

set -e

echo "🔧 Initializing PRS-CSx Figure 4 Analysis repository..."

# Check if already a git repo
if [ -d .git ]; then
    echo "ℹ️  Repository already initialized."
else
    git init
    echo "✅ Git repository initialized"
fi

# Add all files
git add .
echo "✅ Files staged for commit"

# Initial commit
git config user.name "Your Name" || true
git config user.email "your.email@example.com" || true

git commit -m "Initial commit: PRS-CSx Figure 4 analysis pipeline" || echo "⚠️  Commit may have failed (perhaps already committed)"

echo ""
echo "📋 Repository Status:"
git log --oneline -5 || echo "No commits yet"

echo ""
echo "✨ Setup complete! Your repository is ready for submission."
echo ""
echo "Next steps:"
echo "1. Update your name/email in CONTRIBUTING.md"
echo "2. Update citation information in README.md"
echo "3. Replace sample data with your actual results CSV"
echo "4. Run: python src/generate_figure4.py --input <your_data.csv> --output outputs/Figure4.png"
echo "5. Push to a remote repository if needed"
echo ""
