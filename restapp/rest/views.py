from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Avg
from .models import Note, Restaurant, Favorite, Rating
from .forms import *
from django.contrib.auth.decorators import login_required
import requests
import time
import json

# Create your views here.
def nav_home(request):
    return render(request, "rest/home.html")


def register(request):
    form = CreateUserForm(request.POST)
    if form.is_valid():
        user = form.save()
        
        group = Group.objects.get(name='foodie')
        user.groups.add(group)
        #user = User.objects.create(user=user)
        user.save()
        return redirect('/accounts/login/?next=/')
    context={'form':form}
        
    return render(request, 'registration/register.html', context)


@login_required
def nav_search(request):
    return render(request, "rest/search.html")


@login_required
def search_results(request):
    # get request headers
    citychoice = request.GET['city']
    pagenum = request.GET['page']
    diet_choice = request.GET['diet_restrict']
    
    # get city location through API
    api_url = "https://restaurants222.p.rapidapi.com/typeahead"
    api_payload = {
	    "q": str(citychoice),
	    "language": "en_US"
    }
    api_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "5b50f152a6mshc0ecd677d4f5b6ap1d7c6ajsna7b84abf99ea",
        "X-RapidAPI-Host": "restaurants222.p.rapidapi.com"
    }
    next_request = time.time() + 1
    api_response = (requests.post(api_url, data=api_payload, headers=api_headers)).json()
    while not 'status' in api_response:
        if time.time() > next_request:
            next_request = time.time() + 1
            print("Bad request, trying again...")
            api_response = (requests.post(api_url, data=api_payload, headers=api_headers)).json()

    if not 'results' in api_response:
        context = {
            'error_badcall' : citychoice
        }
        return render(request, "rest/search.html", context)

    # if we don't find any results for the provided city,
    if len(api_response['results']['data']) == 0:
        context = {
            'error_nocity' : citychoice
        }
        return render(request, "rest/search.html", context)
        
    # extract city data
    city_id = api_response['results']['data'][0]['result_object']['location_id']
    city_string = api_response['results']['data'][0]['result_object']['location_string']
    city_name = api_response['results']['data'][0]['result_object']['name']

    # search city through API
    api_url = "https://restaurants222.p.rapidapi.com/search"
    api_payload = {
        "location_id": str(city_id),
        "language": "en_US",
        "currency": "USD",
        "offset": str((int(pagenum) - 1) * 20)
    }
    api_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "5b50f152a6mshc0ecd677d4f5b6ap1d7c6ajsna7b84abf99ea",
        "X-RapidAPI-Host": "restaurants222.p.rapidapi.com"
    }
    
    # check if we got a bad response, and try again
    next_request = time.time() + 1
    api_response = (requests.post(api_url, data=api_payload, headers=api_headers)).json()
    while not 'status' in api_response:
        if time.time() > next_request:
            next_request = time.time() + 1
            print("Bad request, trying again...")
            api_response = (requests.post(api_url, data=api_payload, headers=api_headers)).json()

    if not 'results' in api_response:
        context = {
            'error_badcall' : citychoice
        }
        return render(request, "rest/search.html", context)

    businesses = []

    # get our list of businesses using provided dietary restriction
    for i in range(len(api_response['results']['data'])):
        diets = []
        for diet in api_response['results']['data'][i]['dietary_restrictions']:
            diets.append(diet)

        numnotes = str(len(Note.objects.filter(business_id=int(api_response['results']['data'][i]['location_id']))))

        if diet_choice == '0':
            businesses.append({'name' : api_response['results']['data'][i]['name'], 
                               'id' : api_response['results']['data'][i]['location_id'],
                               'ranking' : api_response['results']['data'][i]['ranking_position'],
                               'notes' : numnotes
                               })
        else:
            for diet in diets:
                if diet_choice == diet['key']:
                    businesses.append({'name' : api_response['results']['data'][i]['name'], 
                                       'id' : api_response['results']['data'][i]['location_id'],
                                       'ranking' : api_response['results']['data'][i]['ranking_position'],
                                       'notes' : numnotes
                                       })
    
    # select the diet to check by default
    default_checked = {
        '10665' : '',
        '10697' : '',
        '10992' : '',
        '0' : ''
    }
    default_checked[diet_choice] = 'selected'

    # send HTML context
    context = {
        'pagenum' : pagenum,
        'nextpage' : str(int(pagenum) + 1),
        'prevpage' : str(max(1, int(pagenum) - 1)),
        'citystring' : city_string,
        'cityname' : city_name,
        'business_list' : businesses,
        'results' : str(len(businesses)),
        'results_hidden' : str(20 - len(businesses)),
        'checked' : default_checked
    }

    return render(request, "rest/search_results.html", context)


