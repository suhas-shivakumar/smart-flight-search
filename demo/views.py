import json
import os
from amadeus import Client, ResponseError, Location
from django.shortcuts import render
from django.contrib import messages
from .flight import Flight
from django.http import HttpResponse, HttpRequest

def demo(request):
    origin = request.POST.get('Origin')
    destination = request.POST.get('Destination')
    departureDate = request.POST.get('Departuredate')
    returnDate = request.POST.get('Returndate')
    adults = request.POST.get('Adults')

    if not adults:
        adults = 1

    kwargs = {'originLocationCode': origin,
              'destinationLocationCode': destination,
              'departureDate': departureDate,
              'adults': adults
              }

    tripPurpose = ''
    if returnDate:
        kwargs['returnDate'] = returnDate
        try:
            trip_purpose_response = amadeus.travel.predictions.trip_purpose.get(**kwargs).data
            tripPurpose = trip_purpose_response['result']
        except ResponseError as error:
            messages.add_message(request, messages.ERROR, error)
            return render(request, 'demo/demo_form.html', {})

    if origin and destination and departureDate:
        try:
            flight_offers = amadeus.shopping.flight_offers_search.get(**kwargs)
            prediction_flights = amadeus.shopping.flight_offers.prediction.post(flight_offers.result)
        except ResponseError as error:
            messages.add_message(request, messages.ERROR, error)
            return render(request, 'demo/demo_form.html', {})
        flights_offers_returned = []
        for flight in flight_offers.data:
            offer = Flight(flight).construct_flights()
            flights_offers_returned.append(offer)

        prediction_flights_returned = []
        for flight in prediction_flights.data:
            offer = Flight(flight).construct_flights()
            prediction_flights_returned.append(offer)

        return render(request, 'demo/results.html', {'response': flights_offers_returned,
                                                     'prediction': prediction_flights_returned,
                                                     'origin': origin,
                                                     'destination': destination,
                                                     'departureDate': departureDate,
                                                     'returnDate': returnDate,
                                                     'tripPurpose': tripPurpose,
                                                     })
    return render(request, 'demo/demo_form.html', {})


def origin_airport_search(request):
    if is_ajax(request=request):
        try:
            data = amadeus.reference_data.locations.get(keyword=request.GET.get('term', None),
                                                        subType=Location.ANY).data
            return HttpResponse(get_city_airport_list(data), 'application/json')
        except ResponseError as error:
            messages.add_message(request, messages.ERROR, error)



def destination_airport_search(request):
    if is_ajax(request=request):
        try:
            data = amadeus.reference_data.locations.get(keyword=request.GET.get('term', None),
                                                        subType=Location.ANY).data
            return HttpResponse(get_city_airport_list(data), 'application/json')
        except ResponseError as error:
            messages.add_message(request, messages.ERROR, error)
    

def get_city_airport_list(data):
    result = []
    for i, val in enumerate(data):
        result.append(data[i]['iataCode'] + ', ' + data[i]['name'])
    result = list(dict.fromkeys(result))
    return json.dumps(result)

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def verify(request: HttpRequest) -> HttpResponse:
    client_id = request.GET.get("client_id", None)
    client_secret = request.GET.get("client_secret", None)

    if client_id is None or client_secret is None:
        messages.add_message(request, messages.ERROR, "")
        return render(request, 'demo/index.html', {})
    else:
        os.environ["AMADEUS_CLIENT_ID"] = client_id
        os.environ["AMADEUS_CLIENT_SECRET"] = client_secret
        global amadeus
        amadeus = Client()
        return demo(request)
