import { useState, useCallback } from "react";
import { sendMessage } from "../api/client";
import { soundEffects } from "../utils/soundEffects";
import { speechEngine } from "../utils/speech";

export function useChat() {
  // keyed by npcId: { [npcId]: [{role, content, emotion, timestamp}] }
  const [conversations, setConversations] = useState({});
  const [currentEmotions, setCurrentEmotions] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const getMessages = useCallback(
    (npcId) => conversations[npcId] || [],
    [conversations]
  );

  const getEmotion = useCallback(
    (npcId) => currentEmotions[npcId] || "Neutral",
    [currentEmotions]
  );

  const send = useCallback(async (npcId, playerId, message, npcName = "Eldon") => {
    setError(null);
    setIsLoading(true);

    // Audio SFX on send
    soundEffects.playSendSound();

    // Add player message immediately
    const playerMsg = {
      role: "player",
      content: message,
      timestamp: Date.now(),
    };

    setConversations((prev) => ({
      ...prev,
      [npcId]: [...(prev[npcId] || []), playerMsg],
    }));

    try {
      const data = await sendMessage(npcId, playerId, message);

      const emotion = data.emotion || "Neutral";

      const npcMsg = {
        role: "npc",
        content: data.response,
        emotion: emotion,
        timestamp: Date.now(),
      };

      setConversations((prev) => ({
        ...prev,
        [npcId]: [...(prev[npcId] || []), npcMsg],
      }));

      setCurrentEmotions((prev) => ({
        ...prev,
        [npcId]: emotion,
      }));

      // Audio SFX on receive
      soundEffects.playReceiveSound();

      // Trigger Text-to-Speech voice reading
      speechEngine.speak(data.response, npcName);

    } catch (err) {
      setError(err.message);

      // Add error message to chat
      const errMsg = {
        role: "error",
        content: err.message,
        timestamp: Date.now(),
      };

      setConversations((prev) => ({
        ...prev,
        [npcId]: [...(prev[npcId] || []), errMsg],
      }));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearChat = useCallback((npcId) => {
    setConversations((prev) => {
      const next = { ...prev };
      delete next[npcId];
      return next;
    });
  }, []);

  return { getMessages, getEmotion, send, isLoading, error, clearChat };
}
