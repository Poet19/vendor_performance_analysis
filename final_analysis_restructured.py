import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import sqlite3
from scipy.stats import ttest_ind
import scipy.stats as stats
import logging
import os

# === 1. IMPORTS AND CONFIGURATION ===
# pd: Pandas library for data manipulation and analysis.
# np: NumPy for numerical operations.
# plt & sns: Matplotlib and Seaborn for visualizations.
# warnings: Suppress non-critical warnings for cleaner output.
# sqlite3: Connect to SQLite database.
# stats & ttest_ind: SciPy for statistical tests.
# Suppress all warnings to focus on analysis output.
warnings.filterwarnings('ignore')

# === 2. LOAD VENDOR SUMMARY DATA ===
# sqlite3.connect('inventory.db'): Creates a connection to the local SQLite database 'inventory.db'.
conn = sqlite3.connect('inventory.db')

# pd.read_sql_query('SELECT * FROM vendor_summary', conn): Executes SQL query to fetch all data from 'vendor_summary' table and loads it into a Pandas DataFrame 'df'.
df = pd.read_sql_query('SELECT * FROM vendor_summary', conn)
print("Dataset loaded. First 5 rows:")
print(df.head())

# === 3. EXPLORE DATA SUMMARY ===
# df.describe().transpose(): Computes summary statistics (count, mean, std, min, max, quartiles) for all numerical columns and transposes for better readability.
print("\nSummary Statistics for Numerical Columns:")
print(df.describe().transpose())

# === 4. VISUALIZE DISTRIBUTIONS ===
# df.select_dtypes(include=np.number).columns: Identifies all columns with numerical data types.
numerical_cols = df.select_dtypes(include=np.number).columns

# plt.figure(figsize=(15, 10)): Creates a figure canvas of size 15x10 inches for subplots.
plt.figure(figsize=(15, 10))  # plt.figure(figsize=(15, 10)): Creates a figure canvas of size 15x10 inches for subplots.
# Loop over numerical columns to create histograms.
for i, col in enumerate(numerical_cols):  # for i, col in enumerate(numerical_cols): Iterates over each numerical column with index.
    # plt.subplot(4, 4, i + 1): Creates a subplot grid position for each column.
    plt.subplot(4, 4, i + 1)  # plt.subplot(4, 4, i + 1): Creates a subplot grid position for each column.
    # sns.histplot(df[col], kde=True, bins=30): Plots histogram with kernel density estimate (KDE) curve, 30 bins.
    sns.histplot(df[col], kde=True, bins=30)  # sns.histplot(df[col], kde=True, bins=30): Plots histogram with kernel density estimate (KDE) curve, 30 bins.
    # plt.title(...): Sets title for each subplot.
    plt.title(f'Distribution of {col}')  # plt.title(f'Distribution of {col}'): Sets title for each subplot.
# plt.tight_layout(): Adjusts subplot spacing automatically.
plt.tight_layout()  # plt.tight_layout(): Adjusts subplot spacing automatically.
plt.show()  # plt.show(): Displays the plot.

# === 5. DETECT OUTLIERS ===
# plt.figure(figsize=(15, 10)): New figure for boxplots.
plt.figure(figsize=(15, 10))  # plt.figure(figsize=(15, 10)): New figure for boxplots.
for i, col in enumerate(numerical_cols):  # for i, col in enumerate(numerical_cols): Iterates over each numerical column.
    plt.subplot(4, 4, i + 1)  # plt.subplot(4, 4, i + 1): Position in subplot grid.
    # sns.boxplot(x=df[col]): Creates boxplot to visualize outliers (points beyond whiskers).
    sns.boxplot(x=df[col])  # sns.boxplot(x=df[col]): Creates boxplot to visualize outliers (points beyond whiskers).
    plt.title(f'Box Plot of {col}')  # plt.title(f'Box Plot of {col}'): Sets subplot title.
plt.tight_layout()  # plt.tight_layout(): Adjusts layout.
plt.show()  # plt.show(): Displays the plot.

# === 6. ANALYZE AND REMOVE OUTLIERS ===
# Key observations from summary and plots (no code change):
# - GrossProfit min -52k: Some losses from high costs/low sales.
# - ProfitMargin min -inf: Zero revenue cases.
# - TotalSalesQuantity min 0: Unsold stock.
# - High std in prices/freight: Bulk/premium items.
# - StockTurnover 0-274: Slow vs fast movers (>1 = good).

