/**
 * tsParticles — very light ambient field (Apple-quiet density)
 * Soft indigo dots + faint links. Low count, low speed.
 */

export async function initParticles() {
  const el = document.getElementById("particles-bg");
  if (!el || typeof tsParticles === "undefined") return;

  try {
    await tsParticles.load({
      id: "particles-bg",
      options: {
        fullScreen: { enable: false },
        fpsLimit: 45,
        detectRetina: true,
        background: { color: { value: "transparent" } },
        particles: {
          number: {
            value: 24,
            density: { enable: true, width: 1400, height: 900 },
          },
          color: {
            value: ["#6366F1", "#A5B4FC", "#C7D2FE", "#E0E7FF"],
          },
          opacity: {
            value: { min: 0.06, max: 0.18 },
            animation: {
              enable: true,
              speed: 0.2,
              sync: false,
              startValue: "random",
            },
          },
          size: {
            value: { min: 0.8, max: 2.2 },
          },
          move: {
            enable: true,
            speed: 0.15,
            direction: "none",
            random: true,
            straight: false,
            outModes: { default: "out" },
          },
          links: {
            enable: true,
            distance: 130,
            color: "#C7D2FE",
            opacity: 0.07,
            width: 0.55,
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
              distance: 72,
              duration: 0.55,
              factor: 0.35,
              speed: 0.35,
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
