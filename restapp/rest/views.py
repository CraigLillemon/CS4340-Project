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
    citychoice = request.GET['city']
    pagenum = request.GET['page']

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

    if len(api_response['results']['data']) == 0:
        context = {
            'error_msg' : citychoice
        }
        return render(request, "rest/search.html", context)
        
    city_id = api_response['results']['data'][0]['result_object']['location_id']
    city_string = api_response['results']['data'][0]['result_object']['location_string']
    city_name = api_response['results']['data'][0]['result_object']['name']

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
    api_response = (requests.post(api_url, data=api_payload, headers=api_headers)).json()

    businesses = []

    for i in range(len(api_response['results']['data'])):
        businesses.append({'name' : api_response['results']['data'][i]['name'],
                           'id' : api_response['results']['data'][i]['location_id']})

    print(city_name)

    context = {
        'pagenum' : pagenum,
        'citystring' : city_string,
        'cityname' : city_name,
        'business_list' : businesses
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
        'name' : api_response['results']['name'],
        'address' : api_response['results']['address'],
        'diets' : diet_restricts,
    }

    context = {
        'business' : business
    }

    return render(request, "rest/business.html", context)