"""
Data validation and preprocessing utilities
Handles missing values, data type inference, and data quality checks
"""
import pandas as pd
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def analyze_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze data quality metrics
    
    Args:
        df: DataFrame to analyze
    
    Returns:
        Dictionary with quality metrics
    """
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    missing_percentage = (missing_cells / total_cells * 100) if total_cells > 0 else 0
    
    column_info = []
    for col in df.columns:
        col_data = {
            'name': col,
            'dtype': str(df[col].dtype),
            'missing_count': int(df[col].isnull().sum()),
            'missing_percentage': float(df[col].isnull().sum() / len(df) * 100),
            'unique_values': int(df[col].nunique()),
            'sample_values': df[col].dropna().head(3).tolist() if not df[col].dropna().empty else []
        }
        column_info.append(col_data)
    
    quality_report = {
        'total_rows': int(df.shape[0]),
        'total_columns': int(df.shape[1]),
        'total_cells': int(total_cells),
        'missing_cells': int(missing_cells),
        'missing_percentage': round(float(missing_percentage), 2),
        'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
        'columns': column_info,
        'has_missing_values': bool(missing_cells > 0),
        'has_duplicates': bool(df.duplicated().any()),
        'duplicate_count': int(df.duplicated().sum())
    }
    
    return quality_report


def preprocess_dataframe(df: pd.DataFrame, strategy: str = "auto") -> Tuple[pd.DataFrame, List[str]]:
    """
    Preprocess DataFrame to handle missing values and data types
    
    Args:
        df: Input DataFrame
        strategy: Preprocessing strategy
            - "auto": Automatically choose best strategy per column
            - "drop": Drop rows with missing values
            - "fill_mean": Fill numeric columns with mean
            - "fill_mode": Fill categorical columns with mode
            - "fill_zero": Fill missing values with 0
    
    Returns:
        Tuple of (processed DataFrame, list of actions taken)
    """
    df_processed = df.copy()
    actions = []
    
    # First: Clean numeric columns that contain commas or are stored as strings
    for col in df_processed.columns:
        if df_processed[col].dtype == 'object':
            # Try to detect if this is a numeric column with formatting
            sample_values = df_processed[col].dropna().head(10)
            if len(sample_values) > 0:
                # Check if values look like numbers with commas
                sample_str = str(sample_values.iloc[0]) if len(sample_values) > 0 else ""
                if any(char.isdigit() for char in sample_str):
                    try:
                        # Remove commas and convert to numeric
                        df_processed[col] = df_processed[col].str.replace(',', '').str.replace('"', '')
                        df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
                        actions.append(f"Converted '{col}' from string to numeric (removed commas)")
                    except:
                        pass  # Keep as string if conversion fails
    
    if strategy == "auto":
        # Auto strategy: Smart handling per column type
        for col in df_processed.columns:
            missing_count = df_processed[col].isnull().sum()
            if missing_count == 0:
                continue
            
            # Numeric columns: fill with median (more robust than mean)
            if pd.api.types.is_numeric_dtype(df_processed[col]):
                median_val = df_processed[col].median()
                df_processed[col].fillna(median_val, inplace=True)
                actions.append(f"Filled {missing_count} missing values in '{col}' with median ({median_val:.2f})")
            
            # Categorical/Object columns: fill with mode or 'Unknown'
            elif pd.api.types.is_object_dtype(df_processed[col]) or pd.api.types.is_categorical_dtype(df_processed[col]):
                if df_processed[col].mode().empty:
                    df_processed[col].fillna('Unknown', inplace=True)
                    actions.append(f"Filled {missing_count} missing values in '{col}' with 'Unknown'")
                else:
                    mode_val = df_processed[col].mode()[0]
                    df_processed[col].fillna(mode_val, inplace=True)
                    actions.append(f"Filled {missing_count} missing values in '{col}' with mode ('{mode_val}')")
            
            # Datetime columns: forward fill
            elif pd.api.types.is_datetime64_any_dtype(df_processed[col]):
                df_processed[col] = df_processed[col].ffill()
                actions.append(f"Forward-filled {missing_count} missing values in '{col}'")
    
    elif strategy == "drop":
        initial_rows = len(df_processed)
        df_processed.dropna(inplace=True)
        dropped_rows = initial_rows - len(df_processed)
        if dropped_rows > 0:
            actions.append(f"Dropped {dropped_rows} rows with missing values")
    
    elif strategy == "fill_mean":
        for col in df_processed.select_dtypes(include=['number']).columns:
            missing_count = df_processed[col].isnull().sum()
            if missing_count > 0:
                mean_val = df_processed[col].mean()
                df_processed[col].fillna(mean_val, inplace=True)
                actions.append(f"Filled {missing_count} missing values in '{col}' with mean ({mean_val:.2f})")
    
    elif strategy == "fill_mode":
        for col in df_processed.columns:
            missing_count = df_processed[col].isnull().sum()
            if missing_count > 0 and not df_processed[col].mode().empty:
                mode_val = df_processed[col].mode()[0]
                df_processed[col].fillna(mode_val, inplace=True)
                actions.append(f"Filled {missing_count} missing values in '{col}' with mode")
    
    elif strategy == "fill_zero":
        missing_total = df_processed.isnull().sum().sum()
        df_processed.fillna(0, inplace=True)
        actions.append(f"Filled {missing_total} missing values with 0")
    
    # Infer better data types
    df_processed = df_processed.infer_objects()
    
    return df_processed, actions


def validate_and_preprocess_csv(file_path: Path) -> Dict[str, Any]:
    """
    Validate and preprocess uploaded CSV file
    
    Args:
        file_path: Path to CSV file
    
    Returns:
        Dictionary with validation results and processed file path
    """
    try:
        # Try reading with different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                used_encoding = encoding
                logger.info(f"Successfully read CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise ValueError("Could not read CSV with any standard encoding")
        
        # Analyze data quality
        quality_report = analyze_data_quality(df)
        
        # Preprocess if needed
        preprocessing_needed = quality_report['has_missing_values']
        preprocessing_actions = []
        
        if preprocessing_needed:
            logger.info(f"Preprocessing data: {quality_report['missing_percentage']}% missing values")
            df_processed, actions = preprocess_dataframe(df, strategy="auto")
            preprocessing_actions = actions
            
            # Save preprocessed version
            processed_path = file_path.parent / f"processed_{file_path.name}"
            df_processed.to_csv(processed_path, index=False)
            logger.info(f"Saved preprocessed data to {processed_path}")
        else:
            processed_path = file_path
            logger.info("No preprocessing needed - data is clean")
        
        return {
            'success': True,
            'original_path': str(file_path),
            'processed_path': str(processed_path),
            'encoding': used_encoding,
            'preprocessing_needed': preprocessing_needed,
            'preprocessing_actions': preprocessing_actions,
            'quality_report': quality_report
        }
    
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'original_path': str(file_path)
        }


def get_data_summary_for_llm(df: pd.DataFrame, max_sample_rows: int = 3) -> str:
    """
    Generate a concise data summary for LLM context
    
    Args:
        df: DataFrame to summarize
        max_sample_rows: Maximum number of sample rows to include
    
    Returns:
        String summary for LLM
    """
    summary_parts = [
        f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns",
        f"\nColumns: {', '.join(df.columns.tolist())}",
        f"\nData types:\n{df.dtypes.to_string()}",
        f"\nSample data:\n{df.head(max_sample_rows).to_string()}"
    ]
    
    # Add info about missing values if any
    missing = df.isnull().sum()
    if missing.sum() > 0:
        summary_parts.append(f"\nMissing values:\n{missing[missing > 0].to_string()}")
    
    return "\n".join(summary_parts)
