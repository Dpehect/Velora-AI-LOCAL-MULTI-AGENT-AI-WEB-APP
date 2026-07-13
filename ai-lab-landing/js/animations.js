/**
 * GSAP animations — navbar, hero, reveals, steps, magnetic, mobile menu
 * Slow, elegant, premium timing.
 */

const gsap = () => window.gsap;
const ST = () => window.ScrollTrigger;

/* ---------- Navbar: shrink + stronger blur on scroll ---------- */
export function initNavbar(lenis = null) {
  const nav = document.getElementById("navbar");
  if (!nav) return;

  const apply = (y) => {
    nav.classList.toggle("is-scrolled", y > 20);
  };

  apply(window.scrollY || document.documentElement.scrollTop);

  // Lenis-aware scroll source when available
  if (lenis && typeof lenis.on === "function") {
    lenis.on("scroll", ({ scroll }) => apply(scroll));
  } else {
    window.addEventListener(
      "scroll",
      () => apply(window.scrollY || document.documentElement.scrollTop),
      { passive: true }
    );
  }

  // GSAP fine-tune: slight height feel via padding class is CSS-driven
  if (gsap() && ST()) {
    ST().create({
      start: 0,
      end: 240,
      onUpdate: (self) => apply(self.scroll()),
    });
  }
}

/* ---------- Mobile menu ---------- */
export function initMobileMenu(lenis = null) {
  const toggle = document.getElementById("menu-toggle");
  const menu = document.getElementById("mobile-menu");
  const iconOpen = document.getElementById("icon-open");
  const iconClose = document.getElementById("icon-close");
  if (!toggle || !menu) return;

  let open = false;

  const setOpen = (next) => {
    open = next;
    menu.classList.toggle("hidden", !open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    if (iconOpen) iconOpen.classList.toggle("hidden", open);
    if (iconClose) iconClose.classList.toggle("hidden", !open);

    if (gsap() && open) {
      gsap().fromTo(
        menu.querySelectorAll(".mobile-link"),
        { opacity: 0, y: 10 },
        {
          opacity: 1,
          y: 0,
          duration: 0.45,
          stagger: 0.05,
          ease: "power3.out",
        }
      );
    }
  };

  toggle.addEventListener("click", () => setOpen(!open));

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setOpen(false));
  });

  // Close on resize to desktop
  window.addEventListener("resize", () => {
    if (window.innerWidth >= 768 && open) setOpen(false);
  });
}

/* ---------- Hero: elegant staggered entrance ---------- */
export function initHero(reduced = false) {
  const g = gsap();
  if (!g) return;

  if (reduced) {
    g.set(
      [".hero-eyebrow", ".hero-line-inner", ".hero-sub", ".hero-cta", ".hero-scroll"],
      { opacity: 1, y: 0, filter: "none" }
    );
    return;
  }

  const tl = g.timeline({
    defaults: { ease: "power3.out" },
  });

  tl.fromTo(
    ".hero-eyebrow",
    { opacity: 0, y: 18, filter: "blur(8px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.2 },
    0.2
  )
    .fromTo(
      ".hero-line-inner",
      { opacity: 0, y: 56 },
      {
        opacity: 1,
        y: 0,
        duration: 1.25,
        stagger: 0.16,
        ease: "power4.out",
      },
      0.35
    )
    .fromTo(
      ".hero-sub",
      { opacity: 0, y: 24 },
      { opacity: 1, y: 0, duration: 1.1 },
      0.85
    )
    .fromTo(
      ".hero-cta",
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 1.0 },
      1.05
    )
    .fromTo(
      ".hero-scroll",
      { opacity: 0 },
      { opacity: 1, duration: 1.0 },
      1.35
    );

  // Soft scroll-indicator pulse
  g.to(".scroll-line", {
    scaleY: 0.4,
    transformOrigin: "top",
    duration: 1.5,
    ease: "sine.inOut",
    yoyo: true,
    repeat: -1,
  });

  // Gentle hero glow breathing
  g.to(".hero-glow", {
    opacity: 0.7,
    scale: 1.06,
    duration: 4.5,
    ease: "sine.inOut",
    yoyo: true,
    repeat: -1,
  });
}

/* ---------- Generic section reveals ---------- */
export function initReveals(reduced = false) {
  const g = gsap();
  if (!g || !ST()) return;

  const els = document.querySelectorAll(".reveal-up");
  if (!els.length) return;

  if (reduced) {
    g.set(els, { opacity: 1, y: 0 });
    g.set(".feature-card", { opacity: 1, y: 0 });
    return;
  }

  els.forEach((el) => {
    g.fromTo(
      el,
      { opacity: 0, y: 40 },
      {
        opacity: 1,
        y: 0,
        duration: 1.15,
        ease: "power3.out",
        scrollTrigger: {
          trigger: el,
          start: "top 88%",
          toggleActions: "play none none none",
        },
      }
    );
  });

  // Feature cards cascade
  const cards = document.querySelectorAll(".feature-card");
  if (cards.length) {
    g.fromTo(
      cards,
      { opacity: 0, y: 48 },
      {
        opacity: 1,
        y: 0,
        duration: 1.1,
        stagger: 0.12,
        ease: "power3.out",
        scrollTrigger: {
          trigger: "#features",
          start: "top 70%",
          toggleActions: "play none none none",
        },
      }
    );
  }
}

