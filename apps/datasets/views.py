from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.files.base import ContentFile
import os
import pandas as pd

from .models import Dataset, DatasetVersion
from .utils import analyze_dataset_metadata, load_dataframe

@login_required
def dataset_list_view(request):
    search_query = request.GET.get('q', '')
    filter_fav = request.GET.get('fav', '')
    
    datasets = Dataset.objects.filter(user=request.user)
    if search_query:
        datasets = datasets.filter(name__icontains=search_query)
    if filter_fav == 'true':
        datasets = datasets.filter(is_favorite=True)
        
    datasets = datasets.order_by('-updated_at')
    
    # Check role quota
    can_upload = request.user.can_upload_dataset
    max_allowed = request.user.max_datasets_allowed
    current_count = datasets.count()

    context = {
        'datasets': datasets,
        'search_query': search_query,
        'filter_fav': filter_fav,
        'can_upload': can_upload,
        'max_allowed': max_allowed,
        'current_count': current_count,
    }
    return render(request, 'datasets/dataset_list.html', context)

@login_required
def dataset_upload_view(request):
    if not request.user.can_upload_dataset:
        messages.error(request, f"Upload quota reached for Student role ({request.user.max_datasets_allowed} datasets max). Upgrade your role or delete an existing dataset.")
        return redirect('datasets:list')

    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        name = request.POST.get('name', uploaded_file.name)
        description = request.POST.get('description', '')
        
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        file_format = 'CSV'
        if ext in ['.xlsx', '.xls']:
            file_format = 'EXCEL'
        elif ext == '.json':
            file_format = 'JSON'
            
        dataset = Dataset.objects.create(
            user=request.user,
            name=name,
            description=description,
            file_format=file_format
        )
        
        version = DatasetVersion.objects.create(
            dataset=dataset,
            version_number=1,
            file=uploaded_file
        )
        
        # Analyze metadata
        try:
            meta = analyze_dataset_metadata(version.file.path)
            version.row_count = meta['row_count']
            version.column_count = meta['column_count']
            version.memory_usage_bytes = meta['memory_usage_bytes']
            version.memory_usage_str = meta['memory_usage_str']
            version.duplicate_rows = meta['duplicate_rows']
            version.missing_values = meta['missing_values']
            version.numerical_cols = meta['numerical_cols']
            version.categorical_cols = meta['categorical_cols']
            version.save()
            messages.success(request, f"Dataset '{dataset.name}' uploaded successfully (Version 1).")
            return redirect('datasets:detail', dataset_id=dataset.id)
        except Exception as e:
            dataset.delete()
            messages.error(request, f"Error parsing dataset file: {str(e)}")
            return redirect('datasets:upload')
            
    return render(request, 'datasets/dataset_upload.html')

@login_required
def dataset_detail_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    v_id = request.GET.get('version')
    if v_id:
        version = get_object_or_404(DatasetVersion, id=v_id, dataset=dataset)
    else:
        version = dataset.latest_version

    meta = {}
    describe_html = ""
    preview_rows = []
    headers = []
    
    if version and version.file:
        try:
            meta = analyze_dataset_metadata(version.file.path)
            df = load_dataframe(version.file.path)
            describe_df = df.describe(include='all').fillna('')
            describe_html = describe_df.to_html(classes='table table-dark table-striped table-sm table-hover text-nowrap', border=0)
            headers = df.columns.tolist()
            preview_rows = df.head(15).values.tolist()
        except Exception as e:
            messages.error(request, f"Failed to load dataset data: {str(e)}")

    context = {
        'dataset': dataset,
        'version': version,
        'all_versions': dataset.versions.all(),
        'meta': meta,
        'describe_html': describe_html,
        'headers': headers,
        'preview_rows': preview_rows,
    }
    return render(request, 'datasets/dataset_detail.html', context)

@login_required
def dataset_new_version_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        latest_ver = dataset.latest_version
        next_ver_num = (latest_ver.version_number + 1) if latest_ver else 1
        
        version = DatasetVersion.objects.create(
            dataset=dataset,
            version_number=next_ver_num,
            file=uploaded_file
        )
        try:
            meta = analyze_dataset_metadata(version.file.path)
            version.row_count = meta['row_count']
            version.column_count = meta['column_count']
            version.memory_usage_bytes = meta['memory_usage_bytes']
            version.memory_usage_str = meta['memory_usage_str']
            version.duplicate_rows = meta['duplicate_rows']
            version.missing_values = meta['missing_values']
            version.numerical_cols = meta['numerical_cols']
            version.categorical_cols = meta['categorical_cols']
            version.save()
            dataset.save()  # update updated_at timestamp
            messages.success(request, f"Uploaded Version {next_ver_num} for '{dataset.name}'.")
        except Exception as e:
            version.delete()
            messages.error(request, f"Failed to upload dataset version: {str(e)}")
            
    return redirect('datasets:detail', dataset_id=dataset.id)

@login_required
def dataset_toggle_fav_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    dataset.is_favorite = not dataset.is_favorite
    dataset.save()
    return redirect('datasets:list')

@login_required
def dataset_delete_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    name = dataset.name
    dataset.delete()
    messages.success(request, f"Dataset '{name}' deleted.")
    return redirect('datasets:list')

@login_required
def dataset_download_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    v_id = request.GET.get('version')
    if v_id:
        version = get_object_or_404(DatasetVersion, id=v_id, dataset=dataset)
    else:
        version = dataset.latest_version
        
    if version and version.file:
        return FileResponse(open(version.file.path, 'rb'), as_attachment=True, filename=os.path.basename(version.file.name))
    messages.error(request, "File not found.")
    return redirect('datasets:detail', dataset_id=dataset.id)
