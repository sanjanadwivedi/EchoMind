import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { speechRecognizer } from "../utils/speechRecognition";

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [micSupported, setMicSupported] = useState(false);

  useEffect(() => {
    setMicSupported(speechRecognizer.isSupported());
  }, []);

  function handleSubmit(e) {
    if (e) e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;

    if (isRecording) {
      speechRecognizer.stop();
      setIsRecording(false);
    }

    onSend(trimmed);
    setValue("");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }

  function toggleMic() {
    if (isRecording) {
      speechRecognizer.stop();
      setIsRecording(false);
    } else {
      setIsRecording(true);
      speechRecognizer.start(
        (transcript) => {
          setValue(transcript);
        },
        (err) => {
          console.error("Mic error:", err);
          setIsRecording(false);
        },
        () => {
          setIsRecording(false);
        }
      );
    }
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <div className={`chat-input__wrapper ${isRecording ? "chat-input__wrapper--recording" : ""}`}>
        <textarea
          className="chat-input__field"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            disabled
              ? "Waiting for response..."
              : isRecording
                ? "🎙️ Listening... speak now..."
                : "Type your message or click mic to speak..."
          }
          disabled={disabled}
          rows={1}
        />

        {/* Microphone Speech-To-Text Button */}
        {micSupported && (
          <motion.button
            type="button"
            className={`chat-input__mic ${isRecording ? "chat-input__mic--active" : ""}`}
            onClick={toggleMic}
            disabled={disabled}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title={isRecording ? "Stop Listening" : "Speak into Microphone"}
          >
            {isRecording ? "🔴" : "🎙️"}
          </motion.button>
        )}

        {/* Send Button */}
        <motion.button
          className="chat-input__send"
          type="submit"
          disabled={disabled || !value.trim()}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </motion.button>
      </div>
    </form>
  );
}
