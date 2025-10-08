var socket = io();
var interval = null;
var startBtn = document.getElementById('start');

function deleteExisting() {
  let remoteFeed = document.getElementById('remote-feed');
  while (remoteFeed.firstChild) {
    remoteFeed.removeChild(remoteFeed.firstChild);
  }
  document.querySelectorAll('video').forEach(video => {
    if (video.srcObject) {
      video.srcObject.getTracks().forEach(track => track.stop());
    }
    video.remove();
  });
};

startBtn.addEventListener('click', function() {
  if (startBtn.dataset.state === 'transmitting') {
    if (interval) {
      clearInterval(interval);
      interval = null;
    }
    startBtn.textContent = 'Start';
    startBtn.dataset.state = 'stopped';
    socket.emit('stop_feed');
    deleteExisting()
    return;
  }

  let facingMode = "user";
  let constraints = {
    audio: false,
    video: {
      facingMode: facingMode,
      width: { min: 720, ideal: 1280 }, height: { min: 720, ideal: 1280 },
      frameRate: {min: 15, ideal: 20}
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
      console.log(`Starting video at resolution: ${video.videoWidth}x${video.videoHeight}px`);
      console.log(`Starting video at frame rate: ${frameRate}fps`);
      console.log(`Actual camera frame rate: ${video.srcObject.getVideoTracks()[0].getSettings().frameRate}fps`);
      console.log(`Sending a frame every: ${1000 /frameRate}ms`);
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      interval = setInterval(function() {
        if (video) {
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