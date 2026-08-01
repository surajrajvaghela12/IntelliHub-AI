import pandas as pd
import numpy as np
import os
import joblib
import json

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import (
    r2_score, mean_absolute_error, mean_squared_error,
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)

from apps.datasets.utils import load_dataframe

def prepare_dataset_for_ml(df, target_col, feature_cols=None):
    """
    Preprocesses dataset: handles missing values, encodes categories, splits X and y.
    Maps to Unit 3 of Syllabus.
    """
    df_clean = df.copy()
    
    # Fill missing values
    for col in df_clean.columns:
        if df_clean[col].isna().sum() > 0:
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
            else:
                df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0] if not df_clean[col].mode().empty else 'Unknown')

    encoders = {}
    for col in df_clean.select_dtypes(include=['object', 'category']).columns:
        le = LabelEncoder()
        df_clean[col] = le.fit_transform(df_clean[col].astype(str))
        encoders[col] = le

    if not feature_cols:
        feature_cols = [c for c in df_clean.columns if c != target_col]
        
    X = df_clean[feature_cols]
    y = df_clean[target_col] if target_col in df_clean.columns else None
    
    return X, y, feature_cols, encoders


def train_regression_model(file_path, target_col, feature_cols, algorithm='multiple_linear', poly_degree=2):
    """
    Trains Regression Model (Unit 4 syllabus):
    Simple/Multiple Linear, Polynomial Regression, Ridge, Lasso.
    Evaluates R2, MAE, MSE, RMSE.
    """
    df = load_dataframe(file_path)
    X, y, feature_cols, encoders = prepare_dataset_for_ml(df, target_col, feature_cols)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    if algorithm == 'polynomial':
        poly = PolynomialFeatures(degree=poly_degree)
        X_train_trans = poly.fit_transform(X_train)
        X_test_trans = poly.transform(X_test)
        model = LinearRegression()
        model.fit(X_train_trans, y_train)
        y_pred = model.predict(X_test_trans)
    elif algorithm == 'ridge':
        model = Ridge()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    elif algorithm == 'lasso':
        model = Lasso()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    else: # simple or multiple linear
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
    r2 = float(r2_score(y_test, y_pred))
    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    
    metrics = {
        'r2_score': round(r2, 4),
        'mae': round(mae, 4),
        'mse': round(mse, 4),
        'rmse': round(rmse, 4),
        'accuracy': round(max(0.0, r2), 4),
    }
    
    return model, metrics, feature_cols


def train_classification_model(file_path, target_col, feature_cols, algorithm='random_forest'):
    """
    Trains Classification Model (Unit 5 syllabus):
    kNN, Decision Tree with Entropy criterion, Random Forest, SVM.
    Evaluates Confusion Matrix, Accuracy, Error Rate, Sensitivity, Specificity.
    """
    df = load_dataframe(file_path)
    X, y, feature_cols, encoders = prepare_dataset_for_ml(df, target_col, feature_cols)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    if algorithm == 'knn':
        model = KNeighborsClassifier(n_neighbors=5)
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    elif algorithm == 'decision_tree':
        # Unit 5.1: Decision Tree using Entropy criterion
        model = DecisionTreeClassifier(criterion='entropy', random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    elif algorithm == 'svm':
        model = SVC(probability=True, random_state=42)
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    elif algorithm == 'logistic':
        model = LogisticRegression(max_iter=1000)
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    else: # random_forest
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
    acc = float(accuracy_score(y_test, y_pred))
    error_rate = float(1.0 - acc)
    
    cm = confusion_matrix(y_test, y_pred)
    cm_list = cm.tolist()
    
    # Sensitivity (Recall) & Specificity
    if len(cm) == 2:
        tn, fp, fn, tp = cm.ravel()
        sensitivity = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    else:
        sensitivity = float(recall_score(y_test, y_pred, average='macro'))
        specificity = float(acc)
        
    prec = float(precision_score(y_test, y_pred, average='macro', zero_division=0))
    rec = float(recall_score(y_test, y_pred, average='macro', zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average='macro', zero_division=0))
    
    metrics = {
        'accuracy': round(acc, 4),
        'error_rate': round(error_rate, 4),
        'sensitivity': round(sensitivity, 4),
        'specificity': round(specificity, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'confusion_matrix': cm_list,
    }
    
    return model, metrics, feature_cols


def run_automl(file_path, target_col, task_type='classification'):
    """
    AutoML Engine: automatically trains candidate models, ranks them, and selects the best.
    """
    df = load_dataframe(file_path)
    X, y, feature_cols, encoders = prepare_dataset_for_ml(df, target_col)
    
    candidates = []
    if task_type == 'regression':
        algos = ['multiple_linear', 'polynomial', 'ridge', 'lasso']
        for alg in algos:
            try:
                model, metrics, _ = train_regression_model(file_path, target_col, feature_cols, algorithm=alg)
                candidates.append({
                    'algorithm': alg.replace('_', ' ').title(),
                    'metrics': metrics,
                    'score': metrics['accuracy'],
                    'model': model
                })
            except Exception:
                pass
    else:
        algos = ['random_forest', 'decision_tree', 'knn', 'svm', 'logistic']
        for alg in algos:
            try:
                model, metrics, _ = train_classification_model(file_path, target_col, feature_cols, algorithm=alg)
                candidates.append({
                    'algorithm': alg.replace('_', ' ').title(),
                    'metrics': metrics,
                    'score': metrics['accuracy'],
                    'model': model
                })
            except Exception:
                pass
                
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates
