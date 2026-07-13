/**
 * AI Lab Landing — Lenis + GSAP + tsParticles + Canvas
 * Premium, quiet motion. No 3D.
 */

import { initLenis } from "./lenis-setup.js";
import { initParticles } from "./particles.js";
import { initNavbar, initHero, initReveals, initSteps, initMagnetic } from "./animations.js";
import { initTrailCanvas } from "./canvas-interactive.js";

function ready(fn) {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fn, { once: true });
  } else {
    fn();
  }
}

ready(async () => {
  const reduced =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Smooth scroll (skip heavy smoothing if user prefers reduced motion)
  const lenis = reduced ? null : initLenis();

  // GSAP plugins
  if (window.gsap && window.ScrollTrigger) {
    window.gsap.registerPlugin(window.ScrollTrigger);
    if (lenis) {
      // Keep ScrollTrigger in sync with Lenis
      lenis.on("scroll", window.ScrollTrigger.update);
      window.gsap.ticker.add((time) => {
        lenis.raf(time * 1000);
      });
      window.gsap.ticker.lagSmoothing(0);
    }
  }

  // Ambient background
  await initParticles();

  // Motion systems
  initNavbar();
  initHero(reduced);
  initReveals(reduced);
  initSteps(reduced);
  initMagnetic(reduced);
  initTrailCanvas(reduced);

  // Soft refresh after layout settles
  requestAnimationFrame(() => {
    if (window.ScrollTrigger) window.ScrollTrigger.refresh();
  });
});
