# 📊 Vendor Performance Analysis Dashboard

> **End-to-end supply chain intelligence project** — from raw SQL data to interactive Power BI dashboard, powered by Python analytics and statistical testing.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-Statistics-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)

---

## 🖼️ Dashboard Preview

![Vendor Performance Dashboard](./assets/dashboard_preview.png)

> *Dark-themed Power BI dashboard — 7 interactive visuals, 4 KPI cards, full horizontal layout*

---

## 📌 Project Overview

This project performs a **comprehensive vendor performance analysis** for a retail supply chain operation, covering **48 vendors** and **368 brand SKUs**. The goal was to transform raw transactional data into actionable business intelligence across **7 research areas**.

### Key Business Questions Answered

| # | Research Question | Technique Used |
|---|---|---|
| Q1 | Which brands have high margins but low sales? (Promotional targets) | Quantile segmentation + Scatter plot |
| Q2 | Who are the top 10 revenue-generating vendors and brands? | GroupBy aggregation + Bar charts |
| Q3 | Does a small vendor group drive most procurement spend? | Pareto analysis + Cumulative line chart |
| Q4 | What is each vendor's % contribution to total purchases? | Normalization + Donut chart |
| Q5 | Do bulk orders result in lower unit prices? | pd.qcut() + Box plot |
| Q6 | Which vendors have critically low stock turnover? | Filter + Ranking |
| Q7 | How much capital is locked in unsold inventory? | Derived metric + Horizontal bar |

---

## 📊 Key Findings

```
💰 Total Sales Revenue     →   $3.98M
🛒 Total Procurement Spend →   $1.95M
📈 Avg Profit Margin       →   40.16%
⚠️  Unsold Capital Locked   →  -$768.94K
```

- 🔴 **Top 3 vendors** (4425, 9165, 9552) account for **49.2% of total spend** — high concentration risk
- 🟢 **Brand 23353** leads revenue at **$146,180** with a **51.18% profit margin**
- 🔴 **Vendor 9165** holds **-$149,629** in unsold inventory despite being the 2nd largest supplier
- 📊 **170 of 368 brands** (46%) operate in the **20–40% profit margin** tier
- ✅ **Statistical test confirms**: High-sales vendors earn significantly higher margins (52.83% vs 46.87%, p < 0.05)

---

## 🗂️ Project Structure

```
vendor-performance-analysis/
│
├── 📄 final_analysis_restructured.py   # Main Python analysis script
│
├── 📁 data/
│   ├── BrandPerformance.csv            # 368 brands — Sales & Profit Margin
│   ├── PurchaseContribution.csv        # 48 vendors — Purchase spend & contribution %
│   ├── VendorSalesSummary.csv          # 48 vendors — Unsold inventory values
│   └── LowTurnoverVendor.csv           # 10 vendors — Stock turnover metrics
│
├── 📁 plots/
│   ├── histograms.png                  # Distribution analysis — all numerical vars
│   ├── box plaots.png                  # Outlier detection box plots
│   ├── co relation heatmap.png         # Pearson correlation matrix
│   ├── scatter plot.png                # Sales vs Profit Margin — Q1
│   ├── ans 2.png                       # Top 10 vendors & brands — Q2
│   ├── ams 3.png                       # Pareto chart — Q3
│   ├── 4.png                           # Purchase contribution donut — Q4
│   ├── 5.png                           # Bulk buying impact box plot — Q5
│   ├── 6.png                           # Low turnover bar chart — Q6
│   ├── 6.1.png                         # Stock turnover distribution — Q6
│   └── HT.png                          # Hypothesis testing CI comparison — Q7
│
├── 📁 powerbi/
│   ├── VendorPerformanceDashboard.pbix # Power BI dashboard file
│   └── VendorDark.json                 # Custom dark theme JSON
│
├── 📄 VendorPerformanceReport.docx     # Full industry-level analysis report
└── 📄 README.md
```

---

## ⚙️ Tech Stack

