var socket = io();

socket.emit('join_server');

socket.on('server_frame', function(data) {
  var sid = data.sid;
  var canvasId = 'remote-feed-' + sid;
  var remoteFeedDiv = document.getElementById('remote-feed');

  var remoteCanvas = remoteFeedDiv.querySelector('canvas');
  if (!remoteCanvas) {
    remoteCanvas = document.createElement('canvas');
    remoteCanvas.id = canvasId;
    remoteFeedDiv.appendChild(remoteCanvas);
  }

  var img = new window.Image();
  img.onload = function() {
    remoteCanvas.width = img.width;
    remoteCanvas.height = img.height;
    var ctx = remoteCanvas.getContext('2d');
    ctx.drawImage(img, 0, 0, img.width, img.height);
  };
  img.src = data.image;
});

socket.on('user_disconnected', function(data) {
  var sid = data.sid;
  var canvasId = 'remote-feed-' + sid;
  var remoteCanvas = document.getElementById(canvasId);
  if (remoteCanvas) {
    remoteCanvas.remove();
  }
});