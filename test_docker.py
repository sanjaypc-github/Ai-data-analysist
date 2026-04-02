import pandas as pd

# Create sample data
data = {
    'product_name': ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard'],
    'order_value': [1000, 500, 300, 400, 100]
}
df = pd.DataFrame(data)

# Group by product_name, sum the order_value, sort, and get the top 4
top_4_products = df.groupby('product_name')['order_value'].sum().sort_values(ascending=False).head(4)

# Print the result
print("Top 4 Products Based on Order Value:")
print(top_4_products)

# Save the result to a CSV file
top_4_products.to_csv('/tmp/result.csv')

print("\nResult saved to /tmp/result.csv")
