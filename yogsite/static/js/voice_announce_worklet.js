const BUFFER_SIZE = 65536;
class VoiceAnnounceProcessor extends AudioWorkletProcessor {
	constructor(options) {
		super();
		let is_ai = options.processorOptions.is_ai;
		let sample_rate = options.processorOptions.sample_rate;

		this.sample_rate = sample_rate;
		let [delay, frequency] = is_ai ? [0.005, 3] : [0.0001, 0.1];
		this.delay_samples = Math.round(delay * sample_rate);
		this.period_samples = Math.round(sample_rate / frequency);
		console.log(this.delay_samples + " samples delay, " + this.period_samples + " samples period");
		/**
		 * @type {Float32Array[][]}
		 */
		this.frame_buffer = [];
		this.frame_buffer_pointer = 0;
		this.clock = 0;
	}

	/**
	 * 
	 * @param {Float32Array[][]} inputs 
	 * @param {Float32Array[][]} outputs 
	 * @param {*} parameters 
	 */
	process(inputs, outputs, parameters) {
		// audio processing code here.

		if(!inputs.length || !inputs[0].length) return;

		let samples_per_frame = inputs[0][0].length;

		let multiplier = 1 / this.period_samples * Math.PI * 2;

		for(let k = 0; k < inputs.length && k < outputs.length; k++) {
			if(!this.frame_buffer[k]) this.frame_buffer[k] = [];
			for(let j = 0; j < inputs[k].length && j < outputs[k].length; j++) {
				if(!this.frame_buffer[k][j]) this.frame_buffer[k][j] = new Float32Array(BUFFER_SIZE);
				let next_pointer = this.frame_buffer_pointer;
				
				let buffer = this.frame_buffer[k][j];
				let output_channel = outputs[k][j];
				let input_channel = inputs[k][j];
				for(let i = 0; i < input_channel.length; i++) {
					buffer[next_pointer] = input_channel[i];
					next_pointer = (next_pointer + 1) & (BUFFER_SIZE-1);
					output_channel[i] = 0;
				}
				for(let delay_type = 0; delay_type < 2; delay_type++) {
					let base_delay = this.delay_samples;
					for(let i = 0; i < input_channel.length; i++) {
						let delay = base_delay;
						if(delay_type == 1) {
							delay += Math.round(Math.sin((this.clock + i) * multiplier) * this.delay_samples);
						}
						output_channel[i] += buffer[(this.frame_buffer_pointer + i - delay) & (BUFFER_SIZE-1)] * 0.5;
					}
				}
			}
		}
		this.frame_buffer_pointer = (this.frame_buffer_pointer + samples_per_frame) & (BUFFER_SIZE-1);
		this.clock += samples_per_frame;
		if(this.clock > this.period_samples) this.clock -= this.period_samples;
		return true;
	}
}
  
registerProcessor('voice-announce-processor', VoiceAnnounceProcessor);