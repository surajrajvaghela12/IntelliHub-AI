import pandas as pd
import numpy as np
import os

def load_dataframe(file_path):
    """Utility to safely load a DataFrame from CSV, Excel, or JSON."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.csv', '.txt']:
        df = pd.read_csv(file_path)
    elif ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    elif ext == '.json':
        df = pd.read_json(file_path)
    else:
        df = pd.read_csv(file_path)
    
    # Try converting numeric string columns to numeric types
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                converted = pd.to_numeric(df[col], errors='coerce')
                # Only convert if more than half of non-null values are numeric
                if converted.notna().sum() > 0 and (converted.notna().sum() / len(df)) >= 0.5:
                    df[col] = converted
            except Exception:
                pass
    return df

def analyze_dataset_metadata(file_path):
    """
    Analyzes dataset mirroring pandas info(), describe(), shape, memory usage, duplicates & nulls.
    Maps to Unit 1 of Syllabus.
    """
    df = load_dataframe(file_path)
    
    rows, cols = df.shape
    mem_bytes = df.memory_usage(deep=True).sum()
    if mem_bytes < 1024 * 1024:
        mem_str = f"{mem_bytes / 1024:.2f} KB"
    else:
        mem_str = f"{mem_bytes / (1024 * 1024):.2f} MB"
        
    duplicates = int(df.duplicated().sum())
    missing = int(df.isna().sum().sum())
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    
    column_info = []
    for col in df.columns:
        c_type = str(df[col].dtype)
        null_count = int(df[col].isna().sum())
        null_pct = round((null_count / rows) * 100, 2) if rows > 0 else 0
        unique_count = int(df[col].nunique())
        sample_vals = df[col].dropna().unique()[:3].tolist()
        sample_str = ", ".join([str(x) for x in sample_vals])
        
        column_info.append({
            'name': col,
            'dtype': c_type,
            'null_count': null_count,
            'null_pct': null_pct,
            'unique_count': unique_count,
            'is_numerical': col in num_cols,
            'sample_values': sample_str,
        })
        
    return {
        'row_count': rows,
        'column_count': cols,
        'memory_usage_bytes': mem_bytes,
        'memory_usage_str': mem_str,
        'duplicate_rows': duplicates,
        'missing_values': missing,
        'numerical_cols': len(num_cols),
        'categorical_cols': len(cat_cols),
        'columns': column_info,
        'preview_head': df.head(10).to_dict(orient='records'),
        'preview_tail': df.tail(10).to_dict(orient='records'),
    }
