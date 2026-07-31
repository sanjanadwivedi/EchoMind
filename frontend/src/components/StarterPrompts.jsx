import { motion } from "framer-motion";

const promptSuggestions = {
  Eldon: [
    "☕ My cat is named Luna and I love drinking espresso.",
    "❓ Do you remember what my pet's name is?",
    "📜 Tell me about the Ancient Library of Oakhaven.",
    "🛡️ How do you feel about Ragnar the Blacksmith?",
  ],
  Ragnar: [
    "⚒️ I prefer heavy armor forged from star-iron.",
    "🍺 Pour me a dark ale and tell me a war story.",
    "❓ What was my preference for weapons?",
    "🔥 Have you forged anything interesting lately?",
  ],
  Luna: [
    "🌿 I spent years studying herbalism in the Silverwood.",
    "❓ Do you recall where I learned alchemy?",
    "🔮 What secrets do the stars reveal tonight?",
    "🐾 Have you seen any rare creatures in the forest?",
  ],
};

export default function StarterPrompts({ npcName, onSelectPrompt, disabled }) {
  const prompts = promptSuggestions[npcName] || promptSuggestions.Eldon;

  return (
    <div className="starter-prompts">
      <span className="starter-prompts__label">Suggested Prompts:</span>
      <div className="starter-prompts__list">
        {prompts.map((promptText, idx) => (
          <motion.button
            key={idx}
            type="button"
            className="starter-prompt-pill"
            onClick={() => onSelectPrompt(promptText)}
            disabled={disabled}
            whileHover={{ scale: 1.03, y: -2 }}
            whileTap={{ scale: 0.97 }}
          >
            {promptText}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
