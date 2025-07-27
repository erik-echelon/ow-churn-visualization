import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(
    page_title="Churn Model Deployment & Visualization", 
    page_icon="📊", 
    layout="wide"
)

# Title and header
st.title("🔄 Churn Model Deployment & Visualization")
st.markdown("---")

# File upload section
st.sidebar.header("📁 Data Upload")
uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV file", 
    type=['csv'],
    help="Upload a CSV file in the format of model_scores_final.csv"
)

if uploaded_file is not None:
    # Load data
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success(f"✅ File uploaded successfully! ({len(df)} rows)")
        
        # Create dropdown options
        df['dropdown_option'] = df['customer_cd'].astype(str) + ': ' + df['customer_nm'].astype(str)
        
        # Calculate weighted risk score for ranking
        df['weighted_risk_score'] = df['final_raw_prediction'] * df['revenue_weight']
        
        # Initialize session state for selected customer
        if 'selected_customer_from_table' not in st.session_state:
            st.session_state.selected_customer_from_table = None
        
        # Create tabs
        tab1, tab2 = st.tabs(["📊 Top Risk Customers", "🔍 Individual Customer Analysis"])
        
        # TAB 1: Top Risk Customers Table
        with tab1:
            st.header("🚨 Top 10 Highest Risk Customers")
            st.markdown("*Ranked by Final Raw Prediction × Revenue Weight*")
            st.markdown("💡 **Click on a customer name to view detailed analysis in Tab 2**")
            
            # Get top 10 highest risk customers
            top_risk_customers = df.nlargest(10, 'weighted_risk_score').copy()
            
            # Prepare the display table with shorter column names
            display_df = pd.DataFrame()
            display_df['Customer'] = top_risk_customers['customer_nm']
            display_df['Status'] = top_risk_customers['customer_status_txt']
            display_df['Risk Ratio'] = top_risk_customers['churn_risk_ratio'].round(2)
            display_df['Days Since Invoice'] = top_risk_customers['days_since_last_invoice']
            display_df['Contract?'] = top_risk_customers['has_contract']
            display_df['Contract End'] = top_risk_customers['last_contract_end_date']
            display_df['Revenue'] = top_risk_customers['revenue_weight_dollars'].round(0).astype(int)
            display_df['QAV'] = top_risk_customers['qav_score_category']
            display_df['End Alert?'] = top_risk_customers['contract_end_less_than_180_days_alert']
            display_df['Provider Alert?'] = top_risk_customers['provider_changed_alert']
            
            # Apply conditional formatting with different logic for different columns
            def style_cell(val, col_name):
                if pd.isna(val):
                    return ''
                
                # For Contract column: TRUE (has contract) = good (green), FALSE (no contract) = bad (orange)
                if col_name == 'Contract?':
                    return 'background-color: #98FB98' if val is True else ('background-color: #FFA500' if val is False else '')
                
                # For Alert columns: TRUE (alert present) = bad (orange), FALSE (no alert) = good (green)
                elif col_name in ['End Alert?', 'Provider Alert?']:
                    return 'background-color: #FFA500' if val is True else ('background-color: #98FB98' if val is False else '')
                
                # For other columns, no special formatting
                else:
                    return ''
            
            # Apply the styling function to each cell
            styled_df = display_df.style.apply(lambda x: [style_cell(val, x.name) for val in x], axis=0)
            
            # Display the table with click functionality
            event = st.dataframe(
                styled_df,
                use_container_width=True,
                height=400,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Handle row selection
            if event.selection and len(event.selection['rows']) > 0:
                selected_row_idx = event.selection['rows'][0]
                selected_customer_name = top_risk_customers.iloc[selected_row_idx]['customer_nm']
                selected_customer_code = top_risk_customers.iloc[selected_row_idx]['customer_cd']
                
                # Store the selection in session state
                st.session_state.selected_customer_from_table = f"{selected_customer_code}: {selected_customer_name}"
                
                # Show success message and switch instruction
                st.success(f"✅ Selected: {selected_customer_name}")
                st.info("👉 **Switch to Tab 2 to view detailed analysis**")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_revenue_at_risk = top_risk_customers['revenue_weight_dollars'].sum()
                st.metric("Total Revenue at Risk", f"${total_revenue_at_risk:,.0f}")
            
            with col2:
                avg_risk_ratio = top_risk_customers['churn_risk_ratio'].mean()
                st.metric("Average Risk Ratio", f"{avg_risk_ratio:.2f}")
            
            with col3:
                customers_with_contracts = top_risk_customers['has_contract'].sum()
                st.metric("Customers with Active Contracts", f"{customers_with_contracts}/10")
            
            with col4:
                contract_expiring = top_risk_customers['contract_end_less_than_180_days_alert'].sum()
                st.metric("Contracts Expiring <180 Days", f"{contract_expiring}/10")
        
        # TAB 2: Individual Customer Analysis
        with tab2:
            # Customer selection dropdown in sidebar for this tab
            st.sidebar.header("🏢 Individual Customer Selection")
            customer_options = sorted(df['dropdown_option'].unique())
            
            # Use the customer selected from table if available, otherwise use first option
            default_customer = st.session_state.selected_customer_from_table if st.session_state.selected_customer_from_table in customer_options else customer_options[0]
            default_index = customer_options.index(default_customer) if default_customer in customer_options else 0
            
            selected_customer = st.sidebar.selectbox(
                "Select Company",
                options=customer_options,
                index=default_index,
                key="individual_customer"
            )
            
            # Show if customer was selected from table
            if st.session_state.selected_customer_from_table == selected_customer:
                st.sidebar.success("📋 Selected from Top Risk table")
            
            # Get selected customer data
            customer_data = df[df['dropdown_option'] == selected_customer].iloc[0]
            
            # BIG HEADLINE with customer code and name
            st.markdown(f"# 🏢 {customer_data['customer_cd']}: {customer_data['customer_nm']}")
            st.markdown("---")
            
            # Main dashboard layout
            col1, col2 = st.columns([2, 1])
            
            with col2:
                # Churn Risk Ratio - Central metric
                st.markdown("### 🎯 Churn Risk Ratio")
                
                # Create a gauge chart for churn risk
                churn_risk = float(customer_data['churn_risk_ratio'])
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = churn_risk,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Risk Level"},
                    gauge = {
                        'axis': {'range': [None, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 0.3], 'color': "lightgreen"},
                            {'range': [0.3, 0.7], 'color': "yellow"},
                            {'range': [0.7, 1], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0.8
                        }
                    }
                ))
                fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col1:
                # Customer Attributes Section
                st.markdown("### 📋 Customer Attributes")
                
                attr_col1, attr_col2 = st.columns(2)
                
                with attr_col1:
                    st.metric("Customer Status", customer_data.get('customer_status_txt', 'N/A'))
                    st.metric("Days Since Last Invoice", f"{customer_data.get('days_since_last_invoice', 'N/A')}")
                    
                with attr_col2:
                    contract_status = "Active Contract" if customer_data.get('has_contract', False) else "No Contract"
                    st.metric("Contract Status", contract_status)
                    
                    # Format contract end date if available
                    contract_end = customer_data.get('last_contract_end_date', 'N/A')
                    st.metric("Contract End Date", contract_end)
                
                # Revenue metric (past 6 months)
                revenue_6m = customer_data.get('revenue_weight_dollars', 0)
                st.metric("Past 6 Months Revenue", f"${revenue_6m:,.2f}")
            
            # Second row with two main sections
            col3, col4 = st.columns(2)
            
            with col3:
                # Key Indicators Section
                st.markdown("### 📈 Key Indicators")
                
                # Profit Margin
                profit_margin = customer_data.get('margin_pct_mean_35days', 0)
                if profit_margin is not None and not pd.isna(profit_margin):
                    st.metric("Profit Margin", f"{profit_margin:.1%}")
                else:
                    st.metric("Profit Margin", "N/A")
                
                # Revenue metrics
                total_invoiced = customer_data.get('invoiced_amount_sum_180days_raw', 0)
                invoiced_change = customer_data.get('invoiced_amount_sum_180days_raw_delta', 0)
                
                if invoiced_change != 0 and not pd.isna(invoiced_change):
                    change_pct = (invoiced_change / total_invoiced) * 100 if total_invoiced != 0 else 0
                    st.metric("Total Invoiced Revenue (6mo)", f"${total_invoiced:,.2f}", f"{change_pct:+.1f}%")
                else:
                    st.metric("Total Invoiced Revenue (6mo)", f"${total_invoiced:,.2f}")
                
                # Past due balance
                past_due = customer_data.get('past_due_balance_mean_180days', 0)
                past_due_change = customer_data.get('past_due_balance_mean_180days_delta', 0)
                
                if past_due_change != 0 and not pd.isna(past_due_change):
                    st.metric("Past Due Balance", f"${past_due:,.2f}", f"${past_due_change:+,.2f}")
                else:
                    st.metric("Past Due Balance", f"${past_due:,.2f}")
                
                # Ticket metrics
                ticket_count = customer_data.get('ticket_count_sum_180days', 0)
                avg_days_close = customer_data.get('cum_avg_days_to_ticket_close', 0)
                st.metric("Ticket Count (6mo) / Avg Days to Close", f"{ticket_count} tickets / {avg_days_close:.1f} days")
            
            with col4:
                # Multipliers and Alerts Section
                st.markdown("### ⚠️ Multipliers & Alerts")
                
                # QAV Score
                qav_score = customer_data.get('qav_score_category', 'missing')
                qav_alert = "🔴 Alert" if qav_score in ['1', '2', '3', '4', '5'] and float(qav_score) <= 5 else "✅ OK"
                st.write(f"**QAV Score:** {qav_score} - {qav_alert}")
                
                # NPS Alert
                nps_category = customer_data.get('nps_alert_category', 'N/A')
                nps_alert = "🔴 Alert" if 'low' in str(nps_category).lower() or 'high' in str(nps_category).lower() else "✅ OK"
                st.write(f"**NPS Status:** {nps_category} - {nps_alert}")
                
                # Contract expiration alert
                contract_alert = customer_data.get('contract_end_less_than_180_days_alert', False)
                contract_status = "🔴 Expires <180 days" if contract_alert else "✅ OK"
                st.write(f"**Contract Expiration:** {contract_status}")
                
                # Provider change alert
                provider_alert = customer_data.get('provider_changed_alert', False)
                provider_status = "🔴 Provider Changed" if provider_alert else "✅ OK"
                st.write(f"**Service Provider:** {provider_status}")
                
                # Customer sentiment placeholder
                st.write("**Customer Sentiment:** Analysis Available")
            
            # Recent Customer Interactions Section
            st.markdown("### 💬 Recent Customer Interactions")
            
            # Check if customer_relationship_status has data
            relationship_status = customer_data.get('customer_relationship_status')
            if relationship_status and pd.notna(relationship_status) and str(relationship_status).strip():
                st.markdown(str(relationship_status))
            else:
                st.info("GenAI summary of recent customer interactions would appear here")
            
            # Detailed Analysis Section
            st.markdown("---")
            st.markdown("### 🔍 Detailed Churn Analysis")
            
            # Display the churn analysis markdown
            churn_analysis = customer_data.get('churn_analysis', '')
            if churn_analysis and pd.notna(churn_analysis):
                st.markdown(str(churn_analysis))
            else:
                st.info("Detailed churn analysis not available for this customer")
            
            # Additional metrics in expandable section
            with st.expander("📊 Additional Technical Metrics"):
                st.write("**Model Predictions:**")
                st.write(f"- Base Model Prediction: {customer_data.get('base_model_prediction', 'N/A'):.4f}")
                st.write(f"- Final Raw Prediction: {customer_data.get('final_raw_prediction', 'N/A'):.4f}")
                st.write(f"- Prediction Percentile: {customer_data.get('prediction_percentile', 'N/A')}th percentile")
                st.write(f"- Weighted Risk Score: {customer_data.get('weighted_risk_score', 'N/A'):.2f}")
                
                st.write("**Revenue Details:**")
                st.write(f"- Revenue Weight: {customer_data.get('revenue_weight', 'N/A'):.2f}")
                st.write(f"- Monthly Value (28-day avg): ${customer_data.get('monthly_value_mean_28days_raw', 0):,.2f}")
                st.write(f"- Recurring Revenue (28-day): ${customer_data.get('recurring_rev_mean_28days', 0):,.2f}")
                
                st.write("**Contract & Activity:**")
                st.write(f"- Active Contracts (28-day avg): {customer_data.get('active_contract_cnt_mean_28days', 'N/A')}")
                st.write(f"- Active Contracts (180-day avg): {customer_data.get('active_contract_cnt_mean_180days', 'N/A')}")
                st.write(f"- Franchise % of Sites: {customer_data.get('franchisee_pct_of_sites_mean_35days', 0):.1%}")
        
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        st.info("Please ensure your CSV file has the correct format with all required columns.")

else:
    st.info("👆 Please upload a CSV file to begin the analysis")
    
    # Show sample format
    st.markdown("### 📋 Expected CSV Format")
    st.markdown("""
    Your CSV should contain the following key columns:
    - `customer_cd`: Customer code
    - `customer_nm`: Customer name  
    - `churn_risk_ratio`: Risk ratio (0-1)
    - `final_raw_prediction`: Model prediction score
    - `revenue_weight_dollars`: Revenue weight in dollars
    - `days_since_last_invoice`: Days since last invoice
    - `has_contract`: Contract status (True/False)
    - `customer_status_txt`: Customer status
    - `qav_score_category`: QAV score category
    - `churn_analysis`: Detailed markdown analysis
    - `customer_relationship_status`: Relationship status markdown
    - And other financial/operational metrics...
    """)

# Footer
st.markdown("---")
st.markdown("*Customer Level Operational Dashboard - Echelon DS*")