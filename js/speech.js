// Audio uses the browser's own speech engine, and only when it offers a Khmer
// (km / km-KH) voice. Most desktop browsers have none, so the speaker buttons
// simply stay hidden there. No recorded or downloaded audio is used.
let khmerVoice = null;
let listeners = [];

function pick() {
  if (!('speechSynthesis' in window)) return;
  const voices = window.speechSynthesis.getVoices() || [];
  const v = voices.find((x) => /^km(-|_|$)/i.test(x.lang)) || null;
  if (v !== khmerVoice) {
    khmerVoice = v;
    listeners.forEach((fn) => fn(!!v));
  }
}

export function initSpeech() {
  try {
    if (!('speechSynthesis' in window)) return;
    pick();
    window.speechSynthesis.addEventListener?.('voiceschanged', pick);
  } catch { khmerVoice = null; }
}

export const canSpeak = () => !!khmerVoice;
export const onVoiceChange = (fn) => { listeners.push(fn); };

export function speak(text) {
  if (!khmerVoice) return;
  try {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.voice = khmerVoice;
    u.lang = khmerVoice.lang;
    u.rate = 0.85;
    window.speechSynthesis.speak(u);
  } catch { /* ignore */ }
}
