from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from apps.accounts.models import User
from apps.datasets.models import Dataset
from apps.ml_studio.models import TrainedModel, PredictionHistory

def is_admin_check(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser or user.is_staff)

@login_required
@user_passes_test(is_admin_check)
def admin_dashboard_view(request):
    users = User.objects.all().order_by('-date_joined')
    datasets = Dataset.objects.all().order_by('-created_at')[:10]
    models = TrainedModel.objects.all().order_by('-created_at')[:10]
    
    total_users = users.count()
    total_datasets = Dataset.objects.count()
    total_models = TrainedModel.objects.count()
    total_predictions = PredictionHistory.objects.count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        target_user_id = request.POST.get('user_id')
        if target_user_id:
            u = get_object_or_404(User, id=target_user_id)
            if action == 'toggle_ban':
                u.is_banned = not u.is_banned
                u.save()
                messages.success(request, f"User '{u.username}' status updated to {'Banned' if u.is_banned else 'Active'}.")
            elif action == 'change_role':
                new_role = request.POST.get('role')
                if new_role in dict(User.ROLE_CHOICES):
                    u.role = new_role
                    u.save()
                    messages.success(request, f"Updated role for '{u.username}' to {new_role}.")
                    
        return redirect('admin_panel:home')

    context = {
        'users': users,
        'datasets': datasets,
        'models': models,
        'total_users': total_users,
        'total_datasets': total_datasets,
        'total_models': total_models,
        'total_predictions': total_predictions,
    }
    return render(request, 'admin_panel/admin_dashboard.html', context)
