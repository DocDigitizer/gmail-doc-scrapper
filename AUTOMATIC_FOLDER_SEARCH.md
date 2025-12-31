# Automatic All-Folder Search

The Gmail Document Scraper now **automatically searches in ALL Gmail folders** without asking!

## What Changed

### Before ❌
```
Step 4: Gmail Folder
Search in all folders (INBOX, Sent Mail, All Mail)? (Y/n): 
```

### Now ✅
```
📁 Will search in all Gmail folders (INBOX, Sent Mail, All Mail)

🔍 Discovering all Gmail folders...
✓ Found 12 folders to search
Folders: INBOX, [Gmail]/Sent Mail, [Gmail]/All Mail, Work, Personal...
```

**No questions asked!** The scraper automatically:
1. Discovers ALL folders in your Gmail account
2. Excludes only Spam and Trash folders
3. Searches everything else (INBOX, Sent, labels, archives, etc.)

## How It Works

### Dynamic Folder Discovery

The scraper now:
1. Connects to Gmail via IMAP
2. Lists all available folders using `IMAP LIST` command
3. Automatically excludes:
   - `[Gmail]/Spam`
   - `[Gmail]/Trash`
   - `[Gmail]/Bin`
4. Searches in **all other folders** including:
   - INBOX
   - [Gmail]/Sent Mail
   - [Gmail]/All Mail
   - [Gmail]/Drafts
   - [Gmail]/Important
   - [Gmail]/Starred
   - All your custom labels (Work, Personal, etc.)

### Example Output

```
Gmail Document Scraper v1.0

Loading configuration...
✓ Configuration loaded

Connecting to imap.gmail.com:993...
✓ Connected successfully to Gmail

📁 Will search in all Gmail folders (INBOX, Sent Mail, All Mail)

🔍 Discovering all Gmail folders...
✓ Found 12 folders to search
Folders: INBOX, [Gmail]/Sent Mail, [Gmail]/All Mail, Work, Personal...

Selected folder 'INBOX' (150 messages)
✓ Found 15 emails in 'INBOX'

Selected folder '[Gmail]/Sent Mail' (82 messages)
✓ Found 8 emails in '[Gmail]/Sent Mail'

Selected folder 'Work' (45 messages)
✓ Found 5 emails in 'Work'

... [continues for all folders]

Removed 12 duplicate emails
Total unique emails to process: 53

Processing 53 emails... ████████████████ 100%
```

## Benefits

✅ **No configuration needed** - Just run and it finds everything
✅ **Never miss a document** - Searches all folders automatically
✅ **Includes custom labels** - Your Work, Personal, Project folders, etc.
✅ **Smart filtering** - Excludes Spam and Trash automatically
✅ **Duplicate removal** - Same email in multiple folders = counted once
✅ **Dynamic** - Adapts to YOUR Gmail structure

## Interactive Mode

```bash
python main.py --interactive
```

Now you'll see:

```
Step 1: Gmail Credentials
  Gmail email: your-email@gmail.com
  Gmail App Password: ****

Step 2: Date Range
  Start date [2024-12-01]: 
  Specify end date? (y/N): n

Step 3: Document Types
  Document types [all]: all

Step 4: Output Directory           ← Note: Step 4 is now Output, not Folder!
  Output directory [./output]: 

  Dry run? (y/N): y

Configuration Summary:
  Email: your-email@gmail.com
  Start Date: 2024-12-01
  Document Types: All
  Folders: ALL (automatic)          ← Always set to ALL
  Output Directory: ./output
  Dry Run: Yes

Proceed? (Y/n): y
```

## Command Line Usage

The `--folder` parameter still exists for advanced users:

```bash
# Default: searches all folders automatically
python main.py --email user@gmail.com --start-date 2024-01-01

# Advanced: specify specific folder(s)
python main.py --email user@gmail.com --start-date 2024-01-01 --folder INBOX

# Advanced: multiple specific folders
python main.py --email user@gmail.com --start-date 2024-01-01 --folder "INBOX,Work"
```

## Why This Is Better

### Before (Manual Selection)
- ❌ Users had to know Gmail folder names
- ❌ Easy to miss folders/labels
- ❌ Required understanding of Gmail structure
- ❌ Extra step in workflow

### Now (Automatic)
- ✅ Zero configuration needed
- ✅ Guaranteed to find everything
- ✅ Works with any Gmail setup
- ✅ Faster workflow (one less question)

## Performance Notes

**"Will this be slow?"**

- First run: Takes longer as it searches all folders
- Subsequent runs: Duplicates are removed, so similar speed
- Tip: Use narrower date ranges if needed (`--start-date 2024-12-01`)

**"Too many folders?"**

If you have 50+ labels and it's too slow:
- Use command line with specific folder: `--folder INBOX`
- Or use a recent date range: `--start-date 2024-12-15`

## Troubleshooting

### "Failed to list folders"

If folder discovery fails, the scraper automatically falls back to:
- INBOX
- [Gmail]/Sent Mail
- [Gmail]/All Mail

### "Skipping folder (not found)"

Some folders might be inaccessible due to Gmail settings. This is normal and the scraper continues with other folders.

### Different Languages

Gmail folder names vary by language:
- English: `[Gmail]/Sent Mail`
- Portuguese: `[Gmail]/Mensagens enviadas`
- The scraper handles this automatically by listing actual folder names!

## Quick Test

```bash
cd C:\Users\jcfernandes\Desktop\gmail-doc-scrapper
python main.py --interactive

# Just answer the 4 questions (no folder selection!)
# It will automatically search everywhere
```

Enjoy never missing a document again! 🎉