# pd.read_sql_query(... WHERE ...): Reloads data filtering out inconsistent outliers (positive profit/sales).
df = pd.read_sql_query('SELECT * FROM vendor_summary WHERE GrossProfit > 0 AND ProfitMargin > 0 AND TotalSalesQuantity > 0; ', conn)
print("\nData after outlier removal:")
print(df)

# Recheck summary.
print(df.describe().transpose())

# === 7. CATEGORICAL ANALYSIS ===
# ['VendorNumber']: List of categorical columns to analyze (top 10 only).
categorical_cols = ['VendorNumber']

plt.figure(figsize=(12,5))  # plt.figure(figsize=(12,5)): Figure for categorical plots.
for i, col in enumerate(categorical_cols):  # Loop over categorical columns.
    plt.subplot(1, 2, i + 1)  # plt.subplot(1, 2, i + 1): Subplot position.
    # sns.countplot(y=df[col], order=...[:10]): Horizontal bar count plot, top 10 by frequency.
    sns.countplot(y=df[col], order=df[col].value_counts().index[:10])  # sns.countplot(y=df[col], order=df[col].value_counts().index[:10]): Horizontal bar count plot, top 10 by frequency.
    plt.title(f'Count Plot of {col}')  # plt.title(f'Count Plot of {col}'): Subplot title.
plt.tight_layout()  # plt.tight_layout(): Adjust layout.
plt.show()  # plt.show(): Display plot.

# === 8. CORRELATION HEATMAP ===
# df[numerical_cols].corr(): Computes Pearson correlation matrix for numerical columns.
plt.figure(figsize=(12, 8))  # plt.figure(figsize=(12, 8)): Figure for heatmap.
correlation_matrix = df[numerical_cols].corr()  # df[numerical_cols].corr(): Computes Pearson correlation matrix for numerical columns.
# sns.heatmap(..., annot=True, cmap='coolwarm'): Visualizes correlations with numbers, blue-red colormap.
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)  # sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5): Visualizes correlations with numbers, blue-red colormap.
plt.title('Correlation Heatmap')  # plt.title('Correlation Heatmap'): Sets title.
plt.show()  # plt.show(): Displays plot.

# Insight: Strong positive correlation between Gross Profit, Profit Margin, and Vendor Performance Score. Higher profitability links to better performance.

# === 9. RESEARCH Q1: LOW SALES / HIGH MARGIN BRANDS (Promotional Targets) ===
# df.groupby("Brand").agg({...}): Groups by Brand, sums sales dollars, averages margin.
brand_performance = (
    df.groupby("Brand")
    .agg(TotalSalesDollars=('TotalSalesDollars','sum'),
         ProfitMargin=('ProfitMargin','mean'))
    .reset_index()
)
print(brand_performance)

# Quantiles for thresholds: Bottom 15% sales, top 85% margin.
low_threshold_sales = brand_performance['TotalSalesDollars'].quantile(0.15)
high_threshold_profit = brand_performance['ProfitMargin'].quantile(0.85)
print("Low Sales Threshold:", low_threshold_sales)
print("High Profit Threshold:", high_threshold_profit)

# Filter target brands.
target_brands = brand_performance[
    (brand_performance['TotalSalesDollars'] <= low_threshold_sales) &
    (brand_performance['ProfitMargin'] >= high_threshold_profit)
]

# Scatterplot with thresholds.
plt.figure(figsize=(10, 6))  # plt.figure(figsize=(10, 6)): Figure for scatterplot.
sns.scatterplot(data=brand_performance, x='TotalSalesDollars', y='ProfitMargin', color='blue', label='All Brands', alpha=0.2)  # sns.scatterplot(...): Scatter all brands (blue, transparent).
sns.scatterplot(data=target_brands, x='TotalSalesDollars', y='ProfitMargin', color='red', label='Target Brands')  # sns.scatterplot(...): Target brands highlighted (red).
plt.axhline(y=high_threshold_profit, linestyle='--', color='black', label='High Margin Threshold')  # plt.axhline(...): Horizontal threshold line.
plt.axvline(x=low_threshold_sales, linestyle='--', color='black', label='Low Sales Threshold')  # plt.axvline(...): Vertical threshold line.
plt.xlabel("Total Sales ($)")  # plt.xlabel(...): X-axis label.
plt.ylabel("Profit Margin (%)")  # plt.ylabel(...): Y-axis label.
plt.title("Brands for Promotional or Pricing Adjustments")  # plt.title(...): Plot title.
plt.legend()  # plt.legend(): Shows legend.
plt.grid(True)  # plt.grid(True): Adds grid.
plt.show()  # plt.show(): Displays plot.

