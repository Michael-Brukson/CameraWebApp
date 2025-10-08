var socket = io();

var interval = null;
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
    startBtn.textContent = 'Start';
    startBtn.dataset.state = 'stopped';
    socket.emit('stop_feed');
    return;
  }

  let facingMode = "user";
  let constraints = {
    audio: false,
    video: {
      facingMode: facingMode,
      width: { min: 1280 }, height: { min: 720 },
      frameRate: {min: 15, ideal: 30}
    }
  };

  let frameRate = constraints.video.frameRate.ideal || constraints.video.frameRate.min

  navigator.mediaDevices.getUserMedia(constraints).then(function success(stream) {
    let video = document.createElement('video');
    video.setAttribute('playsinline', '');
    video.setAttribute('autoplay', '');
    video.setAttribute('muted', '');
    document.body.appendChild(video);
    video.srcObject = stream;
    activeVideo = video;

    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    document.getElementById('remote-feed').appendChild(canvas);
    canvas.style.display = 'none';

    video.onloadedmetadata = function() {
      console.log(`Video resolution: ${video.videoWidth}x${video.videoHeight}px`);
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      interval = setInterval(function() {
        if (video) {
          console.log(video.frameRate)
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          let dataURL = canvas.toDataURL('image/jpeg', quality=0.95);
          socket.emit('video_frame', { image: dataURL, frameRate: frameRate });
        }
      }, 1000 / frameRate); // ~20fps
  
      startBtn.textContent = 'Stop';
      startBtn.dataset.state = 'transmitting';
    };
  });
});