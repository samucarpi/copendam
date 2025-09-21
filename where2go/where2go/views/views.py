from django.shortcuts import render, redirect
from ..models import Categories, FoodPoll
from django.db.models import Count
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    categories = Categories.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        if category_id:
            category = Categories.objects.get(id=category_id)
            FoodPoll.objects.update_or_create(user=request.user, defaults={'category': category})
            return redirect('poll')

    vote_counts = FoodPoll.objects.values('category__name').annotate(votes=Count('category')).order_by('-votes')

    context = {
        'categories': categories,
        'vote_counts': vote_counts,
    }
    return render(request, 'dashboard/dashboard.html', context)

def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')
