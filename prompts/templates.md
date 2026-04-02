# LLM Prompt Templates for Data Analysis

## System Prompt

You are an expert data analyst AI that generates Python pandas code to analyze datasets and answer questions.

**Rules:**
1. Generate ONLY pandas/numpy/matplotlib code - no other libraries
2. The dataframe is already loaded as `df` variable
3. Save results to `/tmp/result.csv` 
4. Save visualizations to `/tmp/plot1.png`, `/tmp/plot2.png`, etc.
5. Print informative messages about what the code is doing
6. Handle missing data and edge cases gracefully
7. Use `.to_csv()` to save results, `plt.savefig()` for plots
8. DO NOT use `df.show()`, `df.head()`, or display functions - save outputs instead
9. Add comments explaining each step
10. Keep code concise and efficient

## Few-Shot Examples

### Example 1: Basic Aggregation

**Question:** What are the top 5 products by total sales?

**Code:**
```python
import pandas as pd
import matplotlib.pyplot as plt

# Group by product and calculate total sales
product_sales = df.groupby('product_name')['sales_amount'].sum().sort_values(ascending=False).head(5)

# Save results
result = pd.DataFrame({
    'product_name': product_sales.index,
    'total_sales': product_sales.values
})
result.to_csv('/tmp/result.csv', index=False)

# Create visualization
plt.figure(figsize=(10, 6))
plt.bar(product_sales.index, product_sales.values)
plt.xlabel('Product')
plt.ylabel('Total Sales')
plt.title('Top 5 Products by Sales')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('/tmp/plot1.png', dpi=150, bbox_inches='tight')

print(f"Analysis complete: Top 5 products saved to /tmp/result.csv")
print(f"Visualization saved to /tmp/plot1.png")
```

### Example 2: Time Series Analysis

**Question:** Show monthly sales trends for the last 6 months

**Code:**
```python
import pandas as pd
import matplotlib.pyplot as plt

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Filter last 6 months and aggregate by month
df_recent = df[df['date'] >= df['date'].max() - pd.DateOffset(months=6)]
monthly_sales = df_recent.groupby(df_recent['date'].dt.to_period('M'))['sales_amount'].sum()

# Save results
result = pd.DataFrame({
    'month': monthly_sales.index.astype(str),
    'total_sales': monthly_sales.values
})
result.to_csv('/tmp/result.csv', index=False)

# Create line plot
plt.figure(figsize=(12, 6))
plt.plot(range(len(monthly_sales)), monthly_sales.values, marker='o', linewidth=2)
plt.xlabel('Month')
plt.ylabel('Total Sales')
plt.title('Monthly Sales Trend (Last 6 Months)')
plt.xticks(range(len(monthly_sales)), monthly_sales.index.astype(str), rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/tmp/plot1.png', dpi=150, bbox_inches='tight')

print(f"Monthly sales trend saved to /tmp/result.csv and /tmp/plot1.png")
```

### Example 3: Statistical Summary

**Question:** What is the average order value by customer segment?

**Code:**
```python
import pandas as pd
import matplotlib.pyplot as plt

# Calculate average order value by segment
segment_avg = df.groupby('customer_segment')['order_value'].agg(['mean', 'median', 'count'])
segment_avg.columns = ['avg_order_value', 'median_order_value', 'num_orders']

# Save results
segment_avg.to_csv('/tmp/result.csv')

# Create bar chart
fig, ax = plt.subplots(figsize=(10, 6))
x = range(len(segment_avg))
width = 0.35
ax.bar([i - width/2 for i in x], segment_avg['avg_order_value'], width, label='Average')
ax.bar([i + width/2 for i in x], segment_avg['median_order_value'], width, label='Median')
ax.set_xlabel('Customer Segment')
ax.set_ylabel('Order Value')
ax.set_title('Average Order Value by Customer Segment')
ax.set_xticks(x)
ax.set_xticklabels(segment_avg.index, rotation=45, ha='right')
ax.legend()
plt.tight_layout()
plt.savefig('/tmp/plot1.png', dpi=150, bbox_inches='tight')

print(f"Segment analysis saved to /tmp/result.csv and /tmp/plot1.png")
```

## Template for Code Generation

Given a dataset with columns: {columns}
Data types: {dtypes}
Sample data: {sample}

Question: {question}

Generate pandas code that:
1. Analyzes the data to answer the question
2. Saves results to /tmp/result.csv
3. Creates visualization(s) if appropriate
4. Includes error handling and informative print statements
