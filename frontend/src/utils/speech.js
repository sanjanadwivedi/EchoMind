class SpeechEngine {
  constructor() {
    this.enabled = true;
    this.synth = typeof window !== "undefined" ? window.speechSynthesis : null;
    this.voices = [];

    if (this.synth) {
      this.loadVoices();
      if (this.synth.onvoiceschanged !== undefined) {
        this.synth.onvoiceschanged = () => this.loadVoices();
      }
    }
  }

  loadVoices() {
    if (this.synth) {
      this.voices = this.synth.getVoices();
    }
  }

  getVoiceForNPC(npcName) {
    if (!this.voices || this.voices.length === 0) {
      this.loadVoices();
    }

    const EnglishVoices = this.voices.filter((v) => v.lang.startsWith("en"));
    const pool = EnglishVoices.length > 0 ? EnglishVoices : this.voices;

    if (npcName === "Ragnar") {
      // Prefer male / deep voices
      return pool.find((v) => v.name.includes("Male") || v.name.includes("David") || v.name.includes("Daniel")) || pool[0];
    } else if (npcName === "Luna") {
      // Prefer female / articulate voices
      return pool.find((v) => v.name.includes("Female") || v.name.includes("Zira") || v.name.includes("Samantha")) || pool[1] || pool[0];
    } else {
      // Eldon
      return pool.find((v) => v.name.includes("George") || v.name.includes("James")) || pool[2] || pool[0];
    }
  }

  speak(text, npcName = "Eldon") {
    if (!this.enabled || !this.synth) return;

    // Stop previous speech
    this.synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    const voice = this.getVoiceForNPC(npcName);

    if (voice) {
      utterance.voice = voice;
    }

    // NPC voice pitch & rate adjustments
    if (npcName === "Ragnar") {
      utterance.pitch = 0.8;
      utterance.rate = 0.95;
    } else if (npcName === "Luna") {
      utterance.pitch = 1.15;
      utterance.rate = 1.0;
    } else {
      // Eldon
      utterance.pitch = 0.9;
      utterance.rate = 0.95;
    }

    this.synth.speak(utterance);
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
    }
  }

  toggle() {
    this.enabled = !this.enabled;
    if (!this.enabled) {
      this.stop();
    }
    return this.enabled;
  }
}

export const speechEngine = new SpeechEngine();
