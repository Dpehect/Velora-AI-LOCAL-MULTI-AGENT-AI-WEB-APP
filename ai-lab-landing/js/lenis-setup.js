/**
 * Lenis — ultra smooth scroll
 */

export function initLenis() {
  if (typeof Lenis === "undefined") {
    console.warn("[AI Lab] Lenis not loaded");
    return null;
  }

  const lenis = new Lenis({
    duration: 1.35,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    orientation: "vertical",
    gestureOrientation: "vertical",
    smoothWheel: true,
    touchMultiplier: 1.4,
    wheelMultiplier: 0.95,
    autoRaf: false, // GSAP ticker drives raf in main.js
  });

  // Anchor links via Lenis
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      const id = anchor.getAttribute("href");
      if (!id || id === "#") return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      lenis.scrollTo(target, {
        offset: -72,
        duration: 1.4,
      });
    });
  });

  return lenis;
}
