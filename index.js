var express = require('express');
var app = express();
var bodyParser = require('body-parser');

app.get('/', function (req, res) {
  res.send('Hello World!');
});

app.post('/', function(req, res) {
   var data = req.body;
   console.log(data);
});

var server = app.listen(3000, function () {
  var port = process.env.PORT || process.env.STICK_API_PORT || 3000;

  console.log('Pickup app listening at %s', port);
});
