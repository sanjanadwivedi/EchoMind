import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createNPC } from "../api/client";

export default function CreateCharacterModal({ isOpen, onClose, onCreated }) {
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [location, setLocation] = useState("");

  const [personality, setPersonality] = useState({
    warmth: 60,
    curiosity: 75,
    trust: 50,
    respect: 60,
    aggression: 15,
    loyalty: 70,
    fear: 10,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSliderChange = (trait, value) => {
    setPersonality((prev) => ({ ...prev, [trait]: parseInt(value, 10) }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !role.trim() || !location.trim()) {
      setError("Please fill out Name, Role, and Location.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const newNpc = await createNPC({
        name: name.trim(),
        role: role.trim(),
        location: location.trim(),
        personality,
      });

      // Reset form
      setName("");
      setRole("");
      setLocation("");
      onCreated(newNpc);
      onClose();
    } catch (err) {
      setError(err.message || "Failed to create character.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="modal-backdrop" onClick={onClose}>
        <motion.div
          className="modal-card"
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="modal-header">
            <h3>✨ Create New NPC</h3>
            <button className="modal-close" onClick={onClose}>
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="modal-form">
            {error && <div className="modal-error">{error}</div>}

            <div className="form-group">
              <label>Character Name</label>
              <input
                type="text"
                placeholder="e.g. Zephyr"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Role</label>
                <input
                  type="text"
                  placeholder="e.g. Alchemist"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  placeholder="e.g. Apothecary"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="personality-section">
              <h4>Personality Matrix (0 – 100)</h4>
              <div className="sliders-grid">
                {Object.entries(personality).map(([trait, value]) => (
                  <div key={trait} className="slider-group">
                    <div className="slider-header">
                      <span className="slider-label">{trait}</span>
                      <span className="slider-value">{value}</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={value}
                      onChange={(e) => handleSliderChange(trait, e.target.value)}
                      className="slider-input"
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Creating..." : "✨ Create Character"}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