@login_required
def view_business(request):
    if request.method == 'GET':
        location_id = request.GET['business_id']
    elif request.method == 'POST':
        location_id = request.POST['business_id']

    api_url = "https://restaurants222.p.rapidapi.com/detail"
    api_payload = {
        "location_id": str(location_id),
        "language": "en_US",
        "currency": "USD"
    }
    api_headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": "5b50f152a6mshc0ecd677d4f5b6ap1d7c6ajsna7b84abf99ea",
        "X-RapidAPI-Host": "restaurants222.p.rapidapi.com"
    }
    next_request = time.time() + 1
    api_response = (requests.post(api_url, data=api_payload, headers=api_headers)).json()
    while not 'status' in api_response:
        if time.time() > next_request:
            next_request = time.time() + 1
            print("Bad request, trying again...")
            api_response = (requests.post(api_url, data=api_payload, headers=api_headers)).json()

    diet_restricts = []
    for i in range(len(api_response['results']['dietary_restrictions'])):
        diet_restricts.append(api_response['results']['dietary_restrictions'][i]['name'])

    business = {
        'id' : str(location_id),
        'name' : api_response['results']['name'],
        'address' : api_response['results']['address'],
        'diets' : diet_restricts,
    }

    context = {
        'business' : business
    }

    is_favorited = Favorite.objects.filter(user=request.user, restaurant__business_id=location_id).exists()
    context.update({'is_favorited': is_favorited})

    if request.method == 'POST':
        newnote = Note(business_id=int(location_id), note_text=request.POST['note_text'], note_publisher="Anonymous", note_pub_date=timezone.now())
        newnote.save()

    noteslist = Note.objects.order_by("-note_pub_date").filter(business_id=str(location_id))[:20]

    if len(noteslist) == 0:
        context.update({'err_nonotes' : 'error'})

    context.update({'notes': noteslist})

    return render(request, "rest/business.html", context)


@login_required
def create_restaurant(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            business_id = data.get('business_id')
            name = data.get('name')
            address = data.get('address')
            diets = data.get('diets')

            # Check if the restaurant already exists internally.
            restaurant, created = Restaurant.objects.get_or_create(
                business_id=business_id,
                defaults={'name': name, 'address': address, 'diets': diets}
            )

            return JsonResponse({'success': True, 'restaurant_id': restaurant.business_id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def toggle_favorite(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, business_id=restaurant_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)
    if not created:
        favorite.delete()
        return JsonResponse({'success': True, 'message': 'Removed restaurant from user\'s favorites list'})
    else:
        return JsonResponse({'success': True, 'message': 'Added restaurant to user\'s favorites list'})


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('restaurant')
    ratings_data = {}

    for favorite in favorites:
        restaurant = favorite.restaurant
        user_rating = Rating.objects.filter(user=request.user, restaurant=restaurant).first()
        community_avg = Rating.objects.filter(restaurant=restaurant).aggregate(models.Avg('score'))['score__avg']

        ratings_data[restaurant.business_id] = {
            'user_rating': user_rating.score if user_rating else "Not yet rated",
            'community_avg': round(community_avg, 1) if community_avg else "Not yet rated",
        }

    context = {
        'favorites': favorites,
        'ratings_data': ratings_data
    }

    return render(request, 'rest/favorites_list.html', context)


@login_required
def rate_restaurant(request, restaurant_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        score = int(request.POST.get('score'))
        restaurant = get_object_or_404(Restaurant, business_id=restaurant_id)

        Rating.objects.update_or_create(
            user=request.user,
            restaurant=restaurant,
            defaults={'score': score}
        )

        community_avg = Rating.objects.filter(restaurant=restaurant).aggregate(models.Avg('score'))['score__avg']
        community_avg = round(community_avg, 1) if community_avg else "Not rated yet"

        return JsonResponse({
            'success': True,
            'new_score': score,
            'new_average': community_avg
        })
    
    return JsonResponse({'success': False}, status=400)