import os
import requests
import json
import pandas as pd
import numpy as np

from apps.datasets.utils import load_dataframe

def ask_ai_data_analyst(query, dataset=None):
    """
    Answers user questions regarding data analytics, models, data cleaning, or visualizations.
    Supports optional Gemini API or heuristic expert engine.
    """
    api_key = os.environ.get('GEMINI_API_KEY', '')
    
    # Dataset context string construction
    context_str = ""
    if dataset and dataset.latest_version and dataset.latest_version.file:
        try:
            df = load_dataframe(dataset.latest_version.file.path)
            rows, cols = df.shape
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            missing = df.isna().sum().sum()
            
            corr_text = ""
            if len(num_cols) >= 2:
                corr = df[num_cols].corr().abs().copy()
                corr_vals = corr.to_numpy(copy=True)
                np.fill_diagonal(corr_vals, 0)
                corr = pd.DataFrame(corr_vals, index=corr.index, columns=corr.columns)
                max_corr_val = corr.max().max()
                if not np.isnan(max_corr_val) and max_corr_val > 0:
                    max_cols = corr.stack().idxmax()
                    corr_text = f"Highest correlation pair: {max_cols[0]} and {max_cols[1]} ({max_corr_val:.2f})."
                    
            context_str = (
                f"Dataset Name: {dataset.name}, Rows: {rows}, Columns: {cols}.\n"
                f"Numerical columns: {num_cols}\nCategorical columns: {cat_cols}\n"
                f"Total missing values: {missing}.\n{corr_text}"
            )
        except Exception:
            context_str = f"Dataset Name: {dataset.name}"
            
    # Try Gemini API if key is present
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": f"You are IntelliHub AI's Data Analyst. Context: {context_str}\nUser Question: {query}\nProvide a clear, professional answer."}]
                }]
            }
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                return data['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            pass

    # Heuristic AI Expert Analyst Fallback
    q_lower = query.lower()
    if 'correlation' in q_lower or 'correlated' in q_lower:
        if dataset and dataset.latest_version and dataset.latest_version.file:
            df = load_dataframe(dataset.latest_version.file.path)
            num_df = df.select_dtypes(include=[np.number])
            if num_df.shape[1] >= 2:
                corr = num_df.corr().copy()
                corr_vals = corr.to_numpy(copy=True)
                np.fill_diagonal(corr_vals, 0)
                corr = pd.DataFrame(corr_vals, index=num_df.select_dtypes(include=[np.number]).columns, columns=num_df.select_dtypes(include=[np.number]).columns)
                max_c = corr.abs().stack().idxmax()
                val = corr.loc[max_c[0], max_c[1]]
                return f"🤖 **AI Analysis**: In your dataset **'{dataset.name}'**, the highest correlation is between **'{max_c[0]}'** and **'{max_c[1]}'** with a correlation coefficient of **{val:.2f}**. This indicates a strong {'positive' if val > 0 else 'negative'} relationship!"
        return "🤖 **AI Analysis**: Correlation measures linear relationship between two variables. Values range from -1 (strong negative) to +1 (strong positive). Check the EDA Heatmap tab for complete pairwise visual matrices!"

    elif 'model' in q_lower or 'algorithm' in q_lower or 'predict' in q_lower:
        return f"🤖 **AI Recommendation**: For tabular dataset analysis, if your target variable is continuous (e.g. Price, Revenue), use **Multiple Linear Regression** or **Random Forest Regressor**. If target is categorical (e.g. Pass/Fail, Spam/Ham), **Random Forest Classifier** or **kNN** (Unit 5 syllabus) will deliver the highest accuracy!"

    elif 'clean' in q_lower or 'missing' in q_lower:
        return f"🤖 **AI Cleaner Suggestion**: Based on your dataset profile, missing numeric values should be imputed using **Mean/Median Imputation**, and duplicates dropped via `drop_duplicates()`. Use the **AI Data Cleaner** tab for automated 1-click execution!"

    else:
        return f"🤖 **IntelliHub AI Analyst**: In analyzing **'{dataset.name if dataset else 'your dataset'}'**, we recommend running Exploratory Data Analysis (EDA) first to examine distributions, followed by AutoML training in the ML Studio to select the best predictive model!"
