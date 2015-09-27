from firebase import firebase
from socketIO_client import SocketIO, LoggingNamespace
from threading import Timer
import googlemaps
import json
import time
import requests

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
    socketIO.emit('queue-1', {"origin":
                                  {"lat": lat1,
                                   "lng": lon1},
                              "destination":
                                  {"lat": lat2,
                                   "lng": lon2}}
    )
    res = gmaps.directions({"lat": lat1, "lng": lon1}, {"lat": lat2, "lng": lon2}, mode="driving")
    return float(res[0]['legs'][-1]['duration']['value']/60.0)


def check_and_book_cabs(user):

    if check_booking_status(user):
        print "Already booked"
        return

    data = json.loads(check_cabs(user))
    ola_eta = data['categories'][0]['eta']
    cus_eta = get_arrival_time(user)
    socketIO.emit('queue-2', {"customer_eta": cus_eta,
                          "ola_eta": ola_eta})
    print cus_eta, ola_eta
    if ola_eta - 12 < cus_eta < ola_eta + 12:
        book_cab(user)
        print "Booked cab"
    return


def dummy_data(long1, lat1):
    socketIO.emit('queue-1', {"origin":
                                  {"lat": lat1,
                                   "lng": long1},
                              "destination":
                                  {"lat": 12.9505322,
                                   "lng": 77.6420946}}
    )
    #socketIO.emit('queue-2', {"customer_eta": 10.983333333333333, "ola_eta": 2})
    data = json.loads(check_cabs(user))
    ola_eta = data['categories'][0]['eta']
    cus_eta = get_arrival_time(user)
    socketIO.emit('queue-2', {"customer_eta": cus_eta,
                              "ola_eta": ola_eta})



def start():
    check_and_book_cabs(user)
    #dummy_data()
    Timer(600, start()).start()


def test_script():
    #long = [77.5800795, 77.6026597, 77.6200672, 77.6240583, 77.6341273]
    #lat = [12.9484623, 12.9365709, 12.9288251, 12.9356402, 12.9389393]
    long = [77.5800795, 77.6341273]
    lat = [12.9484623, 12.9389393]

    i = 0
    while(True):
        time.sleep(5)
        dummy_data(long[i % 2], lat[i % 2])
        i = i + 1
        requests.post("https://pacific-thicket-7228.herokuapp.com/location?latitude=" +
                      str(lat[i % 2]) + "&longitude=" + str(long[i % 2]))


with SocketIO('http://logbase-socketio.herokuapp.com', 80, LoggingNamespace) as socketIO:
    print "Hello"
#start()
test_script()


