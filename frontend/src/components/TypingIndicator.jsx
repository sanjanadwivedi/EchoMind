import { motion } from "framer-motion";
import AnimatedAvatar from "./AnimatedAvatar";

export default function TypingIndicator({ npcName }) {
  return (
    <motion.div
      className="typing-indicator"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
    >
      <AnimatedAvatar name={npcName} size="sm" isSpeaking={true} />

      <div className="typing-indicator__body">
        <span className="typing-indicator__name">{npcName}</span>
        <div className="typing-indicator__dots">
          <span className="typing-indicator__dot" />
          <span className="typing-indicator__dot" />
          <span className="typing-indicator__dot" />
        </div>
      </div>
    </motion.div>
  );
}
