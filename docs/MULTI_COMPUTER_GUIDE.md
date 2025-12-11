# Multi-Computer Scraping Guide

This guide explains how to distribute scraping work across multiple computers and merge the results.

## Quick Start Workflow

### Scenario: Scrape 3600 products across 3 computers (1200 each)

### Step 1: On Master Computer - Distribute Work

```bash
python distribute_work.py --computers 3 --chunk-size 1200
```

**Output:**
```
🖥️  Computer 1:
   Offset: 0
   Limit: 1200
   Command: python main.py --details --offset 0 --limit 1200

🖥️  Computer 2:
   Offset: 1200
   Limit: 1200
   Command: python main.py --details --offset 1200 --limit 1200

🖥️  Computer 3:
   Offset: 2400
   Limit: 1200
   Command: python main.py --details --offset 2400 --limit 1200
```

### Step 2: Set Up Each Computer

**On each computer:**

1. Copy project files:
   ```bash
   # Copy these files to each computer
   - scraper.py
   - main.py
   - database.py
   - config.py
   - monitor_scraper.py
   - requirements.txt
   ```

2. Set up environment:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up database (local or shared)
   docker-compose up -d
   ```

3. **IMPORTANT:** Copy the `products_list` table to each computer
   - Option A: Export/import SQL dump
   - Option B: Use shared database (see below)

### Step 3: Run Scraping on Each Computer

**Computer 1:**
```bash
python monitor_scraper.py --details --offset 0 --limit 1200
```

**Computer 2:**
```bash
python monitor_scraper.py --details --offset 1200 --limit 1200
```

**Computer 3:**
```bash
python monitor_scraper.py --details --offset 2400 --limit 1200
```

### Step 4: Export Data from Each Computer

**After scraping completes on each computer:**

**Computer 1:**
```bash
python export_data.py --output computer1_export.json
```

**Computer 2:**
```bash
python export_data.py --output computer2_export.json
```

**Computer 3:**
```bash
python export_data.py --output computer3_export.json
```

### Step 5: Import into Master Database

**On master computer, import all exports:**

```bash
# Import from Computer 1
python import_data.py computer1_export.json

# Import from Computer 2
python import_data.py computer2_export.json

# Import from Computer 3
python import_data.py computer3_export.json
```

**Preview before importing:**
```bash
python import_data.py computer1_export.json --dry-run
```

## Alternative: Shared Database Approach

If all computers can access the same PostgreSQL database:

### Advantages:
- ✅ No export/import needed
- ✅ Real-time progress visibility
- ✅ Automatic conflict resolution
- ✅ All data in one place immediately

### Setup:

1. **Set up PostgreSQL server** accessible by all computers

2. **Update `config.py` on each computer:**
   ```python
   DATABASE_URL = 'postgresql://user:password@server-ip:5432/chewy_db'
   ```

3. **Run scraping with offsets** (same as Step 3 above)

4. **Done!** All data is automatically in the shared database

### Network Requirements:
- All computers must be able to connect to the database server
- Consider firewall rules and VPN if needed
- Ensure stable network connection

## Best Practices

1. **Backup before starting:** Export your `products_list` table
   ```bash
   docker exec chewy_scraper_db pg_dump -U chewy_user chewy_db > backup.sql
   ```

2. **Monitor progress:** Check scraped counts periodically
   ```sql
   SELECT COUNT(*) FROM products_list WHERE scraped = true;
   ```

3. **Use monitor script:** Always use `monitor_scraper.py` for automatic restart on errors

4. **Verify exports:** Check export file sizes and counts before transferring

5. **Test import:** Use `--dry-run` to preview imports before committing

## Troubleshooting

### Issue: Duplicate products after import
**Solution:** The import script automatically skips duplicates based on `product_url`. This is expected behavior.

### Issue: Foreign key errors
**Solution:** Ensure `products_list` table exists and has the same structure on all computers.

### Issue: Offset doesn't match expected products
**Solution:** Products are ordered by ID. If products were deleted, offsets may shift. Use `distribute_work.py` to recalculate.

### Issue: Network timeout with shared database
**Solution:** Increase PostgreSQL connection timeout or use local databases with export/import approach.

## File Transfer

To transfer export files between computers:

**Option 1: USB Drive**
```bash
# Copy export files to USB
cp computer1_export.json /path/to/usb/

# On master computer, copy from USB
cp /path/to/usb/computer1_export.json .
```

**Option 2: Network Share**
```bash
# Copy via SCP
scp computer1_export.json user@master-computer:/path/to/destination/
```

**Option 3: Cloud Storage**
- Upload to Google Drive, Dropbox, etc.
- Download on master computer

## Summary

✅ **Distribute work** → `distribute_work.py`
✅ **Run scraping** → `monitor_scraper.py --details --offset X --limit Y`
✅ **Export data** → `export_data.py`
✅ **Import data** → `import_data.py`

This workflow ensures no data loss, handles duplicates gracefully, and maintains referential integrity.

