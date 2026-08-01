from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.datasets.models import Dataset
from .services import ask_ai_data_analyst

@login_required
def assistant_chat_view(request, dataset_id=None):
    datasets = Dataset.objects.filter(user=request.user)
    selected_dataset = None
    if dataset_id:
        selected_dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)
    elif datasets.exists():
        selected_dataset = datasets.first()
        
    response_text = None
    user_query = ""
    
    if request.method == 'POST':
        user_query = request.POST.get('query', '')
        if user_query:
            response_text = ask_ai_data_analyst(user_query, dataset=selected_dataset)
            
    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
        'user_query': user_query,
        'response_text': response_text,
    }
    return render(request, 'assistant/chat.html', context)
