async function getAudioFingerprint(): Promise<string> {
  const AudioContext = window.OfflineAudioContext || (window as any).webkitOfflineAudioContext;
  if (!AudioContext) return "not_supported";

  try {
      const context = new AudioContext(1, 44100, 44100);
      const oscillator = context.createOscillator();
      oscillator.type = 'triangle';
      oscillator.frequency.value = 10000;

      const compressor = context.createDynamicsCompressor();
      compressor.threshold.value = -50;
      compressor.knee.value = 40;
      compressor.ratio.value = 12;
      compressor.attack.value = 0;
      compressor.release.value = 0.25;

      oscillator.connect(compressor);
      compressor.connect(context.destination);
      oscillator.start(0);

      const buffer = await context.startRendering();
      const signal = buffer.getChannelData(0).subarray(4500, 5000);

      let hash = 0;
      for (let i = 0; i < signal.length; i++) {
          hash = (hash << 5) - hash + Math.floor(signal[i] * 100000);
          hash |= 0;
      }

      return hash.toString();
  } catch (e) {
      return "error";
  }
}
