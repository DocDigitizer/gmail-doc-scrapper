# Quick Testing Instructions

## ✅ Installation Verified!

The Gmail Document Scraper is now installed and ready to test.

---

## 🚀 Quick Start - Test in 3 Steps

### Step 1: View Help (No credentials needed)

```bash
cd C:\Users\jcfernandes\Desktop\gmail-doc-scrapper
python main.py --help
```

**What you'll see**: All available command-line options

---

### Step 2: Setup Gmail App Password

Before testing with real data, you need a Gmail App Password:

1. **Enable 2FA**: https://myaccount.google.com/security → 2-Step Verification
2. **Generate App Password**: https://myaccount.google.com/apppasswords
   - App: Mail
   - Device: Other (Gmail Doc Scraper)
   - Copy the 16-character password (remove spaces)
3. **Enable IMAP**: https://mail.google.com/mail/#settings/fwdandpop → Enable IMAP

---

### Step 3: Test Interactive Mode (Dry Run - SAFE)

```bash
python main.py --interactive
```

**Follow the prompts:**

```
Step 1: Gmail Credentials
  Gmail email: your-email@gmail.com
  Gmail App Password: [paste your 16-char password]

Step 2: Date Range
  Start date (YYYY-MM-DD) [2024-12-01]: ← Press Enter for default
  Specify end date? (y/N): n ← No end date

Step 3: Document Types
  Document types (comma-separated or 'all') [all]: all ← Extract all types

Step 4: Gmail Folder
  Gmail folder to search [INBOX]: ← Press Enter for INBOX

Step 5: Output Directory
  Output directory [./output]: ← Press Enter for default

  Dry run (test without saving files)? (y/N): y ← IMPORTANT: Say YES for safe testing

Configuration Summary:
  [Shows all your settings]

Proceed with extraction? (Y/n): y ← Confirm
```

**What happens in DRY RUN mode:**
- ✅ Connects to your Gmail
- ✅ Searches for emails with attachments
- ✅ Analyzes and classifies documents
- ✅ Shows what WOULD be saved
- ❌ Does NOT actually save any files
- ✅ Shows final report

---

## 📊 What to Expect

### Success Output:
```
Gmail Document Scraper v1.0

Loading configuration...
✓ Configuration loaded

Connecting to imap.gmail.com:993...
✓ Connected successfully to Gmail

Selected folder 'INBOX' (150 messages)

Searching emails...
Found 45 emails

Processing 45 emails... ████████████████ 100% 0:01:23

✓ Extracted text from PDF using pdfplumber
✓ Classified as 'Invoices' (confidence: 0.85, method: pattern)
DRY RUN: Would save invoice_2024.pdf as invoices

[... more processing ...]

Disconnected from Gmail

════════════════════════════════════════════
         Gmail Document Scraper Report
════════════════════════════════════════════
Started:  2025-01-01 10:00:00
Finished: 2025-01-01 10:02:15
Duration: 0:02:15

┌─────────────────────────┬───────┐
│ Emails Processed        │ 45    │
│ Emails with Attachments │ 28    │
│ Total Attachments Found │ 52    │
└─────────────────────────┴───────┘

┌─────────────────────────┬───────┐
│ Documents Classified    │ 35    │
│ Documents Saved         │ 0     │  ← 0 because DRY RUN
│ Duplicates Skipped      │ 2     │
│ Classification Failures │ 15    │
└─────────────────────────┴───────┘

┌───────────────┬───────┐
│ invoices      │ 12    │
│ contracts     │ 8     │
│ receipts      │ 10    │
│ tax_documents │ 5     │
└───────────────┴───────┘
```

---

## 🎯 After Successful Dry Run

If the dry run worked, test actual extraction:

```bash
python main.py --interactive
```

Same steps, but:
- **Dry run**: n ← Say NO to actually save files

Files will be saved to:
```
C:\Users\jcfernandes\Desktop\gmail-doc-scrapper\output\
├── invoices\
│   ├── 2024-12\
│   │   ├── invoice_001.pdf
│   │   └── invoice_002.pdf
│   └── 2025-01\
│       └── invoice_003.pdf
├── contracts\
│   └── 2024-11\
│       └── contract_xyz.pdf
└── metadata.json
```

---

## 🔧 Common Issues & Solutions

### Issue: "IMAP authentication failed"
**Solutions**:
- ✅ Use App Password, not regular Gmail password
- ✅ Remove all spaces from App Password
- ✅ Verify 2FA is enabled
- ✅ Check IMAP is enabled in Gmail settings

### Issue: "No emails found"
**Solutions**:
- Try broader date range: `--start-date 2024-01-01`
- Check if emails have attachments
- Try different folder: some emails might be in other folders

### Issue: "ModuleNotFoundError"
**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: "spaCy model not available"
**Solution**:
```bash
python -m spacy download pt_core_news_lg
```

---

## 🎮 Alternative: Non-Interactive Mode

For automation or scripts:

```bash
# You'll be prompted for password securely
python main.py \
  --email your-email@gmail.com \
  --start-date 2024-01-01 \
  --document-types invoices,contracts \
  --dry-run
```

---

## 📝 Test Checklist

- [ ] Help command works (`python main.py --help`)
- [ ] Gmail App Password generated
- [ ] IMAP enabled in Gmail
- [ ] Interactive mode prompts appear
- [ ] Dry run connects to Gmail successfully
- [ ] Dry run finds emails
- [ ] Dry run classifies documents
- [ ] Real extraction saves files (optional)

---

## 🆘 Need Help?

1. **Full Documentation**: See `README.md`
2. **Test Guide**: See `TEST_GUIDE.md` (comprehensive guide)
3. **Issues**: https://gitlab.com/joaocostafernandes-group/gmail-doc-scrapper/-/issues

---

## ✨ You're Ready!

Start with:
```bash
python main.py --interactive
```

Good luck extracting your documents! 🚀
