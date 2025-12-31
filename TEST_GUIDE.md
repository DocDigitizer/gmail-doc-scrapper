# Gmail Document Scraper - Test Guide

Quick guide to test the Gmail Document Scraper before using it with real credentials.

## Prerequisites

- Python 3.9+ installed ✓ (You have Python 3.13.9)
- Gmail account with App Password configured
- Internet connection

## Step 1: Install Dependencies

```bash
cd C:\Users\jcfernandes\Desktop\gmail-doc-scrapper

# Install required packages
pip install -r requirements.txt

# Download spaCy Portuguese model (for document classification)
python -m spacy download pt_core_news_lg
```

**Expected output**: All packages install successfully without errors.

---

## Step 2: Test Python Syntax (No credentials needed)

```bash
# Test that all Python files are valid
python -m py_compile main.py
python -m py_compile src/*.py

# Show help menu
python main.py --help
```

**Expected output**: Help menu showing all available options including `--interactive`.

---

## Step 3: Test Interactive Mode (Dry Run)

This tests the interactive prompts WITHOUT connecting to Gmail:

```bash
python main.py --interactive
```

**Interactive prompts will ask you:**

1. **Gmail email**: Enter any email (e.g., `test@gmail.com`)
2. **Gmail App Password**: Enter any 16-char string (e.g., `testpassword1234`)
3. **Start date**: Accept default or enter `2024-12-01`
4. **End date**: Choose `N` (no)
5. **Document types**: Type `all`
6. **Gmail folder**: Accept default `INBOX`
7. **Output directory**: Accept default `./output`
8. **Dry run**: Choose `Y` (yes) - **IMPORTANT for testing**
9. **Proceed**: Choose `N` (no) to cancel

**Expected**: You see all prompts, a configuration summary, and can cancel safely.

---

## Step 4: Configure Gmail App Password

Before real testing, you need a Gmail App Password:

### 4.1. Enable 2-Factor Authentication

1. Go to: https://myaccount.google.com/security
2. Under "Signing in to Google", enable **2-Step Verification**
3. Follow the setup wizard

### 4.2. Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in if prompted
3. Select app: **Mail**
4. Select device: **Other (Custom name)**
5. Enter name: `Gmail Doc Scraper`
6. Click **Generate**
7. **Copy the 16-character password** (format: `xxxx xxxx xxxx xxxx`)
8. **Important**: Remove the spaces when using it

### 4.3. Enable IMAP

1. Go to: https://mail.google.com/mail/u/0/#settings/fwdandpop
2. Click **Forwarding and POP/IMAP** tab
3. Enable **IMAP access**
4. Click **Save Changes**

---

## Step 5: Test with Real Gmail (Dry Run - Safe)

Now test with your real credentials but in DRY RUN mode (won't save any files):

```bash
python main.py --interactive
```

**Enter your real information:**

1. **Gmail email**: `your-email@gmail.com`
2. **Gmail App Password**: Your 16-char app password (no spaces)
3. **Start date**: `2024-12-01` (last 30 days)
4. **End date**: `N` (no end date)
5. **Document types**: `all`
6. **Gmail folder**: `INBOX`
7. **Output directory**: `./output`
8. **Dry run**: `Y` (yes) ← **IMPORTANT: This prevents saving files**
9. **Proceed**: `Y` (yes)

**Expected**:
- Connects to Gmail successfully
- Shows "Connected successfully to Gmail"
- Searches emails in date range
- Shows "Found X emails"
- Processes emails and shows what WOULD be saved
- Shows messages like: "DRY RUN: Would save invoice.pdf as invoices"
- Shows final report with statistics
- **NO files are actually saved**

**If you see errors**:
- "IMAP authentication failed" → Check App Password (no spaces, correct password)
- "Connection failed" → Check internet connection, IMAP enabled
- "No emails found" → Try a broader date range

---

## Step 6: Test with Real Extraction (Be Careful)

Only after successful dry run, test actual extraction:

```bash
python main.py --interactive
```

**Same as Step 5, but**:
- **Dry run**: `N` (no) ← This will actually save files

**Expected**:
- All steps from Step 5
- Files are saved to `./output/` directory
- Shows messages like: "✓ Saved: invoices/2024-12/invoice_001.pdf"
- Final report shows documents saved
- Check `./output/` folder for extracted documents

---

## Step 7: Verify Results

```bash
# Check output directory
dir output /s

# Check metadata
type output\metadata.json

# Check report (if generated)
dir reports
```

**Expected**:
- `output/` contains folders like: `invoices/`, `contracts/`, etc.
- Each folder organized by date: `2024-12/`, `2025-01/`
- `metadata.json` contains information about all extracted files
- Report in `reports/` directory (if enabled)

---

## Alternative: Test with Docker

If you prefer Docker:

```bash
# Build image
docker-compose build

# Test interactive mode
docker-compose run --rm gmail-scraper --interactive

# Test help
docker-compose run --rm gmail-scraper --help
```

---

## Common Issues and Solutions

### Issue: "ModuleNotFoundError: No module named 'yaml'"

**Solution**:
```bash
pip install pyyaml
```

### Issue: "ModuleNotFoundError: No module named 'rich'"

**Solution**:
```bash
pip install rich
```

### Issue: "spaCy model not available"

**Solution**:
```bash
python -m spacy download pt_core_news_lg
```

### Issue: "IMAP authentication failed"

**Solutions**:
1. Make sure you're using App Password, not regular password
2. Remove spaces from App Password
3. Verify 2FA is enabled
4. Try regenerating App Password

### Issue: "No documents were extracted"

**Solutions**:
1. Use broader date range
2. Check if emails actually have attachments
3. Try `--document-types all`
4. Lower `confidence_threshold` in `config/config.yaml`

---

## Quick Test Commands

```bash
# Show help
python main.py --help

# Interactive mode
python main.py -i

# Non-interactive with prompts
python main.py --email user@gmail.com --start-date 2024-12-01

# Dry run (safe testing)
python main.py -i  # Then select Dry run: Y

# Specific document types
python main.py --email user@gmail.com --start-date 2024-01-01 --document-types invoices,contracts

# Custom output directory
python main.py -i  # Enter custom path in Step 5
```

---

## Test Checklist

- [ ] Step 1: Dependencies installed
- [ ] Step 2: Help menu works
- [ ] Step 3: Interactive prompts work
- [ ] Step 4: Gmail App Password configured
- [ ] Step 5: Dry run connects successfully
- [ ] Step 5: Dry run shows emails found
- [ ] Step 5: Dry run shows classification results
- [ ] Step 6: Real extraction saves files
- [ ] Step 7: Output directory contains files

---

## Next Steps After Testing

1. **Customize document types**: Edit `config/rules.yaml`
2. **Adjust settings**: Edit `config/config.yaml`
3. **Automate**: Use non-interactive mode in scripts
4. **Schedule**: Set up cron job or Windows Task Scheduler
5. **Review**: Check extracted documents and metadata

---

## Support

- **Documentation**: See README.md for full documentation
- **Quick Start**: See QUICKSTART.md for 5-minute setup
- **Issues**: Report at https://gitlab.com/joaocostafernandes-group/gmail-doc-scrapper/-/issues

**Ready to extract documents? Start with Step 1!** 🚀