# Insight: Target brands have high margins but low sales - ideal for promotions/pricing tweaks without hurting profitability.

# === 10. RESEARCH Q2: TOP PERFORMERS BY SALES ===
# Top 10 Vendors and Brands (sum sales).
top_vendors = df.groupby('VendorNumber')['TotalSalesDollars'].sum().sort_values(ascending=False).head(10)
top_brands = df.groupby('Brand')['TotalSalesDollars'].sum().sort_values(ascending=False).head(10)
print("Top 10 Vendors by Sales:\n", top_vendors)
print("\nTop 10 Brands by Sales:\n", top_brands)

# Format function for Indian number style.
def format_indian(value):
    if value >= 100000:
        return f"{value/100000:.1f}L"
    elif value >= 1000:
        return f"{value/1000:.1f}K"
    else:
        return str(int(value))

plt.figure(figsize=(15,5))
# Vendors barplot.
plt.subplot(1,2,1)
ax1 = sns.barplot(y=top_vendors.index.astype(str), x=top_vendors.values, palette="Blues_r")
plt.title("Top 10 Vendors by Sales")
for bar in ax1.patches:
    ax1.text(bar.get_width() + (bar.get_width()*0.02), bar.get_y() + bar.get_height()/2, format_indian(bar.get_width()), ha='left', va='center', fontsize=10)
# Brands barplot.
plt.subplot(1,2,2)
ax2 = sns.barplot(y=top_brands.index.astype(str), x=top_brands.values, palette="Reds_r")
plt.title("Top 10 Brands by Sales")
for bar in ax2.patches:
    ax2.text(bar.get_width() + (bar.get_width()*0.02), bar.get_y() + bar.get_height()/2, format_indian(bar.get_width()), ha='left', va='center', fontsize=10)
plt.tight_layout()
plt.show()

# Insight: Identifies sales drivers. Analyze their strategies (e.g., pricing, volume) for replication.

# === 11. RESEARCH Q3: VENDOR PURCHASE PARETO ===
# Groupby Vendor: sum purchase, profit, sales; calc % contribution.
vendor_performance = df.groupby('VendorNumber').agg({
    'TotalPurchaseDollars': 'sum',
    'GrossProfit': 'sum',
    'TotalSalesDollars': 'sum'
}).reset_index()
vendor_performance['PurchaseContribution%'] = (vendor_performance['TotalPurchaseDollars'] / vendor_performance['TotalPurchaseDollars'].sum()) * 100
vendor_performance = vendor_performance.sort_values('PurchaseContribution%', ascending=False)
top_vendors = vendor_performance.head(10)
top_vendors['Cumulative_Contribution%'] = top_vendors['PurchaseContribution%'].cumsum()

# Pareto chart.
fig, ax1 = plt.subplots(figsize=(10,6))
sns.barplot(x=top_vendors['VendorNumber'].astype(str), y=top_vendors['PurchaseContribution%'], palette="mako", ax=ax1)
for i, value in enumerate(top_vendors['PurchaseContribution%']):
    ax1.text(i, value + 0.3, f"{value:.1f}%", ha='center')
ax1.set_ylabel("Purchase Contribution %", color="blue")
ax1.set_xlabel("Vendors")
ax1.set_title("Pareto Chart: Vendor Contribution to Total Purchases")
ax1.tick_params(axis='x', rotation=90)
ax2 = ax1.twinx()
ax2.plot(top_vendors['VendorNumber'].astype(str), top_vendors['Cumulative_Contribution%'], color="red", marker="o", linestyle="dashed", label="Cumulative Contribution %")
ax2.set_ylabel("Cumulative Contribution %", color="red")
ax2.axhline(y=100, color='gray', linestyle='dashed', alpha=0.7)
plt.tight_layout()
plt.show()

# Insight: Small vendor group drives most spend → supplier concentration risk.

