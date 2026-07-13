/**
 * tsParticles — very light ambient dots (Apple-quiet density)
 */

export async function initParticles() {
  const el = document.getElementById("particles-bg");
  if (!el || typeof tsParticles === "undefined") return;

  try {
    await tsParticles.load({
      id: "particles-bg",
      options: {
        fullScreen: { enable: false },
        fpsLimit: 48,
        detectRetina: true,
        background: { color: { value: "transparent" } },
        particles: {
          number: {
            value: 28,
            density: { enable: true, width: 1200, height: 800 },
          },
          color: {
            value: ["#6366F1", "#A5B4FC", "#C7D2FE"],
          },
          opacity: {
            value: { min: 0.08, max: 0.22 },
            animation: {
              enable: true,
              speed: 0.25,
              sync: false,
              startValue: "random",
            },
          },
          size: {
            value: { min: 1, max: 2.4 },
          },
          move: {
            enable: true,
            speed: 0.18,
            direction: "none",
            random: true,
            straight: false,
            outModes: { default: "out" },
          },
          links: {
            enable: true,
            distance: 140,
            color: "#C7D2FE",
            opacity: 0.08,
            width: 0.6,
          },
        },
        interactivity: {
          detectsOn: "window",
          events: {
            onHover: { enable: true, mode: "repulse" },
            resize: { enable: true },
          },
          modes: {
            repulse: {
              distance: 80,
              duration: 0.6,
              factor: 0.4,
              speed: 0.4,
            },
          },
        },
        pauseOnBlur: true,
        pauseOnOutsideViewport: true,
      },
    });
  } catch (err) {
    console.warn("[AI Lab] particles init failed", err);
  }
}
