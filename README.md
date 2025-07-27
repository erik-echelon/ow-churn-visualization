# 🔄 Churn Model Deployment & Visualization

A comprehensive Streamlit dashboard for analyzing customer churn risk data, providing both high-level risk overview and detailed individual customer analysis.

## 📋 Overview

This application provides a Customer Level Operational Dashboard designed for analyzing churn risk across your customer base. It features two main views:

1. **Top Risk Customers**: Table view of the 10 highest-risk customers
2. **Individual Customer Analysis**: Detailed dashboard for specific customer deep-dive

## 🚀 Features

### Tab 1: Top Risk Customers
- **Risk Ranking**: Customers ranked by `final_raw_prediction × revenue_weight`
- **Compact Table View**: 10 columns with shortened headers for optimal viewing
- **Color-Coded Alerts**: Visual indicators for contract status and alerts
- **Click Navigation**: Click any customer to view detailed analysis
- **Summary Metrics**: Total revenue at risk, average risk ratios, and alert counts

### Tab 2: Individual Customer Analysis
- **Prominent Customer ID**: Large headline with customer code and name
- **Interactive Risk Gauge**: Visual churn risk ratio display
- **Four Key Sections**:
  - Customer Attributes
  - Key Indicators  
  - Multipliers & Alerts
  - Recent Customer Interactions
- **Markdown Content**: Displays detailed churn analysis and relationship status
- **Expandable Metrics**: Additional technical metrics in collapsible section

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Required Packages
```bash
pip install streamlit pandas numpy plotly
```

### Alternative Installation
```bash
pip install -r requirements.txt
```

## 📁 Usage

### 1. Run the Application
```bash
streamlit run app.py
```

### 2. Upload Your Data
- Click "Browse files" in the sidebar
- Upload a CSV file in the required format
- The application will automatically process and display your data

### 3. Navigate the Dashboard
- **Tab 1**: View top 10 risk customers, click any row to select
- **Tab 2**: View detailed analysis (automatically loads selected customer from Tab 1)

## 📊 Data Format Requirements

Your CSV file must contain the following columns:

### Core Customer Data
- `customer_cd`: Customer code/ID
- `customer_nm`: Customer name
- `customer_status_txt`: Customer status (Active, Inactive, etc.)

### Risk Metrics
- `final_raw_prediction`: Model prediction score
- `churn_risk_ratio`: Risk ratio (0-1)
- `prediction_percentile`: Risk percentile ranking
- `revenue_weight`: Revenue weight factor
- `revenue_weight_dollars`: Revenue weight in dollars

### Contract & Activity Data
- `has_contract`: Boolean - customer has active contract
- `last_contract_end_date`: Contract expiration date
- `contract_end_less_than_180_days_alert`: Boolean - contract expiring soon
- `days_since_last_invoice`: Days since last invoice

### Financial Metrics
- `margin_pct_mean_35days`: Profit margin percentage
- `invoiced_amount_sum_180days_raw`: Total invoiced amount (6 months)
- `invoiced_amount_sum_180days_raw_delta`: Change in invoiced amount
- `past_due_balance_mean_180days`: Past due balance
- `past_due_balance_mean_180days_delta`: Change in past due balance
- `monthly_value_mean_28days_raw`: Monthly value average
- `recurring_rev_mean_28days`: Recurring revenue

### Support & Quality Metrics
- `ticket_count_sum_180days`: Ticket count (6 months)
- `cum_avg_days_to_ticket_close`: Average days to close tickets
- `qav_score_category`: QAV score category
- `nps_alert_category`: NPS alert status
- `provider_changed_alert`: Boolean - provider change detected

### Analysis Content (Markdown)
- `churn_analysis`: Detailed markdown analysis of churn risk
- `customer_relationship_status`: Markdown summary of customer relationship

## 🎨 Color Coding Logic

### Contract Status
- 🟢 **Green**: Has contract (good for retention)
- 🟠 **Orange**: No contract (retention risk)

### Alert Columns  
- 🟢 **Green**: No alerts (good status)
- 🟠 **Orange**: Alert present (requires attention)

## 🔧 Configuration

### Risk Gauge Thresholds
- **Green Zone**: 0.0 - 0.3 (Low risk)
- **Yellow Zone**: 0.3 - 0.7 (Medium risk)  
- **Red Zone**: 0.7 - 1.0 (High risk)
- **Threshold Line**: 0.8 (Critical risk level)

### Table Display
- **Height**: 400px
- **Selection**: Single-row selection enabled
- **Formatting**: Conditional formatting for boolean values

## 📈 Business Use Cases

### For Customer Success Teams
- Identify highest-risk customers requiring immediate attention
- Prioritize outreach based on revenue impact
- Track contract expiration and renewal opportunities

### For Account Management
- Deep-dive analysis of individual customer health
- Historical trend analysis and risk factors
- Revenue protection and expansion planning

### For Executive Reporting
- High-level risk overview with key metrics
- Total revenue at risk calculations
- Strategic customer retention insights

## 🚨 Troubleshooting

### Common Issues

**File Upload Errors**
- Ensure CSV has all required columns
- Check for proper encoding (UTF-8 recommended)
- Verify boolean columns contain True/False values

**Display Issues**
- If table doesn't fit: columns are optimized for standard screens
- Use browser zoom if needed
- Expandable sections available for additional details

**Navigation Issues**
- Click directly on table rows, not headers
- Switch tabs manually after row selection
- Selection state is preserved between tabs

## 🏗️ Technical Architecture

- **Frontend**: Streamlit web framework
- **Visualization**: Plotly for interactive charts
- **Data Processing**: Pandas for data manipulation
- **Styling**: Custom CSS via Streamlit styling API

## 📝 Sample Data

```csv
customer_cd,customer_nm,final_raw_prediction,revenue_weight,churn_risk_ratio,...
C1000010,"1 & 1 Ionos",0.040108371,9.300703791,0.638875857,...
```

## 🤝 Contributing

For feature requests or bug reports, please contact the development team.

## 📄 License

© 2025 Echelon DS, Inc. Confidential, Proprietary, & Trade Secret.

---

*Customer Level Operational Dashboard - Echelon DS*