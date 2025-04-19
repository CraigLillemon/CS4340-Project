from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import Note
from .forms import *
import requests
import time

# Create your views here.
def nav_home(request):
    return render(request, "rest/home.html")

def nav_signup(request):
    return render(request, "rest/signup.html")

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


def nav_search(request):
    return render(request, "rest/search.html")

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

    if request.method == 'POST':
        newnote = Note(business_id=int(location_id), note_text=request.POST['note_text'], note_publisher="Anonymous", note_pub_date=timezone.now())
        newnote.save()

    noteslist = Note.objects.order_by("-note_pub_date").filter(business_id=str(location_id))[:20]

    if len(noteslist) == 0:
        context.update({'err_nonotes' : 'error'})

    context.update({'notes': noteslist})

    return render(request, "rest/business.html", context)