# === 12. RESEARCH Q4: TOP VENDORS DONUT CHART ===
# Reuse vendor_performance, top 10 contribution.
vendor_performance = df.groupby('VendorNumber').agg({'TotalPurchaseDollars':'sum'}).reset_index()
vendor_performance['Purchase_Contribution%'] = (vendor_performance['TotalPurchaseDollars'] / vendor_performance['TotalPurchaseDollars'].sum()) * 100
vendor_performance = vendor_performance.sort_values('Purchase_Contribution%', ascending=False)
top_vendors_pie = vendor_performance.head(10)
total_contribution = round(top_vendors_pie['Purchase_Contribution%'].sum(), 2)
print(f"Total Purchase Contribution of top 10 vendors: {total_contribution}%")

# Donut data.
vendors = list(top_vendors_pie['VendorNumber'].astype(str).values)
purchase_contributions = list(top_vendors_pie['Purchase_Contribution%'].values)
remaining_contribution = 100 - total_contribution
vendors.append("Other Vendors")
purchase_contributions.append(remaining_contribution)

# Pie chart as donut.
fig, ax = plt.subplots(figsize=(8,8))
wedges, texts, autotexts = ax.pie(purchase_contributions, labels=vendors, autopct='%1.1f%%', startangle=140, pctdistance=0.85)
centre_circle = plt.Circle((0,0),0.70,fc='white')
fig.gca().add_artist(centre_circle)
plt.text(0,0, f"Top 10\n{total_contribution:.2f}%", fontsize=14, fontweight='bold', ha='center')
plt.title("Top 10 Vendors Purchase Contribution (%)")
plt.show()

# Insight: Top 10 vendors ~66% of procurement → Heavy reliance, monitor for disruptions.

# === 13. RESEARCH Q5: BULK BUYING IMPACT ===
# df['UnitPurchasePrice'] = ... : Calculates unit price.
df['UnitPurchasePrice'] = df['TotalPurchaseDollars'] / df['TotalPurchaseQuantity']
# pd.qcut(..., q=3): Divides quantity into 3 equal-sized bins: Small/Medium/Large.
df['OrderSize'] = pd.qcut(df['TotalPurchaseQuantity'], q=3, labels=['Small', 'Medium', 'Large'])
# Groupby mean unit price.
order_price_analysis = df.groupby('OrderSize')['UnitPurchasePrice'].mean()
print(order_price_analysis)

# Boxplot.
plt.figure(figsize=(10,6))
sns.boxplot(data=df, x='OrderSize', y='UnitPurchasePrice', palette='Set2')
plt.title("Impact of Bulk Purchasing on Unit Price")
plt.xlabel("Order Size")
plt.ylabel("Average Unit Purchase Price")
plt.show()

# Insight: Larger orders → lower unit prices (economies of scale). Balance with inventory costs for optimal volume.

# === 14. RESEARCH Q6: LOW INVENTORY TURNOVER ===
# df['StockTurnover'] < 1: Filters slow movers (<1 = stock sells less than once/year).
low_turnover_vendors = (
    df[df['StockTurnover'] < 1]
    .groupby('VendorNumber')[['StockTurnover']]
    .mean()
    .sort_values('StockTurnover', ascending=True)
    .head(10)
)
print(low_turnover_vendors)

plt.figure(figsize=(10,6))
sns.barplot(x=low_turnover_vendors['StockTurnover'], y=low_turnover_vendors.index.astype(str), palette="Reds_r")
plt.title("Top Vendors with Lowest Inventory Turnover")
plt.xlabel("Stock Turnover")
plt.ylabel("Vendor Number")
plt.show()

plt.figure(figsize=(8,5))
sns.histplot(df['StockTurnover'], bins=30, kde=True)
plt.title("Distribution of Stock Turnover")
plt.xlabel("Stock Turnover")
plt.ylabel("Frequency")
plt.show()

# Insight: Low turnover = excess stock/slow sales. Improve forecasting, promotions, or reduce orders.

# === 15. RESEARCH Q7: LOCKED CAPITAL IN UNSOLD INVENTORY ===
# df["UnsoldInventoryValue"] = (purchase qty - sales qty) * purchase price.
df["UnsoldInventoryValue"] = (df["TotalPurchaseQuantity"] - df["TotalSalesQuantity"]) * df["PurchasePrice"]
total_unsold = df["UnsoldInventoryValue"].sum()
print("Total Capital Locked in Unsold Inventory:", total_unsold)

# Groupby vendor sum.
inventory_value_per_vendor = df.groupby("VendorNumber")["UnsoldInventoryValue"].sum().reset_index()
inventory_value_per_vendor = inventory_value_per_vendor.sort_values("UnsoldInventoryValue", ascending=False)
print(inventory_value_per_vendor.head(10))