| Layer | Tools |
|---|---|
| **Data Storage** | SQLite via `sqlite3` |
| **Data Processing** | Python — `pandas`, `numpy` |
| **Visualization** | `matplotlib`, `seaborn` |
| **Statistical Testing** | `scipy.stats`, `ttest_ind` |
| **BI Dashboard** | Microsoft Power BI |
| **Theme** | Custom JSON — Dark Navy (`#0A0E1A`) |

---

## 🚀 How to Run

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn scipy
```

### Steps

**1. Set up the SQLite database**
```bash
# The script expects inventory.db with a vendor_summary table
# Make sure your SQLite DB is in the same directory as the script
```

**2. Run the analysis**
```bash
python final_analysis_restructured.py
```

**3. Output files generated automatically**
```
BrandPerformance.csv
PurchaseContribution.csv
VendorSalesSummary.csv
LowTurnoverVendor.csv
```

**4. Open Power BI dashboard**
- Load all 4 CSV files into Power BI Desktop
- Import `VendorDark.json` via View → Themes → Browse for themes
- Open `VendorPerformanceDashboard.pbix`

---

## 📈 Power BI Dashboard Features

| Visual | Chart Type | Key Insight |
|---|---|---|
| Total Sales / Purchases / Margin / Unsold Capital | KPI Cards | At-a-glance business health |
| Purchase Contribution % | Donut Chart | Vendor spend distribution |
| Top 10 Brands by Revenue | Horizontal Bar | Revenue leaders |
| Unsold Inventory by Vendor | Horizontal Bar (Red) | Capital at risk |
| Profit Margin Distribution | Column Chart | Brand performance tiers |
| Sales vs Profit Margin | Scatter Plot | Volume-profitability tradeoff |
| Avg Stock Turnover | Gauge | Inventory health indicator |

---

## 🧪 Statistical Analysis

### Hypothesis Test: Do high-sales vendors earn higher margins?

```
H₀: No significant difference in profit margins between high and low sales vendors
H₁: High-sales vendors have significantly higher profit margins

Test: Welch's two-sample t-test (unequal variances)
Significance Level: α = 0.05

Results:
  High-Sales Vendors Mean Margin  →  52.83%
  Low-Sales Vendors Mean Margin   →  46.87%
  P-Value                         →  < 0.05
  Decision                        →  ✅ Reject H₀
```

**Conclusion:** Statistically significant difference confirmed. High-revenue vendors demonstrably operate at higher profit margins — validating the case for scaling procurement from top-performing vendors.

---

## 💡 Business Recommendations

### 🔴 Immediate (0–30 days)
- Pause new orders from vendors **9165** and **4425** until unsold stock clears
- Launch targeted promotions for **high-margin, low-sales brands** identified in Q1
- Negotiate better bulk pricing terms with top 3 vendors

### 🟡 Medium-Term (1–3 months)
- **Diversify vendor base** — reduce top-3 concentration from 49.2%
- Implement demand forecasting for SKUs with turnover < 0.75
- Scale procurement from brands **16370** and **23258** (highest margin + revenue)

### 🟢 Long-Term (3–6 months)
- Build real-time Power BI connected to live DB for continuous monitoring
- Develop a **vendor scorecard system** (Sales + Margin + Turnover + Unsold)
- Apply **ML clustering** to segment vendors into performance tiers

---

## 📚 Skills Demonstrated

`Python` · `SQL` · `SQLite` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `SciPy` · `Hypothesis Testing` · `Confidence Intervals` · `Power BI` · `DAX` · `Data Cleaning` · `EDA` · `Data Visualization` · `Supply Chain Analytics` · `Business Intelligence`

---

## 👩‍💻 Author

**Gunjan**
B.Tech Computer Science Engineering | Chandigarh University — Batch 2021–2025
CGPA: 8.2 | Specialization: Data Analytics

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/your-profile)
[![GitHub](https://img.shields.io/badge/GitHub-Portfolio-181717?style=flat&logo=github)](https://github.com/your-username)

---

*⭐ If this project helped you, please star the repository!*
