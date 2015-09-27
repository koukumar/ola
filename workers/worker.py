from firebase import firebase
from threading import Timer
import requests
import googlemaps
import json

user = "Kousik"


def check_booking_status(user):
    fb = firebase.FirebaseApplication('https://intense-fire-8730.firebaseio.com', None)
    result = fb.get('/Account/' + user, None)

    if "NONE" in result['status']:
        return False

    if 'BOOKED' in result['status']:
        return True
    else:
        return False


def fetch_dest_location(user):
    fb = firebase.FirebaseApplication('https://intense-fire-8730.firebaseio.com', None)
    result = fb.get('/Account/' + user + '/location/', None)
    return result['lat'], result['long']


def fetch_current_location(user):
    fb = firebase.FirebaseApplication('https://intense-fire-8730.firebaseio.com', None)
    result = fb.get('/Account/' + user + '/location/', None)
    return result['cur_lat'], result['cur_long']


def update_booking_status(user, data):
    fb = firebase.FirebaseApplication('https://intense-fire-8730.firebaseio.com', None)
    fb.patch('Account/' + user + '/details', json.loads(data))
    fb.patch('/Account/' + user + '/', {"status": "BOOKED"})
    return


def book_cab(user):
    lat, lon = fetch_current_location(user)
    payload = {'pickup_lng': lon, 'pickup_lat': lat, 'category': 'sedan', 'pickup_mode': 'NOW'}
    url = 'http://sandbox-t.olacabs.com/v1/bookings/create'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer 7db75d3ac2874b038a73434c1219f607',
               'X-APP-TOKEN': '41644d0c94b44b00810c3552b8a1c997'}
    r = requests.get(url, headers=headers, params=payload)
    update_booking_status(user, r.content)
    return r.content


def check_cabs(user):
    lat, lon = fetch_current_location(user)
    payload = {'pickup_lng': lon, 'pickup_lat': lat, 'category': 'sedan'}
    url = 'http://sandbox-t.olacabs.com/v1/products'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer 7db75d3ac2874b038a73434c1219f607',
               'X-APP-TOKEN': '41644d0c94b44b00810c3552b8a1c997'}
    r = requests.get(url, headers=headers, params=payload)
    return r.content


def get_arrival_time(user):
    lat1, lon1 = fetch_dest_location(user)
    lat2, lon2 = fetch_current_location(user)
    gmaps = googlemaps.Client('AIzaSyB-G0uNuZ0IV0_akfI7sAf6ThRr9OEyU7U')
    res = gmaps.directions({"lat": lat2, "lng":lon2}, {"lat": lat1, "lng":lon1}, mode="driving")
    return float(res[0]['legs'][-1]['duration']['value']/60.0)


def check_and_book_cabs(user):

    if check_booking_status(user):
        print "Already booked"
        return

    data = json.loads(check_cabs(user))
    ola_eta = data['categories'][0]['eta']
    cus_eta = get_arrival_time(user)
    print cus_eta, ola_eta
    if ola_eta - 12 < cus_eta < ola_eta + 12:
        book_cab(user)
        print "Booked cab"
    return


def start():
    check_and_book_cabs(user)
    Timer(5, start()).start()

#print book_cab(user)
start()