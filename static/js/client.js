export default class WakeLockManager {
    #wakeLock = null;

    constructor(){}

    async requestWakeLock() {
        if (!('wakeLock' in navigator)) {
            return;
        }

        try {
            const currentWakeLock = await navigator.wakeLock.request('screen');
            this.#wakeLock = currentWakeLock;
            console.log(this.#wakeLock);

            currentWakeLock.addEventListener('release', () => {
                if (this.#wakeLock === currentWakeLock) {
                    this.#wakeLock = null;
                }
            });
        } catch (error) {
            console.warn('Unable to acquire screen wake lock:', error);
            this.#wakeLock = null;
        }
    }

    async releaseWakeLock() {
        if (!this.#wakeLock) {
            return;
        }

        try {
            await this.#wakeLock.release();
        } catch (error) {
            console.warn('Unable to release screen wake lock:', error);
        } finally {
            this.#wakeLock = null;
        }
    }

    getWakeLockStatus(){
        return this.#wakeLock;
    }
}

var socket = io();
var interval = null;
var inFlight = false;
var inFlightTimeout = null;
var wkm = new WakeLockManager();

const ACK_TIMEOUT_MS = 1000;
const JPEG_QUALITY = 0.65;


document.addEventListener('visibilitychange', function() {
  if (document.visibilityState === 'visible' && inFlight && !wkm.getWakeLockStatus) {
    wkm.requestWakeLock();
  }
});

async function getBattery() {
  if ('getBattery' in navigator) {
    try {
      const battery = await navigator.getBattery();
      const percentage = Math.ceil(battery.level * 100);
      return percentage;
    } catch (error) {
      console.error("Failed to access battery data:", error);
    }
  } else {
    console.log("Battery Status API is not supported by this browser.");
  }
}


async function getOptions(){
  var battery = null;
  if (showBattery.checked){
    battery = await getBattery();
  }

  return {'showFPS': showFPS.checked, 'battery': battery};
}

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

    let [canvas, ctx] = createCanvas();

    video.onloadedmetadata = function() {
      console.log(`Starting video at resolution: ${video.videoWidth}x${video.videoHeight}px`);
      console.log(`Starting video at frame rate: ${frameRate}fps`);
      console.log(`Sending a frame every: ${1000 / frameRate}ms`);
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      interval = setInterval(async function() {
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

          let options = await getOptions();

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
    wkm.releaseWakeLock();
    deleteExisting();
  } else {
    wkm.requestWakeLock();
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