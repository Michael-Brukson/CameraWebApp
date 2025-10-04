var socket = io();

socket.on('show_user', function(data) {
  var remoteFeedDiv = document.getElementById('remote-feed');
  var remoteCanvas = remoteFeedDiv.querySelector('canvas');

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
  var canvasId = 'remote-feed-canvas-' + sid;
  var remoteCanvas = document.getElementById(canvasId);
  if (remoteCanvas) {
    remoteCanvas.remove();
  }
});

var interval = null;
var activeStream = null;
var activeVideo = null;
var activeCanvas = null;

var startBtn = document.getElementById('start');

startBtn.addEventListener('click', function() {
  if (startBtn.dataset.state === 'transmitting') {
    if (interval) {
      clearInterval(interval);
      interval = null;
    }
    if (activeStream) {
      activeStream.getTracks().forEach(track => track.stop());
      activeStream = null;
    }
    if (activeVideo) {
      activeVideo.remove();
      activeVideo = null;
    }
    if (activeCanvas) {
      activeCanvas.remove();
      activeCanvas = null;
    }
    startBtn.textContent = 'Start';
    startBtn.dataset.state = 'stopped';
    socket.emit('disconnect');
    return;
  }

  var facingMode = "user";
  var constraints = {
    audio: false,
    video: {
      facingMode: facingMode,
      width: { min: 1280 }, height: { min: 720 }
    }
  };

  navigator.mediaDevices.getUserMedia(constraints).then(function success(stream) {
    activeStream = stream;
    var video = document.createElement('video');
    video.setAttribute('playsinline', '');
    video.setAttribute('autoplay', '');
    video.setAttribute('muted', '');
    video.style.display = 'none';
    document.body.appendChild(video);
    video.srcObject = stream;
    activeVideo = video;

    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    document.getElementById('remote-feed').appendChild(canvas);
    activeCanvas = canvas;

    video.onloadedmetadata = function() {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      interval = setInterval(function() {
        if (canvas.width && canvas.height) {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          var dataURL = canvas.toDataURL('image/jpeg');
          socket.emit('video_frame', { image: dataURL });
        }
      }, 50); // ~20fps
  
      startBtn.textContent = 'Stop';
      startBtn.dataset.state = 'transmitting';
    };
  });
});