from django.shortcuts import render, redirect
from ..models import Categories, FoodPoll, PresencePoll
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import json
from ..models import Categories, FoodPoll, PresencePoll

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

@login_required
def food_poll_vote_ajax(request):
    """Gestisce i voti del sondaggio cibo tramite AJAX - supporta voti multipli"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_id = data.get('category_id')
            
            if category_id:
                try:
                    category = Categories.objects.get(id=category_id)
                    
                    # Controlla se l'utente ha già votato per questa categoria
                    existing_vote = FoodPoll.objects.filter(user=request.user, category=category).first()
                    
                    if existing_vote:
                        # Se esiste già, rimuovi il voto (toggle off)
                        existing_vote.delete()
                    else:
                        # Se non esiste, aggiungi il voto (toggle on)
                        FoodPoll.objects.create(user=request.user, category=category)
                        
                except Categories.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Categoria non trovata'})
            
            # Restituisci i dati aggiornati del sondaggio cibo
            poll_data = get_food_poll_data_dict()
            user_votes = get_user_food_votes(request.user)
            
            return JsonResponse({
                'success': True,
                'poll_data': poll_data,
                'user_votes': user_votes
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Dati JSON non validi'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Metodo non consentito'})

@login_required
def food_poll_data_ajax(request):
    """Restituisce i dati correnti del sondaggio cibo"""
    if request.method == 'GET':
        poll_data = get_food_poll_data_dict()
        user_votes = get_user_food_votes(request.user)
        
        return JsonResponse({
            'success': True,
            'poll_data': poll_data,
            'user_votes': user_votes
        })
    
    return JsonResponse({'success': False, 'error': 'Metodo non consentito'})

def get_food_poll_data_dict():
    """Restituisce un dizionario con i dati del sondaggio cibo"""
    categories = Categories.objects.all()
    poll_data = {}
    
    for category in categories:
        votes = FoodPoll.objects.filter(category=category)
        vote_count = votes.count()
        voters = [vote.user.username for vote in votes]
        
        poll_data[str(category.id)] = {
            'count': vote_count,
            'voters': voters,
            'category_name': category.name
        }
    
    return poll_data

def get_user_food_votes(user):
    """Restituisce una lista degli ID delle categorie per cui l'utente ha votato nel sondaggio cibo"""
    votes = FoodPoll.objects.filter(user=user)
    return [vote.category.id for vote in votes]

def get_user_food_vote(user):
    """Restituisce l'ID della categoria per cui l'utente ha votato nel sondaggio cibo, o None (mantenuto per compatibilità)"""
    try:
        vote = FoodPoll.objects.get(user=user)
        return vote.category.id
    except FoodPoll.DoesNotExist:
        return None
    except FoodPoll.MultipleObjectsReturned:
        # Se ci sono voti multipli, restituisce il primo
        vote = FoodPoll.objects.filter(user=user).first()
        return vote.category.id if vote else None


# PRESENCE POLL VIEWS

@login_required
def presence_poll_vote_ajax(request):
    """Gestisce i voti del sondaggio presenza tramite AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            presence_value = data.get('presence_value')  # 'present', 'absent', or None
            
            if presence_value in ['present', 'absent']:
                # Aggiorna o crea il voto di presenza
                PresencePoll.objects.update_or_create(
                    user=request.user,
                    defaults={'presence': presence_value}
                )
            elif presence_value is None:
                # Rimuovi il voto se l'utente vuole annullare
                PresencePoll.objects.filter(user=request.user).delete()
            else:
                return JsonResponse({'success': False, 'error': 'Valore di presenza non valido'})
            
            # Restituisci i dati aggiornati del sondaggio presenza
            presence_data = get_presence_poll_data_dict()
            user_vote = get_user_presence_poll_vote(request.user)
            
            return JsonResponse({
                'success': True,
                'presence_data': presence_data,
                'user_vote': user_vote
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Dati JSON non validi'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Metodo non consentito'})


@login_required
def presence_poll_data_ajax(request):
    """Restituisce i dati correnti del sondaggio presenza"""
    if request.method == 'GET':
        presence_data = get_presence_poll_data_dict()
        user_vote = get_user_presence_poll_vote(request.user)
        
        return JsonResponse({
            'success': True,
            'presence_data': presence_data,
            'user_vote': user_vote
        })
    
    return JsonResponse({'success': False, 'error': 'Metodo non consentito'})


def get_presence_poll_data_dict():
    """Restituisce un dizionario con i dati del sondaggio presenza"""
    present_votes = PresencePoll.objects.filter(presence='present')
    absent_votes = PresencePoll.objects.filter(presence='absent')
    
    present_count = present_votes.count()
    absent_count = absent_votes.count()
    
    present_voters = [vote.user.username for vote in present_votes]
    absent_voters = [vote.user.username for vote in absent_votes]
    
    presence_data = {
        'present': {
            'count': present_count,
            'voters': present_voters
        },
        'absent': {
            'count': absent_count,
            'voters': absent_voters
        }
    }
    
    return presence_data


def get_user_presence_poll_vote(user):
    """Restituisce il voto di presenza dell'utente ('present', 'absent', o None)"""
    try:
        presence_vote = PresencePoll.objects.get(user=user)
        return presence_vote.presence
    except PresencePoll.DoesNotExist:
        return None
