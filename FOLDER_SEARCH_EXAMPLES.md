# Gmail Folder Search Options

The Gmail Document Scraper now supports searching in multiple folders or all folders at once!

## Interactive Mode Examples

### Option 1: Search ALL Folders (Recommended)

```
Step 4: Gmail Folder
Common folders:
┌────────────────────────────┬──────────────────────────────────┐
│ Option                     │ Description                      │
├────────────────────────────┼──────────────────────────────────┤
│ INBOX                      │ Main inbox folder                │
│ [Gmail]/Sent Mail          │ Sent emails                      │
│ [Gmail]/All Mail           │ All emails (including archived)  │
│ ALL                        │ Search in ALL folders            │
│ INBOX,[Gmail]/Sent Mail    │ Multiple folders                 │
└────────────────────────────┴──────────────────────────────────┘

Gmail folder(s) to search [ALL]: ← Just press ENTER
```

This will search in: INBOX, Sent Mail, and All Mail automatically.

### Option 2: Single Folder

```
Gmail folder(s) to search [ALL]: INBOX
```

### Option 3: Multiple Specific Folders

```
Gmail folder(s) to search [ALL]: INBOX,[Gmail]/Sent Mail
```

## Command Line Examples

### Search all folders
```bash
python main.py --email user@gmail.com --start-date 2024-01-01 --folder ALL
```

### Search specific folders
```bash
python main.py --email user@gmail.com --start-date 2024-01-01 --folder "INBOX,[Gmail]/Sent Mail"
```

### Search only INBOX (default)
```bash
python main.py --email user@gmail.com --start-date 2024-01-01
```

## What Happens When Searching Multiple Folders?

1. The scraper connects to each folder sequentially
2. Searches for emails with attachments in each folder
3. Combines all results
4. Removes duplicate emails (same email in multiple folders)
5. Shows statistics per folder:
   ```
   ✓ Found 15 emails in 'INBOX'
   ✓ Found 8 emails in '[Gmail]/Sent Mail'
   ✓ Found 42 emails in '[Gmail]/All Mail'
   
   Removed 12 duplicate emails
   Total unique emails to process: 53
   ```

## Common Gmail Folders

- **INBOX** - Your main inbox
- **[Gmail]/Sent Mail** - Emails you sent (might contain invoices you sent to clients)
- **[Gmail]/All Mail** - All emails including archived ones
- **[Gmail]/Drafts** - Draft emails
- **[Gmail]/Spam** - Spam folder (not recommended)
- **[Gmail]/Trash** - Deleted emails (not recommended)
- **Custom Labels** - Any labels you created (e.g., "Work", "Personal")

## Tips

1. **Use ALL for first extraction** - Makes sure you don't miss any documents
2. **Be patient** - Searching multiple folders takes longer
3. **Watch for duplicates** - The same email might be in INBOX and All Mail
4. **Use dry-run first** - Test with `--dry-run` to see what would be found

## Troubleshooting

### "Skipping folder (not found)"
Some Gmail folders might have different names depending on your Gmail language settings. Try:
- `[Gmail]/Sent Mail` (English)
- `[Gmail]/Mensagens enviadas` (Portuguese)
- Check your Gmail web interface for exact folder names

### Too slow?
If searching all folders is too slow:
- Search specific folders: `--folder INBOX`
- Use a narrower date range: `--start-date 2024-12-01`

## Example Full Command

```bash
# Interactive with all folders
python main.py --interactive
# When asked for folder, just press ENTER to use "ALL"

# Command line with all folders
python main.py \
  --email your-email@gmail.com \
  --start-date 2024-01-01 \
  --folder ALL \
  --dry-run
```

Happy document hunting! 🔍
