navigator.mediaDevices.getUserMedia(constraints).then(function success(stream) {
  video.srcObject = stream;

  var socket = io();

  // canvas to capture frames
  var canvas = document.createElement('canvas');
  canvas.width = 500;
  canvas.height = 500;
  var ctx = canvas.getContext('2d');

  setInterval(function() {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    var dataURL = canvas.toDataURL('image/jpeg');
    socket.emit('video_frame', { image: dataURL });
  }, 100); // 100ms = (~10fps)

  socket.on('new_video_frame', function(data) {
    var img = document.getElementById('remote-feed');
    if (!img) {
      img = document.createElement('img');
      img.id = 'remote-feed';
      img.style.width = canvas.width + 'px';
      img.style.height = canvas.height + 'px';
      document.body.appendChild(img);
    }
    img.src = data.image;
  });
});