# Format func reused.
top_inventory_vendors = inventory_value_per_vendor.head(10)
plt.figure(figsize=(10,6))
ax = sns.barplot(data=top_inventory_vendors, x="UnsoldInventoryValue", y="VendorNumber", palette="Oranges_r")
def format_axis(value, pos):
    if value >= 100000:
        return f"{value/100000:.1f}L"
    elif value >= 1000:
        return f"{value/1000:.1f}K"
    else:
        return str(int(value))
from matplotlib.ticker import FuncFormatter
ax.xaxis.set_major_formatter(FuncFormatter(format_axis))
plt.title("Top Vendors with Highest Capital Locked in Unsold Inventory")
plt.xlabel("Unsold Inventory Value")
plt.ylabel("Vendor")
plt.tight_layout()
plt.show()

# Insight: Significant capital tied up; top vendors dominate. Optimize procurement to free cash.

# === 16. HYPOTHESIS TESTING: CONFIDENCE INTERVALS ===
# Quantiles for top/low sales.
top_threshold = df['TotalSalesDollars'].quantile(0.75)
low_threshold = df['TotalSalesDollars'].quantile(0.25)
top_vendors = df[df['TotalSalesDollars'] >= top_threshold]['ProfitMargin'].dropna()
low_vendors = df[df['TotalSalesDollars'] <= low_threshold]['ProfitMargin'].dropna()

# confidence_interval func: Computes 95% CI using t-distribution.
def confidence_interval(data, confidence=0.95):
    mean_val = np.mean(data)
    std_err = stats.sem(data)
    t_critical = stats.t.ppf((1 + confidence) / 2, df=len(data)-1)
    margin_error = t_critical * std_err
    lower = mean_val - margin_error
    upper = mean_val + margin_error
    return mean_val, lower, upper

top_mean, top_lower, top_upper = confidence_interval(top_vendors)
low_mean, low_lower, low_upper = confidence_interval(low_vendors)
print(f"Top Vendors 95% CI: ({top_lower:.2f}, {top_upper:.2f}), Mean: {top_mean:.2f}")
print(f"Low Vendors 95% CI: ({low_lower:.2f}, {low_upper:.2f}), Mean: {low_mean:.2f}")

# Histplot comparison.
plt.figure(figsize=(12,6))
sns.histplot(top_vendors, kde=True, color="blue", bins=30, alpha=0.5, label="Top Vendors")
sns.histplot(low_vendors, kde=True, color="red", bins=30, alpha=0.5, label="Low Vendors")
plt.axvline(top_mean, color='blue', linestyle='--', label=f"Top Mean: {top_mean:.2f}")
plt.axvline(low_mean, color='red', linestyle='--', label=f"Low Mean: {low_mean:.2f}")
plt.axvline(top_lower, color='blue', linestyle=':')
plt.axvline(top_upper, color='blue', linestyle=':')
plt.axvline(low_lower, color='red', linestyle=':')
plt.axvline(low_upper, color='red', linestyle=':')
plt.title("Confidence Interval Comparison: Top vs Low Vendors (Profit Margin)")
plt.xlabel("Profit Margin (%)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.show()

# Insight: Top vendors higher margins (52.83% vs 46.87%); non-overlapping CIs → scale benefits.

# === 17. HYPOTHESIS TESTING: T-TEST ===
# Reuse groups.
t_stat, p_value = stats.ttest_ind(top_vendors, low_vendors, equal_var=False)
print(f"T-Statistic: {t_stat:.4f}")
print(f"P-Value: {p_value:.4f}")
if p_value < 0.05:
    print("Reject H0: Significant difference in profit margins between top/low vendors.")
else:
    print("Fail to Reject H0: No significant difference.")

# Insight: Statistically significant → High sales vendors more profitable.

# === 18. CLEANUP ===
# conn.close(): Closes database connection to free resources.
conn.close()

print("\nFinal Analysis Complete: File restructured with comments, insights refined, duplicates removed.")




# === Export Data for Power BI ===

brand_performance.to_csv("BrandPerformance.csv", index=False)

low_turnover_vendors.to_csv("LowTurnoverVendor.csv", index=False)

vendor_performance.to_csv("PurchaseContribution.csv", index=False)

inventory_value_per_vendor.to_csv("VendorSalesSummary.csv", index=False)

print("CSV files exported for Power BI.")