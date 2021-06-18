const RECORDING_STATE_IDLE = 0;
const RECORDING_STATE_WAITING = 1;
const RECORDING_STATE_RECORDING = 2;
const RECORDING_STATE_UPLOADING = 3;
const RECORDING_STATE_DONE = 4;

let recording_state = RECORDING_STATE_IDLE;
/** @type {MediaStream} */
let mic_media_stream;
/** @type {MediaStream} */
let dest_media_stream;
/** @type {AnalyserNode} */
let analyser;
/** @type {Float32Array} */
let analyser_data;
let recorder;
let recording_start_time;

/** @type {Blob} */
let recorded_blob;
/** @type {string} */
let recorded_blob_url;

const audio_ctx = new AudioContext();
const worklet_load_promise = (async () => {
	let text = await (await fetch('/static/js/voice_announce_worklet.js')).text();
	await audio_ctx.audioWorklet.addModule('data:text/javascript;base64,' + btoa(text));
})();

function set_recording_state(state) {
	let prev = recording_state;
	if(recording_state == state) return;
	recording_state = state;
	let elem = document.getElementById("va-button-record");
	elem.classList.remove("is-warning", "is-success");
	if(state == RECORDING_STATE_IDLE) {
		if(prev == RECORDING_STATE_RECORDING || prev == RECORDING_STATE_UPLOADING) elem.textContent = "Re-record";
		else elem.textContent = "Record";
	} else if(state == RECORDING_STATE_WAITING) {
		elem.textContent = "Waiting for permission...";
		elem.classList.add("is-warning");
	} else if(state == RECORDING_STATE_RECORDING) {
		elem.textContent = "Stop Recording";
		elem.classList.add("is-success");
	}
	for(let item of document.getElementsByClassName("va-record-show")) {
		if(state == RECORDING_STATE_RECORDING) {
			item.classList.remove("is-hidden");
		} else {
			item.classList.add("is-hidden");
		}
	}
	let upload_button = document.getElementById("va-button-announce");
	upload_button.classList.remove("is-warning");
	upload_button.classList.remove("is-success");
	if(state == RECORDING_STATE_UPLOADING) {
		elem.classList.add("is-hidden");
		upload_button.classList.add("is-warning");
		upload_button.textContent = "Uploading...";
	} else if(state == RECORDING_STATE_DONE) {
		elem.classList.add("is-hidden");
		upload_button.classList.add("is-success");
		upload_button.textContent = "Upload successful!";
	} else {
		elem.classList.remove("is-hidden");
		upload_button.textContent = "Confirm Announcement"
	}
}

let speaker_setups = [
	[0, 0, 0.7], // delay, pan, gain
	[0.1, -0.6, 0.25],
	[0.2, 0.9, 0.18],
	[0.4, 0.3, 0.03]
];

/**
 * 
 * @param {AudioNode} output 
 * @param {AudioNode} input 
 */
function apply_effects(output, input) {
	if(enable_robot_voice) {
		let worklet = new AudioWorkletNode(audio_ctx, 'voice-announce-processor', {processorOptions: {is_ai: true, sample_rate: audio_ctx.sampleRate}});
		input.connect(worklet);
		input = worklet;
	}
	analyser = audio_ctx.createAnalyser();
	analyser.connect(output);
	analyser_data = new Float32Array(analyser.frequencyBinCount);
	output = analyser;
	//input.connect(analyser);

	for(let [delay, pan, gain] of speaker_setups) {
		let curr = input;

		if(delay) {
			let delay_node = audio_ctx.createDelay(delay);
			delay_node.delayTime.value = delay;
			curr.connect(delay_node);
			curr = delay_node;
		}

		if(pan) {
			let pan_node = audio_ctx.createStereoPanner();
			pan_node.pan.value = pan;
			curr.connect(pan_node);
			curr = pan_node;
		}

		if(gain) {
			let gain_node = audio_ctx.createGain();
			gain_node.gain.value = gain;
			curr.connect(gain_node);
			curr = gain_node;
		}
		curr.connect(output);
	}
}

