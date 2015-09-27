var express = require('express');
var http = require('http').Server(app);

var app = express();
var bodyParser = require('body-parser');
var Firebase = require("firebase");
var myFirebaseRef = new Firebase("https://intense-fire-8730.firebaseio.com/Account/Kousik/location");
var myFirebaseTripRef = new Firebase("https://intense-fire-8730.firebaseio.com/Account/Kousik/details");

var port = process.env.PORT || process.env.STICK_API_PORT || 2000;


app.get('/', function (req, res) {
  res.send('Hello World!');
});

app.post('/location', function(req, res) {
   var data = req.body;
   var params = req.params
   console.log(data, params, req.query);
   lat = parseFloat(req.query.latitude);
   long = parseFloat(req.query.longitude);
   myFirebaseRef.update({
	    cur_lat: lat,
	    cur_long: long,
    });
   res.send('You are tracked!!!');
});

app.get('/login', function(req, res) {
   var data = req.body;
   var params = req.params
   console.log(data, params, req.query);
   res.status(200).end();
});

app.get('/trip', function(req, res) {
   data = { "status" : "No Trips Available"};
   myFirebaseTripRef.on("value", function(snapshot) {
      console.log(snapshot.val());
      data = snapshot.val();
    }, function (errorObject) {
       console.log("The read failed: " + errorObject.code);
    });
    if (data != null) {
      res.send(data);
    } else {
      res.send({ "status" : "No Trips Available"});
    }
});

app.listen(port);
console.log('Pickup App listening on port 3000');
