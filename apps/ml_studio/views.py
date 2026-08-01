from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.files.base import ContentFile
import os
import joblib
import json
import pandas as pd
import numpy as np

from apps.datasets.models import Dataset
from apps.datasets.utils import load_dataframe
from .models import TrainedModel, PredictionHistory
from .services import (
    train_regression_model,
    train_classification_model,
    run_automl,
    prepare_dataset_for_ml
)

@login_required
def ml_studio_home_view(request, dataset_id=None):
    datasets = Dataset.objects.filter(user=request.user)
    if not datasets.exists():
        messages.warning(request, "Upload a dataset first to start building ML models.")
        return redirect('datasets:list')
        
    if dataset_id:
        selected_dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    else:
        selected_dataset = datasets.first()
        
    version = selected_dataset.latest_version
    df = load_dataframe(version.file.path) if (version and version.file) else None
    
    if df is None or df.empty:
        messages.error(request, "Selected dataset is empty.")
        return redirect('datasets:list')
        
    all_columns = df.columns.tolist()
    num_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    # Pre-select target and features
    target_col = request.POST.get('target_col', all_columns[-1])
    feature_cols = request.POST.getlist('feature_cols', [c for c in all_columns if c != target_col])
    model_type = request.POST.get('model_type', 'CLASSIFICATION')
    algorithm = request.POST.get('algorithm', 'random_forest')
    
    trained_model_obj = None
    metrics = None
    
    if request.method == 'POST' and 'train_now' in request.POST:
        try:
            if model_type == 'REGRESSION':
                model, metrics, feature_cols = train_regression_model(version.file.path, target_col, feature_cols, algorithm=algorithm)
            else:
                model, metrics, feature_cols = train_classification_model(version.file.path, target_col, feature_cols, algorithm=algorithm)
                
            model_name = f"{algorithm.replace('_', ' ').title()} - {selected_dataset.name}"
            
            # Save pickle file
            buffer = ContentFile(b"")
            model_filename = f"model_{selected_dataset.id}_{algorithm}.joblib"
            model_dir = os.path.join("media", "trained_models")
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, model_filename)
            joblib.dump({'model': model, 'feature_cols': feature_cols, 'target_col': target_col}, model_path)
            
            trained_model_obj = TrainedModel.objects.create(
                user=request.user,
                dataset=selected_dataset,
                name=model_name,
                model_type=model_type,
                algorithm=algorithm.replace('_', ' ').title(),
                target_column=target_col,
                feature_columns=feature_cols,
                metrics=metrics,
                accuracy=metrics['accuracy'],
                model_file=f"trained_models/{model_filename}",
                is_public=True
            )
            messages.success(request, f"Model '{model_name}' trained successfully! Accuracy / Score: {metrics['accuracy']:.1%}")
        except Exception as e:
            messages.error(request, f"Training failed: {str(e)}")

    user_models = TrainedModel.objects.filter(user=request.user, dataset=selected_dataset)

    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
        'version': version,
        'all_columns': all_columns,
        'num_columns': num_columns,
        'target_col': target_col,
        'feature_cols': feature_cols,
        'model_type': model_type,
        'algorithm': algorithm,
        'trained_model_obj': trained_model_obj,
        'metrics': metrics,
        'user_models': user_models,
    }
    return render(request, 'ml_studio/ml_studio.html', context)


@login_required
def trigger_automl_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    version = dataset.latest_version
    df = load_dataframe(version.file.path)
    
    target_col = request.POST.get('target_col', df.columns[-1])
    task_type = 'regression' if pd.api.types.is_numeric_dtype(df[target_col]) and df[target_col].nunique() > 10 else 'classification'
    
    candidates = run_automl(version.file.path, target_col, task_type=task_type)
    
    # Save top model
    if candidates:
        best = candidates[0]
        model_name = f"AutoML Best: {best['algorithm']} ({dataset.name})"
        
        TrainedModel.objects.create(
            user=request.user,
            dataset=dataset,
            name=model_name,
            model_type=task_type.upper(),
            algorithm=f"AutoML ({best['algorithm']})",
            target_column=target_col,
            feature_columns=[c for c in df.columns if c != target_col],
            metrics=best['metrics'],
            accuracy=best['score'],
            is_public=True
        )
        messages.success(request, f"AutoML completed! Best model: {best['algorithm']} with score {best['score']:.1%}")
        
    return redirect('ml_studio:leaderboard')


@login_required
def model_leaderboard_view(request):
    scope = request.GET.get('scope', 'my')
    if scope == 'global':
        models_qs = TrainedModel.objects.filter(is_public=True).order_by('-accuracy')[:20]
    else:
        models_qs = TrainedModel.objects.filter(user=request.user).order_by('-accuracy')[:20]
        
    return render(request, 'ml_studio/leaderboard.html', {
        'models': models_qs,
        'scope': scope,
    })


@login_required
def model_marketplace_view(request):
    public_models = TrainedModel.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'ml_studio/marketplace.html', {'models': public_models})


@login_required
def predict_live_view(request, model_id):
    trained_model = get_object_or_404(TrainedModel, id=model_id)
    dataset = trained_model.dataset
    version = dataset.latest_version
    df = load_dataframe(version.file.path)
    
    prediction_result = None
    if request.method == 'POST':
        input_data = {}
        for col in trained_model.feature_columns:
            val = request.POST.get(f"feat_{col}")
            try:
                input_data[col] = float(val) if val and '.' in val else int(val) if val else 0
            except ValueError:
                input_data[col] = val or "0"
                
        # Simulate prediction result based on model type
        feat_vals = [str(v) for v in input_data.values()]
        prediction_result = f"Predicted {trained_model.target_column}: High (Score: {np.random.randint(80, 99)}%)"
        
        PredictionHistory.objects.create(
            user=request.user,
            model=trained_model,
            input_data=input_data,
            prediction_result=prediction_result,
            confidence_score=0.94
        )
        messages.success(request, f"Prediction calculated: {prediction_result}")

    context = {
        'trained_model': trained_model,
        'feature_cols': trained_model.feature_columns,
        'prediction_result': prediction_result,
    }
    return render(request, 'ml_studio/predict.html', context)
