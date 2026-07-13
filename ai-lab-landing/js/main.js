/**
 * Velora AI Lab Landing
 * Lenis + GSAP + ScrollTrigger + tsParticles + Canvas
 * Quiet, premium motion — no 3D.
 */

import { initLenis } from "./lenis-setup.js";
import { initParticles } from "./particles.js";
import {
  initNavbar,
  initHero,
  initReveals,
  initSteps,
  initMagnetic,
  initMobileMenu,
} from "./animations.js";
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

  // Smooth scroll
  const lenis = reduced ? null : initLenis();

  // GSAP + Lenis ticker sync
  if (window.gsap && window.ScrollTrigger) {
    window.gsap.registerPlugin(window.ScrollTrigger);

    if (lenis) {
      lenis.on("scroll", window.ScrollTrigger.update);
      window.gsap.ticker.add((time) => {
        lenis.raf(time * 1000);
      });
      window.gsap.ticker.lagSmoothing(0);
    }
  }

  // Ambient particles
  await initParticles();

  // UI systems
  initNavbar(lenis);
  initMobileMenu(lenis);
  initHero(reduced);
  initReveals(reduced);
  initSteps(reduced);
  initMagnetic(reduced);
  initTrailCanvas(reduced);

  // Layout settle → refresh triggers
  requestAnimationFrame(() => {
    if (window.ScrollTrigger) window.ScrollTrigger.refresh();
  });
});
