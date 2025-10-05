var socket = io();

var interval = null;
var activeStream = null;
var activeVideo = null;
var activeCanvas = null;

var startBtn = document.getElementById('start');

socket.on('stop_feed', function(data) {
  document.getElementById('remote-feed').removeChild(parent.firstChild);
});

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
    socket.emit('stop_feed');
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
    document.body.appendChild(video);
    video.srcObject = stream;
    activeVideo = video;

    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    document.getElementById('remote-feed').appendChild(canvas);
    canvas.style.display = 'none';

    video.onloadedmetadata = function() {
      console.log(`Video resolution: ${video.videoWidth}x${video.videoHeight}px`);
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      interval = setInterval(function() {
        if (video) {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          var dataURL = canvas.toDataURL('image/jpeg', quality=0.95);
          socket.emit('video_frame', { image: dataURL });
        }
      }, 50); // ~20fps
  
      startBtn.textContent = 'Stop';
      startBtn.dataset.state = 'transmitting';
    };
  });
});