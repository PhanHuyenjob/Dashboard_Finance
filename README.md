# 📊 Financial Dashboard (2020–2024)

This is a **Financial Analysis Dashboard** built with `Python` and `Dash`, designed to visualize key financial data of companies from **2020 to 2024**. The dashboard uses periodic financial report data (CSV files) and presents interactive charts and metrics to support investment and analysis decisions.

> 👨‍💼 Ideal for investors, data analysts, and finance/accounting students.

---

## 🖼 Dashboard Preview

![Dashboard Report](![image](https://github.com/user-attachments/assets/2e2fccf9-d33a-4a81-880a-45a9fc4b7024)
)


---

## ⚙️ Key Features

### 🎯 Financial Overview
- Metrics: **Free Cash Flow**, **Net Revenue**, **Net Profit After Tax**, **Gross Profit**.
- Balance sheet items: **Total Assets**, **Cash & Cash Equivalents**, **Liabilities**, **Financial Expenses**, and more.
- Year-over-year comparisons shown with percentage change and directional arrows.

### 📉 Financial Ratios
- Includes **Quick Ratio**, **Cash Ratio**, **D/E (Debt-to-Equity)**, **DOH (Days of Inventory on Hand)**, **ROA**, and **ROE**.
- Color-coded indicators for visualizing positive or negative trends.

### 📊 Charts
- **Top 10 Companies by Net Revenue** (2024).
- **Top 10 Companies by Gross Profit** (2024).
- **Net Revenue Trends (2020–2024)** for selected stock codes.

### 🔍 Interactive Features
- Dropdown menus for selecting **stock ticker**, **comparison year**, and **base year**.
- All metrics and visuals auto-update based on user selection.

---

## 🧾 Input Data

- Format: CSV files with financial statement data.
- Content:
  - Revenue, profit, cash flow, assets, liabilities, equity, and financial ratios.
  - Period: **2020–2024**.
  - Focus sectors: **Food & Beverage industry** and related sub-sectors.

> 🔒 **Note**: Data files are not included for privacy reasons. You can plug in your own CSV data into the `data/` folder to test the dashboard.

---

## 🔧 Technologies Used

| Tool       | Purpose                                |
|------------|----------------------------------------|
| `Python`   | Core programming language               |
| `Dash`     | Framework for building interactive UIs |
| `Plotly`   | High-quality visualization library      |
| `Pandas`   | Data manipulation and transformation    |

---

## 🚀 How to Run the Dashboard

1. **Install dependencies**:

```bash
pip install dash pandas plotly
