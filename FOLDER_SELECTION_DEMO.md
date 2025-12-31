# Gmail Folder Selection - How It Works

The Gmail Document Scraper now asks you directly if you want to search all folders!

## Interactive Flow

### Step 4: Gmail Folder

```
Step 4: Gmail Folder

Search in all folders (INBOX, Sent Mail, All Mail)? (Y/n): 
```

**Two options:**

### Option 1: Search All Folders (Recommended) ⭐

```
Search in all folders (INBOX, Sent Mail, All Mail)? (Y/n): y
✓ Will search in all folders
```

Press **Y** or just **ENTER** to search in:
- INBOX
- [Gmail]/Sent Mail  
- [Gmail]/All Mail

**Why this is recommended:**
- Ensures you don't miss any documents
- Covers sent emails (you might have sent invoices)
- Includes archived emails
- Automatic duplicate removal

---

### Option 2: Specify Folder(s)

```
Search in all folders (INBOX, Sent Mail, All Mail)? (Y/n): n

Available Gmail folders:
┌─────────────────────┬────────────────────────────────┐
│ Folder Name         │ Description                    │
├─────────────────────┼────────────────────────────────┤
│ INBOX               │ Main inbox folder              │
│ [Gmail]/Sent Mail   │ Sent emails                    │
│ [Gmail]/All Mail    │ All emails (including archived)│
│ [Gmail]/Drafts      │ Draft emails                   │
│ Work                │ Custom label example           │
└─────────────────────┴────────────────────────────────┘

Tip: You can specify multiple folders separated by commas
Example: INBOX,[Gmail]/Sent Mail

Gmail folder(s) to search [INBOX]: 
```

**Examples:**

Single folder:
```
Gmail folder(s) to search [INBOX]: INBOX
```

Multiple folders:
```
Gmail folder(s) to search [INBOX]: INBOX,[Gmail]/Sent Mail
```

Custom label:
```
Gmail folder(s) to search [INBOX]: Work
```

---

## What Happens Next

### When searching all folders:
```
Searching in ALL folders: INBOX, Sent Mail, All Mail

Selected folder 'INBOX' (150 messages)
✓ Found 15 emails in 'INBOX'

Selected folder '[Gmail]/Sent Mail' (82 messages)  
✓ Found 8 emails in '[Gmail]/Sent Mail'

Selected folder '[Gmail]/All Mail' (1250 messages)
✓ Found 42 emails in '[Gmail]/All Mail'

Removed 12 duplicate emails
Total unique emails to process: 53

Processing 53 emails... ████████████ 100%
```

### When searching specific folder(s):
```
Searching in folder: INBOX

Selected folder 'INBOX' (150 messages)
Found 15 emails

Processing 15 emails... ████████████ 100%
```

---

## Command Line Usage

You can also specify this via command line:

### Search all folders
```bash
python main.py --email user@gmail.com --start-date 2024-01-01 --folder ALL
```

### Search specific folder
```bash
python main.py --email user@gmail.com --start-date 2024-01-01 --folder INBOX
```

### Search multiple folders
```bash
python main.py --email user@gmail.com --start-date 2024-01-01 --folder "INBOX,[Gmail]/Sent Mail"
```

---

## Tips

1. **First time? Use "all folders"** - You won't miss anything
2. **Subsequent extractions?** - Target specific folders to save time
3. **Use dry-run first** - Test with `--dry-run` to see what's found
4. **Multiple folders with same email?** - Duplicates are automatically removed

---

## Troubleshooting

### "Skipping folder (not found or inaccessible)"

Some folders might have different names based on your Gmail language:
- English: `[Gmail]/Sent Mail`
- Portuguese: `[Gmail]/Mensagens enviadas`
- Spanish: `[Gmail]/Enviados`

**Solution**: Check your Gmail web interface for the exact folder name.

### Folder search is slow

If searching all folders is too slow:
1. Use a narrower date range: `--start-date 2024-12-01`
2. Search specific folders only
3. Use `[Gmail]/All Mail` alone (contains everything but slower)

---

## Quick Test

```bash
cd C:\Users\jcfernandes\Desktop\gmail-doc-scrapper
python main.py --interactive

# When asked "Search in all folders?"
# - Press Y (or ENTER) to search everywhere
# - Press N to choose specific folders
```

Happy document hunting! 🔍
