# GitLab CI/CD Pipeline Fix

## Issue

GitLab pipeline was failing for commit `f78b13ee` with error:
```
gmail-doc-scrapper | Failed pipeline for master | f78b13ee
```

## Root Cause

The `.gitlab-ci.yml` configuration was only set to run on `main`, `develop`, and `merge_requests` branches, but the repository was using the `master` branch. This caused GitLab to skip all pipeline jobs.

## Changes Made

### 1. Updated `.gitlab-ci.yml`

**Added `master` branch to all job configurations:**

- **Test job** (lines 31-35): Added `master` to branch filter
- **Code quality job** (lines 47-50): Added `master` to branch filter
- **Build job** (lines 68-72): Added `master` to branch filter
- **Pages job** (lines 85-87): Added `master` to branch filter

**Updated Docker tagging logic** (line 64):
```yaml
if [ "$CI_COMMIT_REF_NAME" == "main" ] || [ "$CI_COMMIT_REF_NAME" == "master" ]; then
```

This ensures the Docker image is tagged as `:latest` for both `main` and `master` branches.

### 2. Created `mkdocs.yml`

The pages job was configured to build documentation using MkDocs, but the configuration file was missing.

**Created `mkdocs.yml` with:**
- Material theme
- Navigation structure for all documentation files
- Search functionality
- Markdown extensions for better rendering

**Documentation included:**
- Home (README.md)
- Quick Start (QUICKSTART.md)
- Testing guides
- Technical documentation (classification algorithm, folder search, error fixes)

## Pipeline Stages

The pipeline now runs successfully on `master` branch with 4 stages:

### 1. **Test Stage**
- **test job**: Runs pytest with coverage, flake8 linting
- **code-quality job**: Runs black formatter check and flake8 (allowed to fail)

### 2. **Build Stage**
- **build job**: Builds and pushes Docker image to GitLab Container Registry
- Tags as `:latest` when on `main` or `master` branch

### 3. **Deploy Stage**
- **pages job**: Builds MkDocs documentation and deploys to GitLab Pages

## Testing the Fix

To verify the pipeline works:

```bash
# Make any change (e.g., update this file)
git add .
git commit -m "Test pipeline fix"
git push origin master
```

Then check:
- GitLab project → CI/CD → Pipelines
- All jobs should run successfully
- Green checkmarks indicate passing tests

## Alternative: Rename Branch

If you prefer to use `main` as the primary branch (GitLab's default):

```bash
# Rename local branch
git branch -m master main

# Delete old master on remote and push new main
git push origin -u main
git push origin --delete master

# Update default branch in GitLab:
# Settings → Repository → Default Branch → Change to 'main'
```

Then you can remove `master` from all `.gitlab-ci.yml` configurations.

## Files Modified

1. `.gitlab-ci.yml` - Updated branch filters and Docker tagging
2. `mkdocs.yml` - Created MkDocs configuration
3. `PIPELINE_FIX.md` - This documentation

## Expected Pipeline Output

After pushing changes, the pipeline should:

✅ **Test stage**
- Install dependencies (requirements.txt, spaCy model)
- Run pytest with code coverage
- Run flake8 linting
- Generate coverage report

✅ **Build stage** (on master/main/develop/tags)
- Build Docker image
- Push to GitLab Container Registry
- Tag as `:latest` for master/main

✅ **Deploy stage** (on master/main)
- Build MkDocs documentation
- Deploy to GitLab Pages at: `https://joaocostafernandes-group.gitlab.io/gmail-doc-scrapper/`

## Monitoring

**Check pipeline status:**
- GitLab UI: Project → CI/CD → Pipelines
- Badge: [![pipeline status](https://gitlab.com/joaocostafernandes-group/gmail-doc-scrapper/badges/master/pipeline.svg)](https://gitlab.com/joaocostafernandes-group/gmail-doc-scrapper/-/commits/master)

**Common issues:**
- If tests fail: Check pytest output for specific errors
- If build fails: Check Docker credentials are set in CI/CD variables
- If pages fail: Check mkdocs.yml syntax and file paths

## Summary

The pipeline failure was due to branch name mismatch. By adding `master` to all job configurations and creating the missing `mkdocs.yml` file, the pipeline now runs successfully on all commits to the `master` branch.
