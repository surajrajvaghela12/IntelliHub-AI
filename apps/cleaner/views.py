from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os
import pandas as pd
from django.core.files.base import ContentFile

from apps.datasets.models import Dataset, DatasetVersion
from apps.datasets.utils import load_dataframe, analyze_dataset_metadata
from .models import CleaningHistory
from .services import generate_cleaning_recommendations, perform_auto_clean, perform_custom_clean

@login_required
def cleaner_home_view(request, dataset_id=None):
    datasets = Dataset.objects.filter(user=request.user)
    if not datasets.exists():
        messages.warning(request, "Please upload or select a dataset first to start cleaning.")
        return redirect('datasets:list')
        
    if dataset_id:
        selected_dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    else:
        selected_dataset = datasets.first()
        
    version = selected_dataset.latest_version
    recommendations = []
    before_rows = 0
    before_missing = 0
    preview_rows = []
    headers = []
    
    if version and version.file:
        df = load_dataframe(version.file.path)
        recommendations = generate_cleaning_recommendations(df)
        before_rows = len(df)
        before_missing = int(df.isna().sum().sum())
        headers = df.columns.tolist()
        preview_rows = df.head(10).values.tolist()
        
    history = selected_dataset.cleaning_history.all()[:10]
    
    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
        'version': version,
        'recommendations': recommendations,
        'before_rows': before_rows,
        'before_missing': before_missing,
        'headers': headers,
        'preview_rows': preview_rows,
        'history': history,
    }
    return render(request, 'cleaner/cleaner_home.html', context)


@login_required
def trigger_auto_clean_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    version = dataset.latest_version
    if not version or not version.file:
        messages.error(request, "No valid dataset file found.")
        return redirect('cleaner:home', dataset_id=dataset.id)
        
    cleaned_df, res = perform_auto_clean(version.file.path)
    
    # Save as new dataset version
    csv_data = cleaned_df.to_csv(index=False)
    next_ver = version.version_number + 1
    new_filename = f"cleaned_{dataset.name}_v{next_ver}.csv"
    
    new_version = DatasetVersion(dataset=dataset, version_number=next_ver)
    new_version.file.save(new_filename, ContentFile(csv_data))
    
    # Analyze new metadata
    meta = analyze_dataset_metadata(new_version.file.path)
    new_version.row_count = meta['row_count']
    new_version.column_count = meta['column_count']
    new_version.memory_usage_bytes = meta['memory_usage_bytes']
    new_version.memory_usage_str = meta['memory_usage_str']
    new_version.duplicate_rows = meta['duplicate_rows']
    new_version.missing_values = meta['missing_values']
    new_version.numerical_cols = meta['numerical_cols']
    new_version.categorical_cols = meta['categorical_cols']
    new_version.save()
    
    # Save Cleaning History entry
    log_text = " | ".join(res['logs']) if res['logs'] else "Cleaned dataset: no issues detected."
    CleaningHistory.objects.create(
        user=request.user,
        dataset=dataset,
        action_type="Auto Clean Pipeline",
        before_rows=res['before_rows'],
        after_rows=res['after_rows'],
        before_missing=res['before_missing'],
        after_missing=res['after_missing'],
        details=log_text
    )
    
    messages.success(request, f"Auto Clean completed successfully! Created Version {next_ver}. {log_text}")
    return redirect('cleaner:home', dataset_id=dataset.id)


@login_required
def trigger_custom_clean_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    version = dataset.latest_version
    
    if request.method == 'POST':
        action = request.POST.get('action')
        column = request.POST.get('column')
        
        cleaned_df, res = perform_custom_clean(version.file.path, action, column)
        
        csv_data = cleaned_df.to_csv(index=False)
        next_ver = version.version_number + 1
        new_filename = f"cleaned_{action}_{dataset.name}_v{next_ver}.csv"
        
        new_version = DatasetVersion(dataset=dataset, version_number=next_ver)
        new_version.file.save(new_filename, ContentFile(csv_data))
        
        meta = analyze_dataset_metadata(new_version.file.path)
        new_version.row_count = meta['row_count']
        new_version.column_count = meta['column_count']
        new_version.memory_usage_bytes = meta['memory_usage_bytes']
        new_version.memory_usage_str = meta['memory_usage_str']
        new_version.duplicate_rows = meta['duplicate_rows']
        new_version.missing_values = meta['missing_values']
        new_version.numerical_cols = meta['numerical_cols']
        new_version.categorical_cols = meta['categorical_cols']
        new_version.save()
        
        log_text = " | ".join(res['logs']) if res['logs'] else f"Action '{action}' executed."
        CleaningHistory.objects.create(
            user=request.user,
            dataset=dataset,
            action_type=f"Custom: {action} ({column or 'all'})",
            before_rows=res['before_rows'],
            after_rows=res['after_rows'],
            before_missing=res['before_missing'],
            after_missing=res['after_missing'],
            details=log_text
        )
        
        messages.success(request, f"Cleaning action '{action}' completed! Created Version {next_ver}.")
        
    return redirect('cleaner:home', dataset_id=dataset.id)
