import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

export default function AudioVisualizer({ isActive, type = "npc" }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animationId;
    let step = 0;

    const numBars = 16;
    const barWidth = 3;
    const gap = 3;

    function render() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      step += 0.15;

      const gradient = ctx.createLinearGradient(0, canvas.height, 0, 0);
      if (type === "mic") {
        gradient.addColorStop(0, "#ef4444");
        gradient.addColorStop(1, "#f59e0b");
      } else {
        gradient.addColorStop(0, "#7c3aed");
        gradient.addColorStop(1, "#fbbf24");
      }

      ctx.fillStyle = gradient;

      for (let i = 0; i < numBars; i++) {
        const height = isActive
          ? Math.sin(step + i * 0.4) * 12 + Math.cos(step * 0.7 + i) * 6 + 18
          : 4;

        const x = i * (barWidth + gap) + 4;
        const y = canvas.height - height;

        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, height, 2);
        ctx.fill();
      }

      animationId = requestAnimationFrame(render);
    }

    render();

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [isActive, type]);

  return (
    <motion.div
      className="audio-visualizer"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <canvas ref={canvasRef} width={100} height={36} />
      <span className="audio-visualizer__label">
        {type === "mic" ? "LISTENING..." : "VOICE ACTIVE"}
      </span>
    </motion.div>
  );
}
