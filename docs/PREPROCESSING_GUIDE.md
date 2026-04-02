# 🔧 Data Preprocessing Feature - User Guide

## Overview

The Autonomous Data Analyst Agent now includes a professional **Data Preprocessing** interface that gives you full control over how to handle missing values, duplicates, and data quality issues before analysis.

---

## 🎯 How It Works

### Step-by-Step Workflow

```
1. Upload Data → 2. Preprocess Data → 3. Ask Question → 4. View Results
   📁              🔧                  ❓                📈
```

### Tab 2: Preprocess Data

After uploading your dataset, click the **"🔧 Preprocess Data"** tab to:

1. **Analyze Data Quality** - Get comprehensive quality report
2. **Review Issues** - See missing values, duplicates, data types
3. **Choose Strategy** - Select how to handle problems
4. **Preview Impact** - Understand what will change
5. **Apply Preprocessing** - Clean your data
6. **Proceed to Analysis** - Ask questions with confidence!

---

## 📊 Data Quality Report

### What You'll See:

#### Summary Metrics
- **Total Rows** - Number of records
- **Total Columns** - Number of features
- **Missing Values** - Percentage of missing data
- **Duplicates** - Count of duplicate rows

#### Column-Level Details
For each column with issues:
- Column name
- Data type
- Missing count
- Missing percentage
- Unique values count

---

## 🛠️ Preprocessing Strategies

### 1. 🤖 Auto (Recommended)
**Best for:** Most scenarios, general-purpose cleaning

**How it works:**
- **Numeric columns** → Fills with **median** (robust against outliers)
- **Categorical columns** → Fills with **mode** (most frequent value)
- **Date columns** → **Forward fill** (propagate previous value)

**Example:**
```
Column: quantity (numeric)
Missing: 5 values
Action: Filled with median (2.0)
```

---

### 2. 🗑️ Drop Rows
**Best for:** When missing data is minimal (<5%)

**How it works:**
- Removes any row containing at least one missing value

**Warning:** Can significantly reduce dataset size!

**Example:**
```
Before: 100 rows, 10 missing values
After: 92 rows, 0 missing values
```

---

### 3. 🗑️ Drop Columns
**Best for:** Columns with >50% missing data

**How it works:**
- Removes columns where more than 50% of values are missing
- Keeps all rows intact

**Example:**
```
Column: optional_notes
Missing: 75%
Action: Dropped column
```

---

### 4. 0️⃣ Fill with Zero
**Best for:** Count data, flags, binary indicators

**How it works:**
- Replaces all missing values with 0

**Warning:** May skew statistics for continuous variables!

**Good use case:**
```
Column: purchase_count (0 = no purchases)
Missing values → 0
```

---

### 5. 📊 Fill with Mean
**Best for:** Normally distributed numeric data

**How it works:**
- Calculates average of non-missing values
- Fills missing values with this average

**Warning:** Sensitive to outliers!

**Example:**
```
Values: [10, 20, 30, 40, NaN]
Mean: 25
Result: [10, 20, 30, 40, 25]
```

---

### 6. 📊 Fill with Median (Robust)
**Best for:** Numeric data with potential outliers

**How it works:**
- Calculates middle value of sorted non-missing data
- Fills missing values with median

**Why better than mean:** Not affected by extreme values

**Example:**
```
Values: [10, 20, 30, 40, 1000, NaN]
Mean: 220 (skewed by 1000!)
Median: 30 (robust)
Result: [10, 20, 30, 40, 1000, 30]
```

---

### 7. 📊 Fill with Mode
**Best for:** Categorical data, discrete values

**How it works:**
- Finds most frequent value
- Fills missing values with this value

**Example:**
```
Values: ['North', 'South', 'North', NaN, 'North']
Mode: 'North'
Result: ['North', 'South', 'North', 'North', 'North']
```

---

### 8. ➡️ Forward Fill
**Best for:** Time series data, sequential data

**How it works:**
- Uses the last valid value before the gap
- Propagates values forward

**Example:**
```
Date:  [Jan, Feb, Mar, Apr, May]
Value: [10,  20,  NaN, NaN, 50]
Result:[10,  20,  20,  20,  50]
```

---

### 9. ⬅️ Backward Fill
**Best for:** Time series with future dependencies

**How it works:**
- Uses the next valid value after the gap
- Propagates values backward

**Example:**
```
Date:  [Jan, Feb, Mar, Apr, May]
Value: [10,  NaN, NaN, 40,  50]
Result:[10,  40,  40,  40,  50]
```

---

### 10. ⚙️ Custom (Advanced)
**Best for:** Complex requirements, different strategies per column

**How it works:**
- Configure strategy for each column individually
- Mix and match different approaches

**Options per column:**
- **Numeric:** median, mean, zero, mode, drop, forward_fill, backward_fill
- **Categorical:** mode, custom_value, drop, forward_fill, backward_fill

