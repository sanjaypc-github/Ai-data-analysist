"""
Streamlit Frontend for Autonomous Data Analyst Agent
"""
import streamlit as st
import requests
import pandas as pd
import time
import os
from pathlib import Path

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api"

# Page config
st.set_page_config(
    page_title="Autonomous Data Analyst",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">📊 Autonomous Data Analyst Agent</div>', unsafe_allow_html=True)
st.markdown("Upload your data, ask questions in natural language, and get automated analysis with visualizations!")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x100?text=ADA+Logo", use_column_width=True)
    st.markdown("### About")
    st.info(
        "This agent uses AI to generate and execute pandas code for your data analysis questions. "
        "All code is validated for safety before execution."
    )
    
    st.markdown("### ⚠️ Security Notice")
    st.warning(
        "Generated code runs in an isolated sandbox. Always review code before running in production environments."
    )
    
    # Backend status
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if health_response.status_code == 200:
            st.success("✅ Backend: Connected")
        else:
            st.error("❌ Backend: Error")
    except:
        st.error("❌ Backend: Offline")

# Initialize session state
if 'dataset_id' not in st.session_state:
    st.session_state.dataset_id = None
if 'task_id' not in st.session_state:
    st.session_state.task_id = None
if 'dataset_info' not in st.session_state:
    st.session_state.dataset_info = None
if 'preprocessing_done' not in st.session_state:
    st.session_state.preprocessing_done = False
if 'quality_report' not in st.session_state:
    st.session_state.quality_report = None

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload Data", "🔧 Preprocess Data", "❓ Ask Question", "📈 View Results"])

# Tab 1: Upload Data
with tab1:
    st.header("Upload Your Dataset")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        # Show preview
        df_preview = pd.read_csv(uploaded_file, nrows=100)
        
        st.markdown("### Preview (first 5 rows)")
        st.dataframe(df_preview.head(), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", len(df_preview))
        with col2:
            st.metric("Columns", len(df_preview.columns))
        
        with st.expander("Column Details"):
            dtypes_df = pd.DataFrame({
                'Column': df_preview.columns,
                'Type': df_preview.dtypes.astype(str)
            })
            st.dataframe(dtypes_df, use_container_width=True)
        
        if st.button("📤 Upload Dataset", type="primary"):
            with st.spinner("Uploading dataset..."):
                # Reset file pointer
                uploaded_file.seek(0)
                
                # Upload to backend
                files = {'file': (uploaded_file.name, uploaded_file, 'text/csv')}
                
                try:
                    response = requests.post(f"{API_BASE}/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.dataset_id = data['dataset_id']
                        st.session_state.dataset_info = data
                        
                        st.success(f"✅ Dataset uploaded successfully! ID: {data['dataset_id']}")
                        st.markdown(f"**Rows:** {data['rows']} | **Columns:** {len(data['columns'])}")
                        
                        st.balloons()
                    else:
                        st.error(f"Upload failed: {response.text}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Tab 2: Preprocess Data
with tab2:
    st.header("🔧 Data Preprocessing & Quality Check")
    
    if st.session_state.dataset_id is None:
        st.warning("⚠️ Please upload a dataset first (in the 'Upload Data' tab)")
    else:
        st.success(f"📊 Dataset loaded: {st.session_state.dataset_id}")
        
        # Fetch quality report
        if st.button("🔍 Analyze Data Quality") or st.session_state.quality_report:
            with st.spinner("Analyzing data quality..."):
                try:
                    response = requests.get(f"{API_BASE}/dataset/{st.session_state.dataset_id}/quality")
                    
                    if response.status_code == 200:
                        quality_data = response.json()
                        st.session_state.quality_report = quality_data
                        
                        # Display quality metrics
                        st.markdown("### 📊 Data Quality Report")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Rows", quality_data['total_rows'])
                        with col2:
                            st.metric("Total Columns", quality_data['total_columns'])
                        with col3:
                            st.metric("Missing Values", f"{quality_data['missing_percentage']}%")
                        with col4:
                            st.metric("Duplicates", quality_data['duplicate_count'])
                        
                        # Show issues
                        if quality_data['has_missing_values'] or quality_data['has_duplicates']:
                            st.markdown("### ⚠️ Data Quality Issues Detected")
                            
                            if quality_data['has_missing_values']:
                                st.warning(f"Found {quality_data['missing_cells']} missing values ({quality_data['missing_percentage']}%)")
                                
                                # Column-wise missing values
                                missing_cols = [col for col in quality_data['columns'] if col['missing_count'] > 0]
                                if missing_cols:
                                    st.markdown("#### Missing Values by Column")
                                    missing_df = pd.DataFrame([
                                        {
                                            'Column': col['name'],
                                            'Missing Count': col['missing_count'],
                                            'Missing %': f"{col['missing_percentage']:.1f}%",
                                            'Data Type': col['dtype']
                                        }
                                        for col in missing_cols
                                    ])
                                    st.dataframe(missing_df, use_container_width=True)
                            
                            if quality_data['has_duplicates']:
                                st.warning(f"Found {quality_data['duplicate_count']} duplicate rows")
                        else:
                            st.success("✅ No data quality issues detected! Your data is clean.")
                            st.session_state.preprocessing_done = True
                        
                        # Preprocessing options
                        if quality_data['has_missing_values'] or quality_data['has_duplicates']:
                            st.markdown("---")
                            st.markdown("### 🛠️ Preprocessing Options")
                            st.info("Choose how to handle missing values and data quality issues")
                            
                            preprocessing_strategy = st.radio(
                                "Select preprocessing strategy:",
                                options=[
                                    "auto",
                                    "drop_rows",
                                    "drop_columns",
                                    "fill_zero",
                                    "fill_mean",
                                    "fill_median",
                                    "fill_mode",
                                    "fill_forward",
                                    "fill_backward",
                                    "custom"
                                ],
                                format_func=lambda x: {
                                    "auto": "🤖 Auto (Smart per-column handling) - Recommended",
                                    "drop_rows": "🗑️ Drop rows with missing values",
                                    "drop_columns": "🗑️ Drop columns with >50% missing values",
                                    "fill_zero": "0️⃣ Fill all missing values with 0",
                                    "fill_mean": "📊 Fill numeric columns with mean",
                                    "fill_median": "📊 Fill numeric columns with median (robust)",
                                    "fill_mode": "📊 Fill all columns with most frequent value",
                                    "fill_forward": "➡️ Forward fill (use previous value)",
                                    "fill_backward": "⬅️ Backward fill (use next value)",
                                    "custom": "⚙️ Custom (configure per column)"
                                }[x],
                                index=0
                            )
                            
                            # Strategy explanations
                            strategy_info = {
                                "auto": "✨ Automatically chooses the best strategy for each column:\n- Numeric → Median\n- Categorical → Mode\n- Dates → Forward fill",
                                "drop_rows": "⚠️ Removes all rows containing any missing values. Use when missing data is minimal.",
                                "drop_columns": "⚠️ Removes columns with more than 50% missing values. Keeps rows intact.",
                                "fill_zero": "⚠️ Replaces all missing values with 0. Good for counts, but may skew averages.",
                                "fill_mean": "📈 For numeric columns, uses average value. Sensitive to outliers.",
                                "fill_median": "📈 For numeric columns, uses middle value. Robust against outliers (Recommended).",
                                "fill_mode": "📊 Uses most frequent value. Good for categorical data.",
                                "fill_forward": "➡️ Uses the last valid value before the gap. Good for time series.",
                                "fill_backward": "⬅️ Uses the next valid value after the gap.",
                                "custom": "⚙️ Configure different strategies for different columns."
                            }
                            
                            st.info(strategy_info[preprocessing_strategy])
                            
                            # Custom configuration
                            custom_config = {}
                            if preprocessing_strategy == "custom":
                                st.markdown("#### Configure Per Column")
                                missing_cols = [col for col in quality_data['columns'] if col['missing_count'] > 0]
                                
                                for col in missing_cols:
                                    col_name = col['name']
                                    col_type = col['dtype']
                                    
                                    st.markdown(f"**{col_name}** ({col_type}) - {col['missing_count']} missing ({col['missing_percentage']:.1f}%)")
                                    
                                    if 'int' in col_type or 'float' in col_type:
                                        options = ["median", "mean", "zero", "mode", "drop", "forward_fill", "backward_fill"]
                                    else:
                                        options = ["mode", "custom_value", "drop", "forward_fill", "backward_fill"]
                                    
                                    strategy = st.selectbox(
                                        f"Strategy for {col_name}:",
                                        options=options,
                                        key=f"strategy_{col_name}"
                                    )
                                    
                                    if strategy == "custom_value":
                                        custom_value = st.text_input(
                                            f"Enter value for {col_name}:",
                                            key=f"custom_{col_name}"
                                        )
                                        custom_config[col_name] = {"strategy": strategy, "value": custom_value}
                                    else:
                                        custom_config[col_name] = {"strategy": strategy}
                            
                            # Handle duplicates
                            handle_duplicates = st.checkbox("Remove duplicate rows", value=False)
                            
                            # Preview impact
                            with st.expander("📋 Preview Impact"):
                                if preprocessing_strategy == "drop_rows":
                                    rows_to_drop = sum(1 for col in quality_data['columns'] if col['missing_count'] > 0)
                                    st.write(f"Will remove approximately {rows_to_drop} rows")
                                    st.write(f"Remaining rows: ~{quality_data['total_rows'] - rows_to_drop}")
                                elif preprocessing_strategy == "drop_columns":
                                    cols_to_drop = [col['name'] for col in quality_data['columns'] 
                                                   if col['missing_percentage'] > 50]
                                    if cols_to_drop:
                                        st.write(f"Will remove columns: {', '.join(cols_to_drop)}")
                                    else:
                                        st.write("No columns exceed 50% missing threshold")
                            
                            # Apply preprocessing button
                            st.markdown("---")
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                apply_button = st.button("✨ Apply Preprocessing", type="primary", use_container_width=True)
                            
                            if apply_button:
                                with st.spinner("🔄 Preprocessing data..."):
                                    try:
                                        # Prepare preprocessing request
                                        preprocess_payload = {
                                            "dataset_id": st.session_state.dataset_id,
                                            "strategy": preprocessing_strategy,
                                            "handle_duplicates": handle_duplicates,
                                            "custom_config": custom_config if preprocessing_strategy == "custom" else None
                                        }
                                        
                                        response = requests.post(
                                            f"{API_BASE}/dataset/preprocess",
                                            json=preprocess_payload
                                        )
                                        
                                        if response.status_code == 200:
                                            result = response.json()
                                            st.session_state.preprocessing_done = True
                                            
                                            st.success("✅ Preprocessing completed successfully!")
                                            
                                            # Show what was done
                                            if result.get('actions'):
                                                st.markdown("#### 🔨 Actions Performed:")
                                                for action in result['actions']:
                                                    st.markdown(f"- {action}")
                                            
                                            # Show new quality metrics
                                            if result.get('new_quality'):
                                                col1, col2 = st.columns(2)
                                                with col1:
                                                    st.metric(
                                                        "Missing Values After",
                                                        f"{result['new_quality']['missing_percentage']}%",
                                                        delta=f"-{quality_data['missing_percentage'] - result['new_quality']['missing_percentage']:.1f}%"
                                                    )
                                                with col2:
                                                    st.metric(
                                                        "Rows After",
                                                        result['new_quality']['total_rows'],
                                                        delta=result['new_quality']['total_rows'] - quality_data['total_rows']
                                                    )
                                            
                                            st.balloons()
                                            st.info("✨ You can now proceed to 'Ask Question' tab!")
                                        
                                        else:
                                            st.error(f"Preprocessing failed: {response.text}")
                                    
                                    except Exception as e:
                                        st.error(f"Error during preprocessing: {str(e)}")
                        
                        else:
                            st.session_state.preprocessing_done = True
                            
                except Exception as e:
                    st.error(f"Error analyzing data quality: {str(e)}")

# Tab 3: Ask Question
with tab3:
    st.header("Ask a Question About Your Data")
    
    if st.session_state.dataset_id is None:
        st.warning("⚠️ Please upload a dataset first (in the 'Upload Data' tab)")
    else:
        st.success(f"📊 Dataset loaded: {st.session_state.dataset_id}")
        
        if st.session_state.dataset_info:
            with st.expander("Dataset Info"):
                st.write(f"**Columns:** {', '.join(st.session_state.dataset_info['columns'])}")
        
        # Question input
        question = st.text_area(
            "Enter your question:",
            placeholder="e.g., What are the top 5 products by sales?\nShow monthly revenue trends.\nWhat is the average order value by customer segment?",
            height=100
        )
        
        context = st.text_input(
            "Additional context (optional):",
            placeholder="e.g., Focus on data from last quarter, exclude cancelled orders"
        )
        
        # Visualization toggle
        enable_visualization = st.checkbox(
            "📊 Generate visualization", 
            value=True,
            help="Enable this to generate charts/plots with your analysis. Disable for simple data queries."
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.button("🚀 Generate & Run", type="primary", use_container_width=True)
        
        if submit_button and question:
            with st.spinner("🤖 Generating code and executing..."):
                try:
                    # Submit question
                    payload = {
                        "dataset_id": st.session_state.dataset_id,
                        "question": question,
                        "context": context if context else None,
                        "enable_visualization": enable_visualization
                    }
                    
                    response = requests.post(f"{API_BASE}/ask", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.task_id = data['task_id']
                        
                        st.success("✅ Task created successfully!")
                        
                        # Show generated code
                        st.markdown("### 📝 Generated Code")
                        with st.expander("View Code", expanded=True):
                            st.code(data['generated_code'], language='python')
                        
                        st.info("⏳ Code is executing... Check the 'View Results' tab to see progress.")
                    
                    else:
                        error_detail = response.json().get('detail', response.text)
                        st.error(f"❌ Error: {error_detail}")
                
                except Exception as e:
                    st.error(f"Request failed: {str(e)}")
        
        elif submit_button:
            st.warning("Please enter a question!")

# Tab 4: View Results
with tab4:
    st.header("Analysis Results")
    
    if st.session_state.task_id is None:
        st.info("💡 Submit a question first to see results here.")
    else:
        st.success(f"📋 Task ID: {st.session_state.task_id}")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            refresh_button = st.button("🔄 Refresh Status")
        
        # Fetch status
        if auto_refresh or refresh_button:
            try:
                response = requests.get(f"{API_BASE}/status/{st.session_state.task_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    status = data['status']
                    
                    # Show the question prominently at the top
                    st.markdown("### ❓ Question")
                    st.info(data['question'])
                    
                    # Status indicator
                    if status == 'completed':
                        st.success("✅ Status: COMPLETED")
                    elif status == 'failed':
                        st.error("❌ Status: FAILED")
                        if data.get('error_message'):
                            st.error(f"**Error:** {data['error_message']}")
                    elif status == 'running':
                        st.info("⏳ Status: RUNNING")
                    else:
                        st.warning(f"Status: {status.upper()}")
                    
                    # Show output/answer prominently BEFORE the code
                    if data.get('stdout'):
                        st.markdown("### 📄 Answer")
                        st.code(data['stdout'], language='text')
                    
                    # Show generated code in expander (collapsed by default)
                    with st.expander("🔍 View Generated Code"):
                        st.code(data['generated_code'], language='python')
                    
                    # Show errors
                    if data.get('stderr'):
                        st.markdown("### ⚠️ Warnings/Errors")
                        st.code(data['stderr'])
                    
                    # Show result files and actual data
                    if data.get('result_files'):
                        st.markdown("### 📊 Analysis Results")
                        
                        # Display CSV results as table
                        csv_files = [f for f in data['result_files'] if f.endswith('.csv')]
                        for csv_file in csv_files:
                            try:
                                csv_response = requests.get(
                                    f"{API_BASE}/task/{st.session_state.task_id}/file/{csv_file}"
                                )
                                if csv_response.status_code == 200:
                                    import pandas as pd
                                    from io import StringIO
                                    result_df = pd.read_csv(StringIO(csv_response.text))
                                    st.markdown(f"#### 📋 {csv_file}")
                                    st.dataframe(result_df, use_container_width=True)
                                    
                                    # Add download button for CSV
                                    st.download_button(
                                        label=f"⬇️ Download {csv_file}",
                                        data=csv_response.content,
                                        file_name=csv_file,
                                        mime="text/csv"
                                    )
                            except Exception as e:
                                st.error(f"Could not load {csv_file}: {e}")
                        
                        # Display visualizations
                        png_files = [f for f in data['result_files'] if f.endswith('.png')]
                        for png_file in png_files:
                            try:
                                img_response = requests.get(
                                    f"{API_BASE}/task/{st.session_state.task_id}/file/{png_file}"
                                )
                                if img_response.status_code == 200:
                                    st.markdown(f"#### 📈 {png_file}")
                                    st.image(img_response.content, use_column_width=True)
                                    
                                    # Add download button for image
                                    st.download_button(
                                        label=f"⬇️ Download {png_file}",
                                        data=img_response.content,
                                        file_name=png_file,
                                        mime="image/png"
                                    )
                            except Exception as e:
                                st.error(f"Could not load {png_file}: {e}")
                    
                    # Download report button
                    if status == 'completed':
                        st.markdown("### 📥 Download Report")
                        
                        # Generate and download report
                        try:
                            # Check if report exists or generate it
                            report_check = requests.get(f"{API_BASE}/report/{st.session_state.task_id}")
                            
                            if report_check.status_code == 200:
                                report_data = report_check.json()
                                
                                if report_data['report_available']:
                                    # Download the report
                                    report_response = requests.get(
                                        f"{API_BASE}/report/{st.session_state.task_id}/download"
                                    )
                                    
                                    if report_response.status_code == 200:
                                        # Use download_button to provide file download
                                        st.download_button(
                                            label="📥 Download HTML Report",
                                            data=report_response.content,
                                            file_name=f"analysis_report_{st.session_state.task_id}.html",
                                            mime="text/html",
                                            help="Download the analysis report as HTML file"
                                        )
                                        st.success("✅ Report ready for download!")
                                    else:
                                        st.error(f"Failed to download report: {report_response.text}")
                                else:
                                    st.warning(report_data['message'])
                            else:
                                st.error(f"Failed to generate report: {report_check.text}")
                                
                        except Exception as e:
                            st.error(f"Report generation failed: {e}")
                    
                    # Show error message if failed
                    if status == 'failed' and data.get('error_message'):
                        st.error(f"**Error:** {data['error_message']}")
                
                else:
                    st.error(f"Failed to fetch status: {response.text}")
            
            except Exception as e:
                st.error(f"Error fetching status: {str(e)}")
        
        # Auto-refresh
        if auto_refresh:
            time.sleep(5)
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Built with ❤️ using FastAPI, Streamlit, and Docker | "
    "<a href='https://github.com/yourusername/ada-agent'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)
