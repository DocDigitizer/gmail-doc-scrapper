# Resume Functionality Guide

## Overview

The `--resume` flag allows you to continue processing from where a previous run stopped, using saved configuration and checkpoint data.

## How It Works

### 1. First Run (Interactive)

Run the script in interactive mode to set up your configuration:

```bash
python main.py --interactive
```

This will:
- Prompt for all inputs (email, password, dates, folders, etc.)
- Save configuration to `reports/.last_run.json`
- Save checkpoint progress to `reports/.checkpoint.json`
- Process emails and save documents to `output/`

**Example inputs:**
```
Gmail email: your-email@gmail.com
Start date: 2025-01-01
End date: 2025-12-31
Folder: ALL
```

### 2. Resume Run

If the script stops (connection issues, rate limiting, manual interrupt), simply run:

```bash
python main.py --resume
```

This will:
- ✅ Load saved configuration from `reports/.last_run.json`
- ✅ Load checkpoint from `reports/.checkpoint.json`
- ✅ **Skip already processed emails** (no duplicate work!)
- ✅ **Keep existing output directory** (no cleaning!)
- ✅ Continue from where it stopped
- ✅ Prompt only for password (not saved for security)

### 3. What Gets Saved

**Configuration file** (`reports/.last_run.json`):
```json
{
  "gmail_email": "your-email@gmail.com",
  "start_date": "2025-01-01T00:00:00",
  "end_date": "2025-12-31T23:59:59",
  "document_types": null,
  "folder": "ALL",
  "output_dir": "./output",
  "dry_run": false,
  "saved_at": "2026-01-02T12:00:00"
}
```

**Checkpoint file** (`reports/.checkpoint.json`):
```json
{
  "processed": ["1502", "2", "555249", "15429", ...],
  "total_processed": 296
}
```

## Use Cases

### Scenario 1: Connection Lost

```bash
# First run - stops at 14% due to connection issues
python main.py --interactive
# Processed: 2204/15950 emails

# Resume from checkpoint
python main.py --resume
# Continues: 2204/15950 → 15950/15950 emails
```

### Scenario 2: Manual Interrupt

```bash
# Start processing
python main.py --interactive

# Press Ctrl+C to stop
# Processed: 500/15950 emails

# Continue later
python main.py --resume
# Continues: 500/15950 → 15950/15950 emails
```

### Scenario 3: Rate Limiting

```bash
# First run - hits Gmail rate limit
python main.py --interactive
# Processed: 1000/15950 emails
# Rate limit error - stopped

# Wait 1 hour, then resume
python main.py --resume
# Continues: 1000/15950 → 15950/15950 emails
```

### Scenario 4: Multi-Day Processing

```bash
# Day 1: Process for 2 hours
python main.py --interactive
# Processed: 5000/15950 emails

# Day 2: Continue
python main.py --resume
# Continues: 5000/15950 → 10000/15950

# Day 3: Finish
python main.py --resume
# Continues: 10000/15950 → 15950/15950 emails
```

## Important Notes

### Password Security
- Password is **NEVER saved** to disk
- You'll be prompted for password on `--resume`
- Or set `GMAIL_APP_PASSWORD` environment variable

### Output Directory
- `--resume` keeps existing `output/` directory
- No cleaning, no duplicate files (hash-based deduplication)
- Safe to resume multiple times

### Checkpoint Behavior
- Saves **every 100 emails** processed
- Includes ALL emails (with or without attachments)
- Safe to interrupt at any time

### Starting Fresh
If you want to start completely fresh (ignore checkpoint):

```bash
# Method 1: Run interactive again (cleans everything)
python main.py --interactive

# Method 2: Manually delete checkpoint
rm reports/.checkpoint.json
python main.py --resume
```

## Monitoring Progress

During `--resume` run, you'll see:

```
Gmail Document Scraper v1.0

Resume mode activated - loading saved configuration...
✓ Configuration loaded from last run:
  Email: your-email@gmail.com
  Start: 2025-01-01
  End: 2025-12-31
  Types: All
  Folder: ALL

✓ Found checkpoint: 2204 emails already processed

Resume mode: Keeping existing output directory and checkpoint

Connecting to imap.gmail.com:993...
Connected successfully to Gmail
Selected folder 'INBOX' (15950 messages)

Skipping 2204 already processed emails

⠋ Processing 13746 emails... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  0% 0:00:05
```

## Troubleshooting

### "No saved configuration found"
- Run `python main.py --interactive` first
- Or check if `reports/.last_run.json` exists

### "Password not found in environment"
- Enter password when prompted
- Or set: `export GMAIL_APP_PASSWORD="your_password"`

### Resume processes same emails again
- Check checkpoint file has correct email IDs
- Verify `remaining_ids` calculation in logs

### Want to change configuration
- Run interactive mode again (starts fresh)
- Or manually edit `reports/.last_run.json`

## Command Reference

```bash
# Initial setup (required first)
python main.py --interactive

# Resume from last run
python main.py --resume

# Check help
python main.py --help

# View saved configuration
cat reports/.last_run.json

# View checkpoint
cat reports/.checkpoint.json

# Clear checkpoint (start fresh with same config)
rm reports/.checkpoint.json
python main.py --resume
```

## Example Workflow

```bash
# 1. Initial run with configuration
$ python main.py --interactive
Enter email: your-email@gmail.com
Enter password: ****
Start date: 2025-01-01
End date: 2025-12-31
...
Processing... (stops at 14%)

# 2. Resume immediately
$ python main.py --resume
Enter password: ****
Resuming from 2204/15950 emails...
Processing... (stops at 28%)

# 3. Resume again after 1 hour
$ python main.py --resume
Enter password: ****
Resuming from 4408/15950 emails...
Processing... (completes 100%)

✓ All emails processed!
```

## Benefits

✅ **No Wasted Work** - Skips already processed emails
✅ **Fast Recovery** - Resume in seconds, not hours
✅ **Safe Interruption** - Ctrl+C anytime, no data loss
✅ **Multi-Session** - Process over multiple days
✅ **No Reconfiguration** - Saves all your settings
✅ **Smart Deduplication** - Never saves same file twice
