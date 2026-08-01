from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from apps.datasets.models import Dataset
from apps.datasets.utils import load_dataframe
from .services import (
    get_eda_summary_statistics,
    compute_two_way_crosstab,
    generate_networkx_visualization,
    create_plotly_chart
)

@login_required
def eda_dashboard_view(request, dataset_id=None):
    datasets = Dataset.objects.filter(user=request.user)
    if not datasets.exists():
        messages.warning(request, "Please upload a dataset to perform Exploratory Data Analysis.")
        return redirect('datasets:list')
        
    if dataset_id:
        selected_dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    else:
        selected_dataset = datasets.first()
        
    version = selected_dataset.latest_version
    df = load_dataframe(version.file.path) if (version and version.file) else None
    
    if df is None or df.empty:
        messages.error(request, "Selected dataset is empty or missing.")
        return redirect('datasets:list')
        
    eda_stats = get_eda_summary_statistics(df)
    networkx_json, node_degrees = generate_networkx_visualization(df)
    
    # Selected Chart Parameters
    chart_type = request.GET.get('chart_type', 'histogram')
    x_col = request.GET.get('x_col', df.columns[0])
    y_col = request.GET.get('y_col', df.columns[1] if len(df.columns) > 1 else df.columns[0])
    color_col = request.GET.get('color_col', '')
    
    # Heatmap default chart
    heatmap_json = create_plotly_chart(df, 'heatmap', x_col=df.columns[0])
    custom_chart_json = create_plotly_chart(df, chart_type, x_col, y_col, color_col if color_col else None)
    
    # Crosstab (Unit 1.5)
    crosstab_col1 = request.GET.get('ct_col1', eda_stats['cat_cols'][0] if eda_stats['cat_cols'] else df.columns[0])
    crosstab_col2 = request.GET.get('ct_col2', eda_stats['cat_cols'][1] if len(eda_stats['cat_cols']) > 1 else df.columns[1] if len(df.columns) > 1 else df.columns[0])
    crosstab_html = compute_two_way_crosstab(df, crosstab_col1, crosstab_col2)

    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
        'version': version,
        'all_columns': df.columns.tolist(),
        'num_cols': eda_stats['num_cols'],
        'cat_cols': eda_stats['cat_cols'],
        'strong_correlations': eda_stats['strong_correlations'],
        'networkx_json': networkx_json,
        'node_degrees': node_degrees,
        'heatmap_json': heatmap_json,
        'custom_chart_json': custom_chart_json,
        'chart_type': chart_type,
        'x_col': x_col,
        'y_col': y_col,
        'color_col': color_col,
        'crosstab_col1': crosstab_col1,
        'crosstab_col2': crosstab_col2,
        'crosstab_html': crosstab_html,
    }
    return render(request, 'eda/eda_dashboard.html', context)
