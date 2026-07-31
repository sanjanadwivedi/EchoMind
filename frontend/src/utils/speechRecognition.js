class SpeechRecognitionEngine {
  constructor() {
    this.recognition = null;
    this.isListening = false;

    if (typeof window !== "undefined") {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = "en-US";
      }
    }
  }

  isSupported() {
    return !!this.recognition;
  }

  start(onResult, onError, onEnd) {
    if (!this.recognition || this.isListening) return;

    this.isListening = true;

    this.recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      if (onResult) {
        onResult(transcript);
      }
    };

    this.recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      this.isListening = false;
      if (onError) onError(event.error);
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (onEnd) onEnd();
    };

    try {
      this.recognition.start();
    } catch (e) {
      console.error("Failed to start speech recognition:", e);
      this.isListening = false;
    }
  }

  stop() {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
      } catch (e) {
        console.error("Error stopping speech recognition:", e);
      }
      this.isListening = false;
    }
  }
}

export const speechRecognizer = new SpeechRecognitionEngine();