**Example:**
```
Column: quantity → Fill with median
Column: status → Fill with mode
Column: notes → Fill with "No notes"
Column: optional_id → Drop rows with missing
```

---

## 🎮 How to Use Custom Strategy

### Step-by-Step:

1. **Select "Custom" strategy** from radio buttons
2. **Configure each column** with missing values:
   - Choose strategy from dropdown
   - If "custom_value" selected, enter the value
3. **Preview impact** (optional)
4. **Click "Apply Preprocessing"**

### Example Configuration:

```
product_name (text, 5% missing)
└─ Strategy: Fill with mode

quantity (numeric, 10% missing)  
└─ Strategy: Fill with median

price (numeric, 3% missing)
└─ Strategy: Fill with mean

notes (text, 80% missing)
└─ Strategy: Drop column

status (categorical, 2% missing)
└─ Strategy: Custom value → "pending"
```

---

## 📋 Preview Impact

Before applying preprocessing, expand **"📋 Preview Impact"** to see:

- Number of rows to be removed (if using drop_rows)
- Columns to be removed (if using drop_columns)
- Estimated remaining data size

---

## ✅ After Preprocessing

Once preprocessing completes:

1. ✅ **Success message** with confirmation
2. 📊 **Actions performed** - List of all changes made
3. 📈 **Quality metrics** - Before/After comparison
   - Missing values: 8.67% → 0%
   - Rows: 100 → 100 (or changed if dropped)
4. 🎉 **Balloons animation** (you did it!)
5. 💡 **Next step** - Proceed to "Ask Question" tab

---

## 🔄 Re-preprocessing

Want to try a different strategy?

1. Click **"🔍 Analyze Data Quality"** again
2. Choose a different strategy
3. Apply new preprocessing

**Note:** Each preprocessing creates a new `processed_*.csv` file

---

## 📁 File Structure

After preprocessing:

```
backend/data/uploads/ds_abc123/
├── orders.csv                    # Original (preserved)
└── processed_orders.csv          # Cleaned version (used for analysis)
```

The system automatically uses the **processed version** for all analyses.

---

## 🎯 Strategy Selection Guide

### Quick Decision Tree:

```
Is missing data < 5%?
├─ Yes → Use "Drop Rows"
└─ No → Continue...

Do columns have >50% missing?
├─ Yes → Use "Drop Columns" first
└─ No → Continue...

Is data mostly numeric?
├─ Yes → Use "Fill with Median" (robust)
│   └─ Or "Auto" for mixed types
└─ No → Use "Fill with Mode"

Need fine control?
└─ Yes → Use "Custom"

Not sure?
└─ Use "Auto" (recommended!)
```

---

## ⚠️ Important Notes

### Data Integrity
- Original file is **always preserved**
- Preprocessing is **non-destructive**
- You can re-upload and try again

### Performance
- Large files (>100MB) may take longer
- Preprocessing happens server-side
- Progress shown in real-time

### Best Practices
1. **Always review quality report first**
2. **Understand your data** before choosing strategy
3. **Preview impact** when possible
4. **Document your choices** for reproducibility
5. **Test with small subset** if unsure

---

## 🔧 Troubleshooting

### "No data quality issues detected"
- ✅ Your data is already clean!
- ✅ Skip to "Ask Question" tab

### "Preprocessing failed"
- Check file encoding (try UTF-8)
- Ensure CSV is valid format
- Check for extremely large files

### "All rows would be dropped"
- Too many missing values
- Try "Fill with Median/Mode" instead
- Or "Drop Columns" first

---

## 📊 Real-World Examples

### Example 1: E-commerce Orders
**Problem:** 10% missing quantities, 5% missing prices

**Solution:**
```
Strategy: Auto
✓ Filled quantity with median (1.0)
✓ Filled price with median (29.99)
Result: 100% complete data
```

### Example 2: Customer Survey
**Problem:** 60% missing "optional_comments" column

**Solution:**
```
Strategy: Drop Columns
✓ Removed optional_comments (60% missing)
Result: Clean dataset with useful columns only
```

### Example 3: Time Series Sales
**Problem:** 3% missing sales values in middle of dataset

**Solution:**
```
Strategy: Forward Fill
✓ Propagated last known sales value
Result: Continuous time series
```

### Example 4: Mixed Data Types
**Problem:** Various columns with different issues

**Solution:**
```
Strategy: Custom
✓ quantity → median
✓ category → mode
✓ notes → "No notes provided"
✓ optional_field → drop rows
Result: Perfectly cleaned dataset
```

---

## 🚀 Next Steps

After preprocessing:

1. ✅ Go to **"Ask Question"** tab
2. ✅ Ask your analysis questions
3. ✅ System uses cleaned data automatically
4. ✅ Get accurate results!

---

## 📚 Additional Resources

- `docs/DATA_VALIDATION.md` - Technical details
- `test_data_validation.py` - Test script
- `data/sample_orders_messy.csv` - Example messy data

---

**Happy Data Cleaning! 🧹✨**
