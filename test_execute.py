import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv('/data/dataset.csv')

top_6_products = df.groupby('product_name')['order_value'].sum().sort_values(ascending=True).head(6)
print('Top 6 products based on order value (ascending order):\n', top_6_products)
top_6_products_df = top_6_products.to_frame()
top_6_products_df.to_csv('/tmp/result.csv')
print('\nResults saved to /tmp/result.csv')