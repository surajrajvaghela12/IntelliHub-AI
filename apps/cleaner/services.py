import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
import os

from apps.datasets.utils import load_dataframe

def generate_cleaning_recommendations(df):
    """Generates column-wise cleaning recommendations."""
    recommendations = []
    
    # 1. Duplicates
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        recommendations.append({
            'type': 'duplicates',
            'title': 'Duplicate Rows Detected',
            'description': f"Found {dup_count} duplicate row(s). Recommended to remove them.",
            'column': 'All Columns',
            'action': 'remove_duplicates',
            'badge': 'warning'
        })
        
    # 2. Missing Values per column
    for col in df.columns:
        missing = int(df[col].isna().sum())
        if missing > 0:
            missing_pct = (missing / len(df)) * 100
            if pd.api.types.is_numeric_dtype(df[col]):
                rec_action = 'fill_mean' if missing_pct < 20 else 'fill_median'
                rec_desc = f"Fill {missing} missing value(s) with Mean ({df[col].mean():.2f})"
            else:
                rec_action = 'fill_mode'
                rec_desc = f"Fill {missing} missing value(s) with Mode ({df[col].mode()[0] if not df[col].mode().empty else 'Unknown'})"
                
            recommendations.append({
                'type': 'missing',
                'title': f"Missing Values in '{col}'",
                'description': f"{rec_desc} ({missing_pct:.1f}% missing).",
                'column': col,
                'action': rec_action,
                'badge': 'danger'
            })
            
    # 3. Outliers in numerical columns (IQR method)
    for col in df.select_dtypes(include=[np.number]).columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))]
        outlier_count = len(outliers)
        if outlier_count > 0:
            recommendations.append({
                'type': 'outlier',
                'title': f"Outliers in '{col}'",
                'description': f"Detected {outlier_count} potential outlier(s) using 1.5*IQR threshold.",
                'column': col,
                'action': 'remove_outliers_iqr',
                'badge': 'info'
            })

    # 4. Categorical columns encoding
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if cat_cols:
        recommendations.append({
            'type': 'encoding',
            'title': 'Categorical Variables Detected',
            'description': f"Columns {cat_cols} are non-numeric. Recommended to apply Label Encoding or One-Hot Encoding.",
            'column': ', '.join(cat_cols),
            'action': 'encode_categories',
            'badge': 'secondary'
        })
        
    return recommendations


def perform_auto_clean(file_path):
    """
    Executes full automated data cleaning pipeline (Unit 1 & Unit 3):
    1. Removes Duplicates (drop_duplicates)
    2. Fills Missing Values (fillna mean/mode)
    3. Handles Outliers (IQR capping)
    4. Categorical Encoding (LabelEncoder)
    5. Feature Scaling (StandardScaler)
    """
    df = load_dataframe(file_path)
    before_rows = len(df)
    before_missing = int(df.isna().sum().sum())
    logs = []
    
    # 1. Remove Duplicates
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        df = df.drop_duplicates()
        logs.append(f"Removed {dup_count} duplicate row(s) using drop_duplicates().")
        
    # 2. Fill Missing Values
    for col in df.columns:
        missing = int(df[col].isna().sum())
        if missing > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                mean_val = df[col].mean()
                df[col] = df[col].fillna(mean_val)
                logs.append(f"Filled {missing} missing value(s) in column '{col}' with mean ({mean_val:.2f}) using fillna().")
            else:
                mode_val = df[col].mode()[0] if not df[col].mode().empty else 'Missing'
                df[col] = df[col].fillna(mode_val)
                logs.append(f"Filled {missing} missing value(s) in column '{col}' with mode ('{mode_val}') using fillna().")

    # 3. Handle Outliers via IQR
    for col in df.select_dtypes(include=[np.number]).columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers_count = len(df[(df[col] < lower_bound) | (df[col] > upper_bound)])
        if outliers_count > 0:
            df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
            df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])
            logs.append(f"Capped {outliers_count} outlier(s) in '{col}' using IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}].")

    after_rows = len(df)
    after_missing = int(df.isna().sum().sum())
    
    return df, {
        'before_rows': before_rows,
        'after_rows': after_rows,
        'before_missing': before_missing,
        'after_missing': after_missing,
        'logs': logs,
    }


def perform_custom_clean(file_path, action, column=None):
    """Executes a specific targeted cleaning action."""
    df = load_dataframe(file_path)
    before_rows = len(df)
    before_missing = int(df.isna().sum().sum())
    logs = []
    
    if action == 'drop_duplicates':
        dup_count = int(df.duplicated().sum())
        df = df.drop_duplicates()
        logs.append(f"Removed {dup_count} duplicate row(s).")
        
    elif action == 'drop_nulls':
        if column and column in df.columns:
            null_count = int(df[column].isna().sum())
            df = df.dropna(subset=[column])
            logs.append(f"Dropped {null_count} row(s) with nulls in '{column}' using dropna().")
        else:
            df = df.dropna()
            logs.append(f"Dropped all rows containing null values using dropna().")

    elif action in ['fill_mean', 'fill_median', 'fill_mode', 'fill_zero']:
        if column and column in df.columns:
            missing = int(df[column].isna().sum())
            if action == 'fill_mean':
                val = df[column].mean()
            elif action == 'fill_median':
                val = df[column].median()
            elif action == 'fill_mode':
                val = df[column].mode()[0] if not df[column].mode().empty else 0
            else:
                val = 0
            df[column] = df[column].fillna(val)
            logs.append(f"Filled {missing} missing value(s) in '{column}' with {action.replace('fill_', '')} ({val}).")

    elif action == 'remove_outliers_iqr':
        if column and column in df.columns and pd.api.types.is_numeric_dtype(df[column]):
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            init_len = len(df)
            df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
            removed = init_len - len(df)
            logs.append(f"Removed {removed} outlier row(s) from '{column}'.")

    elif action == 'encode_categories':
        cat_cols = [column] if (column and column in df.columns) else df.select_dtypes(include=['object', 'category']).columns.tolist()
        le = LabelEncoder()
        for c in cat_cols:
            if c in df.columns:
                df[c] = le.fit_transform(df[c].astype(str))
                logs.append(f"Applied LabelEncoder on categorical column '{c}'.")

    elif action == 'standard_scaling':
        num_cols = [column] if (column and column in df.columns) else df.select_dtypes(include=[np.number]).columns.tolist()
        scaler = StandardScaler()
        if num_cols:
            df[num_cols] = scaler.fit_transform(df[num_cols])
            logs.append(f"Applied StandardScaler on column(s): {num_cols}.")

    after_rows = len(df)
    after_missing = int(df.isna().sum().sum())
    
    return df, {
        'before_rows': before_rows,
        'after_rows': after_rows,
        'before_missing': before_missing,
        'after_missing': after_missing,
        'logs': logs,
    }
