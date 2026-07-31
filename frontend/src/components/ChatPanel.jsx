import { useRef, useEffect, useState } from "react";
import { AnimatePresence } from "framer-motion";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import ChatInput from "./ChatInput";
import ParticleEffect from "./ParticleEffect";
import AnimatedAvatar from "./AnimatedAvatar";
import EmotionBadge from "./EmotionBadge";
import MemoryBankDrawer from "./MemoryBankDrawer";
import AudioVisualizer from "./AudioVisualizer";
import StarterPrompts from "./StarterPrompts";
import { speechEngine } from "../utils/speech";
import { soundEffects } from "../utils/soundEffects";

const npcBanners = {
  Eldon: "/banners/eldon.png",
  Ragnar: "/banners/ragnar.png",
  Luna: "/banners/luna.png",
};

export default function ChatPanel({
  npc,
  messages,
  currentEmotion,
  isLoading,
  onSend,
  playerId,
}) {
  const scrollRef = useRef(null);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [sfxEnabled, setSfxEnabled] = useState(true);
  const [isMemoryBankOpen, setIsMemoryBankOpen] = useState(false);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  function handleToggleVoice() {
    const newState = speechEngine.toggle();
    setVoiceEnabled(newState);
  }

  function handleToggleSfx() {
    const newState = soundEffects.toggle();
    setSfxEnabled(newState);
  }

  if (!npc) {
    return (
      <div className="chat-panel chat-panel--empty">
        <ParticleEffect />
        <div className="chat-panel__welcome">
          <div className="chat-panel__welcome-icon">🧠</div>
          <h2>Welcome to EchoMind</h2>
          <p>Select an NPC from the sidebar to start a conversation.</p>
          <p className="chat-panel__welcome-hint">
            NPCs will remember everything you tell them.
          </p>
        </div>
      </div>
    );
  }

  const banner = npcBanners[npc.name];
  const emotionClass = `emotion-glow--${(currentEmotion || "neutral").toLowerCase()}`;

  return (
    <div className={`chat-panel ${emotionClass}`}>
      <ParticleEffect />

      {/* Hero Character Stage Header */}
      <div className="chat-panel__header">
        {banner && (
          <div className="chat-panel__header-banner">
            <img src={banner} alt="" className="chat-panel__header-banner-img" />
            <div className="chat-panel__header-banner-overlay" />
          </div>
        )}

        <div className="chat-panel__header-content">
          <div className="chat-panel__header-left">
            <AnimatedAvatar
              name={npc.name}
              role={npc.role}
              size="md"
              isActive={true}
              isSpeaking={isLoading}
            />

            <div className="chat-panel__header-identity">
              <div className="chat-panel__name-line">
                <h2 className="chat-panel__npc-name">{npc.name}</h2>
                <EmotionBadge emotion={currentEmotion} />
              </div>
              <div className="chat-panel__sub-line">
                <span className="chat-panel__npc-role">{npc.role}</span>
                <span className="chat-panel__dot-sep">•</span>
                <span className="chat-panel__npc-loc">📍 {npc.location}</span>
                <span className="chat-panel__status-pill">
                  <span className="chat-panel__status-dot" />
                  MEMORY ACTIVE
                </span>
              </div>
            </div>
          </div>

          <div className="chat-panel__header-right">
            <AudioVisualizer isActive={isLoading} type="npc" />

            <div className="chat-panel__audio-controls">
              <button
                className="audio-btn memory-bank-btn"
                onClick={() => setIsMemoryBankOpen(true)}
                title="Inspect AI Memory Bank"
              >
                🧠 Memory Bank
              </button>

              <button
                className={`audio-btn ${voiceEnabled ? "audio-btn--active" : ""}`}
                onClick={handleToggleVoice}
                title={voiceEnabled ? "Mute Voice" : "Enable Voice"}
              >
                {voiceEnabled ? "🗣️ Voice" : "🔇 Voice"}
              </button>

              <button
                className={`audio-btn ${sfxEnabled ? "audio-btn--active" : ""}`}
                onClick={handleToggleSfx}
                title={sfxEnabled ? "Mute SFX" : "Enable SFX"}
              >
                {sfxEnabled ? "🎵 SFX" : "🔇 SFX"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Memory Bank Drawer Modal */}
      <MemoryBankDrawer
        npc={npc}
        playerId={playerId}
        isOpen={isMemoryBankOpen}
        onClose={() => setIsMemoryBankOpen(false)}
      />

      {/* Messages Area */}
      <div className="chat-panel__messages" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="chat-panel__start">
            <div className="chat-panel__start-card">
              <div className="chat-panel__start-icon">✨</div>
              <h3>Converse with <span>{npc.name}</span></h3>
              <p className="chat-panel__start-hint">
                Tell them a secret, state a preference, or ask a question.
                Their emotion & long-term memories evolve dynamically in real time!
              </p>
            </div>
          </div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <MessageBubble
              key={`${msg.timestamp}-${i}`}
              message={msg}
              npcName={npc.name}
            />
          ))}
        </AnimatePresence>

        <AnimatePresence>
          {isLoading && <TypingIndicator npcName={npc.name} />}
        </AnimatePresence>
      </div>

      {/* Starter Prompt Suggestions */}
      <StarterPrompts
        npcName={npc.name}
        onSelectPrompt={onSend}
        disabled={isLoading}
      />

      {/* Input */}
      <ChatInput onSend={onSend} disabled={isLoading} />
    </div>
  );

}
