from django.shortcuts import render
from django.http import HttpResponse
import requests

# Create your views here.
def nav_home(request):
    return render(request, "rest/home.html")

def nav_signup(request):
    return render(request, "rest/signup.html")

def nav_signin(request):
    return render(request, "rest/signin.html")

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
    api_response = (requests.post(api_url, data=api_payload, headers=api_headers)).json()

    # if we don't find any results for the provided city,
    if len(api_response['results']['data']) == 0:
        context = {
            'error_msg' : citychoice
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
    api_response = []
    while not 'status' in api_response:
        api_response = (requests.post(api_url, data=api_payload, headers=api_headers)).json()

    businesses = []

    # get our list of businesses using provided dietary restriction
    for i in range(len(api_response['results']['data'])):
        diets = []
        for diet in api_response['results']['data'][i]['dietary_restrictions']:
            diets.append(diet)

        if diet_choice == '0':
            businesses.append({'name' : api_response['results']['data'][i]['name'], 
                               'id' : api_response['results']['data'][i]['location_id']})
        else:
            for diet in diets:
                if diet_choice == diet['key']:
                    businesses.append({'name' : api_response['results']['data'][i]['name'], 
                                       'id' : api_response['results']['data'][i]['location_id']})
    
    # select the diet to check by default
    default_checked = {
        '10665' : '',
        '10697' : '',
        '10992' : '',
        '0' : ''
    }
    default_checked[diet_choice] = 'checked'

    # send HTML context
    context = {
        'pagenum' : pagenum,
        'citystring' : city_string,
        'cityname' : city_name,
        'business_list' : businesses,
        'results' : str(len(businesses)),
        'results_hidden' : str(20 - len(businesses)),
        'checked' : default_checked
    }

    return render(request, "rest/search_results.html", context)

def view_business(request):
    location_id = request.GET['business_id']

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

    return render(request, "rest/business.html", context)