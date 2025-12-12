# Process All Guide

This guide explains how to use the `--process-all` command to reprocess all records through all processors in the correct order.

## Overview

The `--process-all` command processes each product record through all processors sequentially, ensuring that each record completes all processing steps before moving to the next record. This approach is optimized for:

- **Data consistency**: Each record is fully processed before moving on
- **Error isolation**: Failures in one record don't affect others
- **Progress tracking**: Clear visibility into which record and step is being processed
- **Database efficiency**: Better transaction management per record

## Processing Order

The processors run in the following order for each record:

1. **Category Classifier** - Classifies food category (Raw, Fresh, Dry, Wet, Other)
2. **Sourcing Integrity** - Determines sourcing integrity (Human Grade, Feed Grade, etc.)
3. **Processing Method** - Identifies processing methods (Extruded, Freeze Dried, etc.)
4. **Nutritionally Adequate** - Determines if product is nutritionally adequate
5. **Starchy Carb** - Extracts nutrition values and calculates starchy carb percentage
6. **Ingredient Quality** - Classifies ingredient quality (includes Synthetic Nutrition Addition)
7. **Longevity Additives** - Identifies longevity additives

## Usage

### Basic Usage

Process all records:

```bash
python scripts/main.py --process-all
```

### With Limits

Process a limited number of records:

```bash
python scripts/main.py --process-all --limit 100
```

### With Offset

Start processing from a specific offset:

```bash
python scripts/main.py --process-all --limit 50 --offset 100
```

This processes records starting from the 100th record, up to 50 records.

### Force Reprocessing

Force reprocessing even if records are already processed:

```bash
python scripts/main.py --process-all --force
```

## Output Format

The command provides detailed progress information:

```
======================================================================
🔄 PROCESS ALL - Running All Processors in Order
======================================================================

📊 Found 150 product(s) to process

Processing order:
  1. Category Classifier
  2. Sourcing Integrity
  3. Processing Method
  4. Nutritionally Adequate
  5. Starchy Carb
  6. Ingredient Quality (includes Synthetic Nutrition)
  7. Longevity Additives

======================================================================
[1/150] Processing: Blue Buffalo Wilderness Chicken Recipe Kibble
======================================================================
  [1/7] Category Classifier... ✅
  [2/7] Sourcing Integrity... ✅
  [3/7] Processing Method... ✅
  [4/7] Nutritionally Adequate... ✅
  [5/7] Starchy Carb... ✅
  [6/7] Ingredient Quality... ✅
  [7/7] Longevity Additives... ✅
  ✅ Record 1 completed successfully

======================================================================
[2/150] Processing: Purina Pro Plan Adult Dog Food
======================================================================
  [1/7] Category Classifier... ✅
  [2/7] Sourcing Integrity... ✅
  ...
```

## Summary Report

After processing completes, a summary report is displayed:

```
======================================================================
📊 PROCESSING SUMMARY
======================================================================

Overall:
  Total Records:        150
  Successful:          148
  Failed:                2
  Duration:          245.32s (4.1m)
  Avg per record:      1.66s

By Processor:
  Category Classifier    :    148 ✅ /      2 ❌ ( 98.7%)
  Sourcing Integrity    :    148 ✅ /      2 ❌ ( 98.7%)
  Processing Method     :    148 ✅ /      2 ❌ ( 98.7%)
  Nutritionally Adequate:    148 ✅ /      2 ❌ ( 98.7%)
  Starchy Carb          :    148 ✅ /      2 ❌ ( 98.7%)
  Ingredient Quality    :    148 ✅ /      2 ❌ ( 98.7%)
  Longevity Additives   :    148 ✅ /      2 ❌ ( 98.7%)
======================================================================
```

## Error Handling

If a processor fails for a specific record:

- The error is logged but processing continues with the next processor
- The record is marked as failed but other records continue processing
- Error messages are truncated to 60 characters for readability
- Full error details can be found in the traceback if the command crashes

## Performance Considerations

### Processing Time

- Average processing time per record: ~1-3 seconds
- Total time depends on number of records and database performance
- Each processor commits changes immediately after processing

### Database Impact

- Each record is processed in a single transaction per processor
- Commits happen after each processor completes
- Failed processors don't rollback successful processors

### Memory Usage

- All product details are loaded into memory at the start
- For large datasets, consider using `--limit` to process in batches

## Best Practices

### 1. Process in Batches

For large datasets, process in manageable batches:

```bash
# Process first 100 records
python scripts/main.py --process-all --limit 100

# Process next 100 records
python scripts/main.py --process-all --limit 100 --offset 100

# Continue with next batch
python scripts/main.py --process-all --limit 100 --offset 200
```

### 2. Monitor Progress

Watch the terminal output to monitor:
- Current record being processed
- Which processor step is running
- Success/failure status for each step

### 3. Handle Errors

If errors occur:
- Check the error message for the specific record
- Verify the product details exist and are valid
- Re-run with `--force` if needed after fixing data issues

### 4. Verify Results

After processing, verify results:

```bash
# Check statistics
python scripts/main.py --stats

# Or check specific processor statistics
python scripts/main.py --process --category
```

## Comparison with Individual Processing

### Process All (Recommended)

**Advantages:**
- Processes each record completely before moving on
- Better error isolation
- Clear progress tracking per record
- Optimized for consistency

**Use when:**
- Reprocessing all records
- Need complete records processed together
- Want clear progress visibility

### Individual Processor Commands

**Advantages:**
- Can process specific processors only
- Can reprocess specific categories/methods
- More granular control

**Use when:**
- Only need to update specific processor results
- Testing individual processors
- Reprocessing specific categories

Example of individual processing:

```bash
# Process only categories
python scripts/main.py --process --category

# Reprocess specific category
python scripts/main.py --process --category --reprocess-category Dry
```

## Troubleshooting

### No Products Found

If you see "No products to process!":

1. Verify products exist: `python scripts/main.py --stats`
2. Check that products have details (scraped)
3. Ensure database connection is working

### Processor Errors

If processors fail:

1. Check product details exist and are valid
2. Verify database schema is up to date
3. Check for missing required fields
4. Review error messages for specific issues

### Performance Issues

If processing is slow:

1. Use `--limit` to process in smaller batches
2. Check database performance and indexes
3. Consider processing during off-peak hours
4. Monitor database connection pool

## Examples

### Example 1: Process First 50 Records

```bash
python scripts/main.py --process-all --limit 50
```

### Example 2: Process Records 100-200

```bash
python scripts/main.py --process-all --limit 100 --offset 100
```

### Example 3: Force Reprocess All

```bash
python scripts/main.py --process-all --force
```

### Example 4: Process All with Progress Monitoring

Run in a terminal with scrollback enabled to review progress:

```bash
python scripts/main.py --process-all 2>&1 | tee process_all.log
```

This saves output to `process_all.log` while displaying in terminal.

## Related Commands

- `--process --category` - Process only food categories
- `--process --sourcing` - Process only sourcing integrity
- `--process --processing` - Process only processing methods
- `--process --ingredient-quality` - Process only ingredient quality
- `--process --longevity-additives` - Process only longevity additives
- `--process --nutritionally-adequate` - Process only nutritionally adequate
- `--process --starchy-carb` - Process only starchy carb extraction
- `--stats` - View processing statistics

## Notes

- Synthetic Nutrition Addition is processed as part of Ingredient Quality (step 6)
- Each processor commits changes immediately after processing
- Failed processors don't prevent other processors from running
- The command processes records sequentially, not in parallel
- Progress is displayed in real-time as each step completes