function update_level() {
	analyser.getFloatTimeDomainData(analyser_data);
	/** @type {HTMLProgressElement} */
	let bar = document.getElementById("va-level");
	let max_abs = 0;
	for(let i = 0; i < analyser_data.length; i++) {
		max_abs = Math.max(max_abs, Math.abs(analyser_data[i]));
	}
	bar.value = 100 * max_abs;
	if(recording_state == RECORDING_STATE_RECORDING) {
		document.getElementById("va-time").textContent = (Math.floor(audio_ctx.currentTime - recording_start_time)) + " / 30";
		if((audio_ctx.currentTime - recording_start_time) >= 30) {
			stop_recording();
		}
	}
	requestAnimationFrame(update_level);
}

async function setup_media_stream() {
	if(dest_media_stream) return;
	
	await audio_ctx.resume();
	await worklet_load_promise;
	mic_media_stream = await navigator.mediaDevices.getUserMedia({audio: true});
	let stream_node = audio_ctx.createMediaStreamSource(mic_media_stream);
	let dest_node = audio_ctx.createMediaStreamDestination();
	dest_media_stream = dest_node.stream;
	apply_effects(dest_node, stream_node);
	update_level();
}

async function stop_recording() {
	set_recording_state(RECORDING_STATE_IDLE);
	recorded_blob = await new Promise((resolve, reject) => {
		recorder.ondataavailable = (e) => {resolve(e.data);};
		recorder.onerror = reject;
		recorder.stop();
	});
	for(let track of mic_media_stream.getAudioTracks()) track.enabled = false;
	recorded_blob_url = URL.createObjectURL(recorded_blob);
	document.getElementById("va-button-announce").classList.remove("is-hidden");
	document.getElementById("va-preview").classList.remove("is-hidden");
	document.getElementById("va-preview").src = recorded_blob_url;
}

async function record_button() {
	if(recording_state == RECORDING_STATE_IDLE) {
		if(recorded_blob) {
			recorded_blob = null;
			URL.revokeObjectURL(recorded_blob_url);
			recorded_blob_url = null;
			document.getElementById("va-button-announce").classList.add("is-hidden");
			document.getElementById("va-preview").classList.add("is-hidden");
			document.getElementById("va-preview").pause();
		}
		set_recording_state(RECORDING_STATE_WAITING);
		try {
			await setup_media_stream();
			for(let track of mic_media_stream.getAudioTracks()) track.enabled = true;
			set_recording_state(RECORDING_STATE_RECORDING);
			recorder = new MediaRecorder(dest_media_stream, {audioBitsPerSecond: 20000});
			recorder.start();
			recording_start_time = audio_ctx.currentTime;
		} catch(e) {
			console.error(e);
			set_recording_state(RECORDING_STATE_IDLE);
		}
	} else if(recording_state == RECORDING_STATE_RECORDING) {
		await stop_recording();
	}
}

async function upload_button() {
	if(recording_state == RECORDING_STATE_IDLE && recorded_blob) {
		set_recording_state(RECORDING_STATE_UPLOADING);
		let url = location.origin + location.pathname + "/upload";
		try {
			let res = await fetch(url, {
				method: 'POST',
				cache: 'no-cache',
				body: recorded_blob,
				headers: {
					'Content-Type': recorded_blob.type
				},
				mode: 'same-origin'
			});
			if(res.status == 204) {
				set_recording_state(RECORDING_STATE_DONE);
				for(let track of mic_media_stream.getAudioTracks()) track.stop();
			} else {
				set_recording_state(RECORDING_STATE_IDLE);
			}
		} catch(e) {
			set_recording_state(RECORDING_STATE_IDLE);
		}
	}
}
/*
window.addEventListener("DOMContentLoaded", () => {
	document.getElementById("va-button-record").addEventListener("click", record_button);
	document.getElementById("va-button-announce").addEventListener("click", upload_button);
});*/

document.addEventListener("visibilitychange", () => {
	let url = location.origin + location.pathname + "/cancel";
	if(recording_state != RECORDING_STATE_DONE && document.visibilityState == 'hidden') {
		navigator.sendBeacon(url)
	}
}) 
