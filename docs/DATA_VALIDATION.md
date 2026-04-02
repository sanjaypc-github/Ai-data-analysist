# Data Validation & Preprocessing Features

## Overview

The Autonomous Data Analyst Agent now includes robust data validation and preprocessing capabilities to handle messy, real-world datasets with missing values, inconsistent formatting, and data quality issues.

## Features

### 1. Automatic Data Quality Analysis

When you upload a CSV file, the system automatically analyzes:
- **Missing values**: Count and percentage per column
- **Data types**: Detected types for each column
- **Duplicates**: Identification of duplicate rows
- **Memory usage**: Dataset size information
- **Sample values**: Preview of data per column

### 2. Intelligent Preprocessing

The system automatically handles missing values using smart strategies:

#### Numeric Columns
- Fills missing values with **median** (more robust than mean)
- Example: If `quantity` has missing values, fills with median quantity

#### Categorical/Text Columns
- Fills missing values with **mode** (most frequent value)
- Falls back to `"Unknown"` if no mode exists
- Example: If `product_name` is missing, uses most common product or "Unknown"

#### Date/Time Columns
- Uses **forward fill** to propagate last valid date
- Maintains temporal continuity

### 3. Multiple Preprocessing Strategies

You can customize preprocessing behavior:

- **`auto`** (default): Smart per-column handling
- **`drop`**: Remove rows with any missing values
- **`fill_mean`**: Fill numeric columns with mean
- **`fill_mode`**: Fill all columns with mode
- **`fill_zero`**: Fill all missing values with 0

### 4. Encoding Support

Automatically detects and handles multiple text encodings:
- UTF-8 (default)
- Latin-1
- ISO-8859-1
- Windows-1252 (CP1252)

## Usage

### Upload API

The `/api/upload` endpoint now returns extended metadata:

```json
{
  "dataset_id": "ds_abc123",
  "filename": "orders.csv",
  "rows": 100,
  "columns": 10,
  "dtypes": {...},
  "validation": {
    "success": true,
    "preprocessing_needed": true,
    "preprocessing_actions": [
      "Filled 5 missing values in 'quantity' with median (2.00)",
      "Filled 3 missing values in 'status' with mode ('completed')"
    ],
    "quality_report": {
      "total_rows": 100,
      "missing_percentage": 3.5,
      "has_missing_values": true,
      ...
    }
  }
}
```

### Quality Report Details

```json
{
  "quality_report": {
    "total_rows": 15,
    "total_columns": 10,
    "missing_percentage": 16.67,
    "has_missing_values": true,
    "has_duplicates": false,
    "columns": [
      {
        "name": "quantity",
        "dtype": "float64",
        "missing_count": 2,
        "missing_percentage": 13.33,
        "unique_values": 8
      }
    ]
  }
}
```

## File Structure

After upload with preprocessing:

```
backend/data/uploads/ds_abc123/
├── orders.csv              # Original file
└── processed_orders.csv    # Cleaned version (if preprocessing needed)
```

The system automatically uses the `processed_*.csv` file for analysis, ensuring clean data is passed to the LLM and pandas code.

## Example: Messy Data Handling

Given a file with missing values:

```csv
order_id,product,quantity,price
1,Laptop,1,999
2,Mouse,,29.99
3,,2,
4,Keyboard,1,79.99
```

The system will:
1. ✅ Detect 3 missing values (25%)
2. ✅ Fill `quantity` with median (1.0)
3. ✅ Fill `product` with mode or "Unknown"
4. ✅ Fill `price` with median (54.99)
4. ✅ Save cleaned version
5. ✅ Use cleaned data for analysis

## Testing

Test file with intentional issues:
```bash
data/sample_orders_messy.csv
```

Contains:
- Missing product names
- Missing quantities
- Missing prices
- Missing statuses
- Missing dates

Upload this file to see automatic preprocessing in action!

## Frontend Integration

### View Results Tab

Now displays:
- ✅ **Actual CSV results** as interactive tables
- ✅ **Visualizations** (PNG images) rendered inline
- ✅ **Download buttons** for each result file
- ✅ **Generated code** in collapsible expander

### Download Report

The HTML report includes:
- Question and metadata
- **Generated pandas code** with syntax highlighting
- Execution output
- Links to result files
- Professional formatting

## API Endpoints

### New Endpoints

1. **Get Task File**: `/api/task/{task_id}/file/{filename}`
   - Download individual output files (CSV, PNG)
   - Properly serves images and data files

2. **Enhanced Upload**: `/api/upload`
   - Returns validation and quality report
   - Indicates if preprocessing was performed

## Code Generation Enhancement

When generating code, the LLM now receives:
- Data quality context
- Column types and missing value info
- Sample data from preprocessed version

This helps generate more robust pandas code that handles edge cases.

## Best Practices

1. **Always review quality report** after upload
2. **Check preprocessing actions** to understand data modifications
3. **Use preprocessed version** for analysis (automatic)
4. **Keep original file** for reference (always preserved)

## Error Handling

- ❌ Invalid CSV format → Clear error message
- ❌ Unsupported encoding → Tries multiple encodings
- ❌ Corrupted file → Validation failure with details
- ❌ Too large file → Memory usage warning

## Configuration

Preprocessing strategy can be customized in `data_validator.py`:

```python
# Change default strategy
df_processed, actions = preprocess_dataframe(df, strategy="auto")

# Options: "auto", "drop", "fill_mean", "fill_mode", "fill_zero"
```

## Limitations

- Maximum file size: Limited by FastAPI settings
- Unstructured data (JSON, XML): Not supported (CSV only)
- Binary data: Not supported
- Very large files (>100MB): May impact performance

## Future Enhancements

- [ ] Support for JSON/Excel formats
- [ ] Custom preprocessing rules per dataset
- [ ] Data validation rules (ranges, constraints)
- [ ] Outlier detection and handling
- [ ] Column type inference improvement
- [ ] Data profiling dashboard

## Security Notes

- All preprocessing happens server-side
- Original files are preserved
- No data is modified in-place
- Processed files are stored separately
- Automatic cleanup of temporary files
