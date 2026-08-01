from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.contrib import messages

from apps.datasets.models import Dataset
from .services import generate_pdf_report

@login_required
def report_center_view(request, dataset_id=None):
    datasets = Dataset.objects.filter(user=request.user)
    if not datasets.exists():
        messages.warning(request, "Upload a dataset first to generate AI Reports.")
        return redirect('datasets:list')
        
    if dataset_id:
        selected_dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    else:
        selected_dataset = datasets.first()
        
    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
    }
    return render(request, 'reports/report_center.html', context)

@login_required
def download_pdf_report_view(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    pdf_buffer = generate_pdf_report(dataset, request.user)
    filename = f"IntelliHub_AI_Report_{dataset.name.replace(' ', '_')}.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename, content_type='application/pdf')
