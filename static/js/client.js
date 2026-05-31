var socket = io();
var interval = null;
var inFlight = false;
var inFlightTimeout = null;

const ACK_TIMEOUT_MS = 500;
const JPEG_QUALITY = 0.65;

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
  inFlight = false;
  if (inFlightTimeout) {
    clearTimeout(inFlightTimeout);
    inFlightTimeout = null;
  }
};

// TODO: add filters, that'd be funny
function startCam(){
  let facingMode = "user";
  let constraints = {
    audio: false,
    video: {
      facingMode: facingMode,
      width: { ideal: 1280 }, height: { ideal: 720 },
      frameRate: {min: 24, ideal: 60}
    }
  };

  navigator.mediaDevices.getUserMedia(constraints).then(function success(stream) {
    let video = document.createElement('video');
    const attributes = {
      'playsinline': 'active',
      'autoplay': 'active',
      'muted': 'active',
      'flipped': 'active'
    };
    
    let frameRate = stream.getVideoTracks()[0].getSettings().frameRate;

    Object.keys(attributes).forEach(key => {video.setAttribute(key, attributes[key])});
    document.body.appendChild(video);
    video.srcObject = stream;
    activeVideo = video;

    let [canvas, ctx] = createCanvas();

    video.onloadedmetadata = function() {
      console.log(`Starting video at resolution: ${video.videoWidth}x${video.videoHeight}px`);
      console.log(`Starting video at frame rate: ${frameRate}fps`);
      console.log(`Sending a frame every: ${1000 / frameRate}ms`);
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      interval = setInterval(function() {
        if (video) {
          if (inFlight || video.readyState < 2) {
            return;
          }

          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          let dataURL = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
          inFlight = true;

          inFlightTimeout = setTimeout(function() {
            inFlight = false;
            inFlightTimeout = null;
          }, ACK_TIMEOUT_MS);

          let options = {"showFPS": showFps.checked};

          send_frame(dataURL, frameRate, options);
        }
      }, 1000 / frameRate); // ~20fps
    };
  });
}


startBtn.addEventListener('click', function() {
  if (startBtn.dataset.state === 'transmitting') {
    if (interval) {
      clearInterval(interval);
      interval = null;
    }
    inFlight = false;
    if (inFlightTimeout) {
      clearTimeout(inFlightTimeout);
      inFlightTimeout = null;
    }
    startBtn.textContent = 'Start';
    startBtn.dataset.state = 'stopped';
    setTimeout(() => {}, 300);
    socket.emit('stop_feed');
    deleteExisting();
  } else {
    startCam();
    startBtn.textContent = 'Stop';
    startBtn.dataset.state = 'transmitting';
  }
});


function createCanvas(){
  let canvas = document.createElement('canvas');
  let ctx = canvas.getContext('2d');
  document.getElementById('remote-feed').appendChild(canvas);
  canvas.style.display = 'none';

  return [canvas, ctx];
}

function send_frame(image, frameRate, options){
  socket.emit('video_frame', { image: image, frameRate: frameRate, options: options}, function() {
    inFlight = false;
    if (inFlightTimeout) {
      clearTimeout(inFlightTimeout);
      inFlightTimeout = null;
    };
  });
}