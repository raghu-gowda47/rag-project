# Git Setup Guide

## Prerequisites

1. **Git installed**: Download from https://git-scm.com/
2. **GitHub account**: Create one at https://github.com/signup

## Step-by-Step Setup

### 1. Initialize Git Repository (First Time Only)

If you haven't initialized Git yet, run:

```bash
cd "Rag Project"
git init
```

### 2. Configure Git User (First Time Only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Replace with your actual name and email.

### 3. Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `rag-project` (or your preferred name)
3. **Do NOT** initialize with README (we already have one)
4. Click "Create repository"

### 4. Add Remote and Push Code

Copy the repository URL from GitHub, then run:

```bash
cd "Rag Project"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/rag-project.git

# Rename branch to main (if needed)
git branch -M main

# Stage all files
git add .

# Create first commit
git commit -m "Initial commit: RAG chatbot with Langfuse observability"

# Push to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### 5. Verify on GitHub

Go to your repository URL and refresh the page. You should see all your files!

## What Gets Ignored (Won't Be Uploaded)

The `.gitignore` file prevents these from being uploaded:

- ❌ `chroma_db/` and `chroma_db_bpe/` (vector databases—can be regenerated)
- ❌ `.env` (sensitive credentials—use `.env.example` instead)
- ❌ `__pycache__/` (Python cache files)
- ❌ `.venv/` (virtual environment)
- ❌ `rag_chatbot.log` (log files)
- ❌ `.pdf_checkpoint` (checkpoint file—regenerates on first run)

## What Gets Uploaded

The following files **will** be in your GitHub repository:

✅ `src/` (all source code)
✅ `requirements.txt` (dependencies)
✅ `README.md` (documentation)
✅ `.env.example` (template for credentials)
✅ `Dockerfile` (containerization)
✅ `LANGFUSE_SETUP.md` (setup guide)
✅ All configuration files

**Note:** `Ramayana.pdf` will be uploaded (155 MB). If you want to exclude large files:

```bash
echo "Ramayana.pdf" >> .gitignore
git rm --cached Ramayana.pdf  # Remove from Git history if already added
```

## Updating After First Commit

After the initial push, use these commands to update:

```bash
# Make changes to your files, then:
git add .
git commit -m "Your commit message"
git push origin main
```

## Useful Git Commands

```bash
# Check status
git status

# View commit history
git log --oneline

# See what changed
git diff

# Undo last commit (but keep changes)
git reset --soft HEAD~1

# Remove file from Git (but keep locally)
git rm --cached filename
```

## Best Practices

1. **Commit frequently**: Make small, logical commits with clear messages
2. **Write good messages**: 
   - ✅ `"Add PDF change detection with checkpoint tracking"`
   - ❌ `"fixed stuff"`
3. **Never commit secrets**: Always use `.env.example` template
4. **Pull before pushing**: `git pull origin main` before `git push`

## Troubleshooting

### "fatal: could not read username"
- You haven't configured Git. Run: `git config --global user.name "Your Name"`

### "Everything up-to-date" when pushing
- All changes are already committed. Make a new change and commit again.

### Large file warnings
- The `Ramayana.pdf` file is large (~155 MB). Consider:
  - Using Git LFS (Large File Storage)
  - Or excluding it with `.gitignore`

### Permission denied
- Check if you have SSH key set up or use HTTPS instead of SSH

## Environment Variables for Production

Your `.env.example` template includes:
```
LANGFUSE_PUBLIC_KEY=your_key_here
LANGFUSE_SECRET_KEY=your_secret_here
```

Users cloning your repo should:
1. Copy `.env.example` to `.env`
2. Fill in their own credentials
3. Never commit `.env` (it's in `.gitignore`)

## Next Steps

1. ✅ Set up Git locally (this guide)
2. ✅ Push to GitHub
3. 📝 Add a GitHub Actions CI/CD pipeline (optional)
4. 📝 Add Git branch protection rules (optional)
5. 📝 Enable GitHub Issues for tracking bugs (optional)

## Questions?

- Git docs: https://git-scm.com/doc
- GitHub guides: https://guides.github.com/
- This README: See the "Installation & Running" section for how others will use your project