/* ---------- How it works: alternating side entrances + line ---------- */
export function initSteps(reduced = false) {
  const g = gsap();
  if (!g || !ST()) return;

  const steps = document.querySelectorAll(".step-item");
  const progress = document.getElementById("timeline-progress");

  if (reduced) {
    g.set(steps, { opacity: 1, x: 0 });
    if (progress) g.set(progress, { height: "100%" });
    return;
  }

  steps.forEach((step) => {
    const fromLeft = step.classList.contains("step-left");

    g.fromTo(
      step,
      {
        opacity: 0,
        x: fromLeft ? -56 : 56,
      },
      {
        opacity: 1,
        x: 0,
        duration: 1.2,
        ease: "power3.out",
        scrollTrigger: {
          trigger: step,
          start: "top 82%",
          toggleActions: "play none none none",
        },
      }
    );

    const num = step.querySelector(".step-num");
    if (num) {
      g.fromTo(
        num,
        { scale: 0.82, opacity: 0.35 },
        {
          scale: 1,
          opacity: 1,
          duration: 0.75,
          ease: "power2.out",
          scrollTrigger: {
            trigger: step,
            start: "top 82%",
            toggleActions: "play none none none",
          },
        }
      );
    }

    // Thin horizontal connector line animation (desktop)
    const content = step.querySelector(".step-content");
    if (content && window.matchMedia("(min-width: 640px)").matches) {
      g.fromTo(
        content,
        { opacity: 0.6 },
        {
          opacity: 1,
          duration: 1,
          ease: "power2.out",
          scrollTrigger: {
            trigger: step,
            start: "top 82%",
            toggleActions: "play none none none",
          },
        }
      );
    }
  });

  // Timeline draw on scroll
  if (progress) {
    g.fromTo(
      progress,
      { height: "0%" },
      {
        height: "100%",
        ease: "none",
        scrollTrigger: {
          trigger: "#how",
          start: "top 55%",
          end: "bottom 65%",
          scrub: 0.85,
        },
      }
    );
  }
}

/* ---------- Magnetic hover (buttons + cards) ---------- */
export function initMagnetic(reduced = false) {
  const g = gsap();
  if (!g || reduced) return;

  // Only on fine pointer devices
  if (window.matchMedia && !window.matchMedia("(pointer: fine)").matches) {
    // Simple CSS-like lift still via mouseenter for touch-hybrid
  }

  // Buttons — magnetic pull
  document.querySelectorAll(".magnetic-btn").forEach((btn) => {
    const text = btn.querySelector(".magnetic-text") || btn;

    const move = (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      g.to(btn, {
        x: x * 0.26,
        y: y * 0.26,
        duration: 0.6,
        ease: "power3.out",
      });
      g.to(text, {
        x: x * 0.12,
        y: y * 0.12,
        duration: 0.6,
        ease: "power3.out",
      });
    };

    const leave = () => {
      g.to(btn, { x: 0, y: 0, duration: 0.85, ease: "elastic.out(1, 0.42)" });
      g.to(text, { x: 0, y: 0, duration: 0.85, ease: "elastic.out(1, 0.42)" });
    };

    btn.addEventListener("mousemove", move);
    btn.addEventListener("mouseleave", leave);
  });

  // Feature cards — lift + subtle magnetic / tilt
  document.querySelectorAll(".magnetic-card").forEach((card) => {
    const speed = parseFloat(card.dataset.speed || "0.7");

    const enter = () => {
      card.classList.add("is-hovered");
      g.to(card, {
        y: -12,
        scale: 1.015,
        duration: 0.6,
        ease: "power3.out",
      });
    };

    const move = (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      g.to(card, {
        x: x * 0.035 * speed,
        y: -12 + y * 0.028 * speed,
        rotateX: (-y / rect.height) * 3.5,
        rotateY: (x / rect.width) * 3.5,
        transformPerspective: 1000,
        duration: 0.55,
        ease: "power2.out",
      });
    };

    const leave = () => {
      card.classList.remove("is-hovered");
      g.to(card, {
        x: 0,
        y: 0,
        scale: 1,
        rotateX: 0,
        rotateY: 0,
        duration: 0.8,
        ease: "power3.out",
      });
    };

    card.addEventListener("mouseenter", enter);
    card.addEventListener("mousemove", move);
    card.addEventListener("mouseleave", leave);
  });
}
