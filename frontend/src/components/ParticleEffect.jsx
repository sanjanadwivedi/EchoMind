import { useEffect, useRef } from "react";

export default function ParticleEffect() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let animId;
    let particles = [];
    let mouse = { x: -1000, y: -1000, radius: 150 };

    function resize() {
      canvas.width = canvas.parentElement.offsetWidth;
      canvas.height = canvas.parentElement.offsetHeight;
    }

    function handleMouseMove(e) {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    }

    function handleMouseLeave() {
      mouse.x = -1000;
      mouse.y = -1000;
    }

    function createParticle() {
      return {
        x: Math.random() * (canvas.width || 800),
        y: Math.random() * (canvas.height || 600),
        size: Math.random() * 2.5 + 0.8,
        speedX: (Math.random() - 0.5) * 0.4,
        speedY: (Math.random() - 0.5) * 0.4 - 0.1, // slight upward float
        opacity: Math.random() * 0.6 + 0.2,
        maxOpacity: Math.random() * 0.7 + 0.3,
        hue: Math.random() > 0.4 ? (Math.random() > 0.5 ? 270 : 220) : 42, // purple, blue, gold
        pulseSpeed: Math.random() * 0.03 + 0.01,
      };
    }

    function init() {
      resize();
      particles = Array.from({ length: 60 }, createParticle);
    }

    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw subtle ambient glow near mouse
      if (mouse.x > 0 && mouse.y > 0) {
        const gradient = ctx.createRadialGradient(
          mouse.x,
          mouse.y,
          0,
          mouse.x,
          mouse.y,
          mouse.radius
        );
        gradient.addColorStop(0, "rgba(124, 58, 237, 0.12)");
        gradient.addColorStop(0.5, "rgba(245, 158, 11, 0.05)");
        gradient.addColorStop(1, "rgba(0, 0, 0, 0)");
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      for (const p of particles) {
        p.x += p.speedX;
        p.y += p.speedY;

        // Mouse attraction/repulsion interaction
        const dx = mouse.x - p.x;
        const dy = mouse.y - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          const force = (mouse.radius - dist) / mouse.radius;
          p.x -= (dx / dist) * force * 1.5;
          p.y -= (dy / dist) * force * 1.5;
        }

        // Screen wrap
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        // Glowing spark pulse
        p.opacity += p.pulseSpeed;
        if (p.opacity > p.maxOpacity || p.opacity < 0.1) {
          p.pulseSpeed = -p.pulseSpeed;
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${p.hue}, 85%, 70%, ${Math.max(0, p.opacity)})`;
        ctx.shadowColor = `hsla(${p.hue}, 90%, 60%, 0.8)`;
        ctx.shadowBlur = p.size * 4;
        ctx.fill();
      }

      animId = requestAnimationFrame(animate);
    }

    init();
    animate();

    const parent = canvas.parentElement;
    parent.addEventListener("mousemove", handleMouseMove);
    parent.addEventListener("mouseleave", handleMouseLeave);
    window.addEventListener("resize", resize);

    return () => {
      cancelAnimationFrame(animId);
      parent.removeEventListener("mousemove", handleMouseMove);
      parent.removeEventListener("mouseleave", handleMouseLeave);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="particle-canvas"
      aria-hidden="true"
    />
  );
}
