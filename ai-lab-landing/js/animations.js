/**
 * GSAP animations — navbar, hero, reveals, steps, magnetic
 */

const gsap = () => window.gsap;
const ST = () => window.ScrollTrigger;

/* ---------- Navbar: shrink + stronger blur on scroll ---------- */
export function initNavbar() {
  const nav = document.getElementById("navbar");
  if (!nav) return;

  const onScroll = () => {
    const y = window.scrollY || document.documentElement.scrollTop;
    nav.classList.toggle("is-scrolled", y > 24);
  };

  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Also listen via ScrollTrigger if available (Lenis-friendly)
  if (gsap() && ST()) {
    ST().create({
      start: 0,
      end: 200,
      onUpdate: (self) => {
        nav.classList.toggle("is-scrolled", self.scroll() > 24);
      },
    });
  }
}

/* ---------- Hero: elegant staggered entrance ---------- */
export function initHero(reduced = false) {
  const g = gsap();
  if (!g) return;

  if (reduced) {
    g.set(
      [".hero-eyebrow", ".hero-line-inner", ".hero-sub", ".hero-cta", ".hero-scroll"],
      { opacity: 1, y: 0 }
    );
    return;
  }

  const tl = g.timeline({
    defaults: { ease: "power3.out" },
  });

  tl.fromTo(
    ".hero-eyebrow",
    { opacity: 0, y: 16, filter: "blur(6px)" },
    { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.1 },
    0.15
  )
    .fromTo(
      ".hero-line-inner",
      { opacity: 0, y: 48 },
      {
        opacity: 1,
        y: 0,
        duration: 1.15,
        stagger: 0.14,
        ease: "power4.out",
      },
      0.28
    )
    .fromTo(
      ".hero-sub",
      { opacity: 0, y: 22 },
      { opacity: 1, y: 0, duration: 1.05 },
      0.72
    )
    .fromTo(
      ".hero-cta",
      { opacity: 0, y: 18 },
      { opacity: 1, y: 0, duration: 0.95 },
      0.95
    )
    .fromTo(
      ".hero-scroll",
      { opacity: 0 },
      { opacity: 1, duration: 0.9 },
      1.25
    );

  // Soft scroll-line pulse
  g.to(".scroll-line", {
    scaleY: 0.45,
    transformOrigin: "top",
    duration: 1.4,
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
    return;
  }

  els.forEach((el) => {
    g.fromTo(
      el,
      { opacity: 0, y: 36 },
      {
        opacity: 1,
        y: 0,
        duration: 1.05,
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
      { opacity: 0, y: 40 },
      {
        opacity: 1,
        y: 0,
        duration: 1,
        stagger: 0.1,
        ease: "power3.out",
        scrollTrigger: {
          trigger: "#features",
          start: "top 72%",
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
    const content =
      step.querySelector("div.pl-14, div.sm\\:pr-8, div.sm\\:pl-8") || step;

    g.fromTo(
      step,
      {
        opacity: 0,
        x: fromLeft ? -48 : 48,
      },
      {
        opacity: 1,
        x: 0,
        duration: 1.1,
        ease: "power3.out",
        scrollTrigger: {
          trigger: step,
          start: "top 82%",
          toggleActions: "play none none none",
        },
      }
    );

    // Number soft pop
    const num = step.querySelector(".step-num");
    if (num) {
      g.fromTo(
        num,
        { scale: 0.85, opacity: 0.4 },
        {
          scale: 1,
          opacity: 1,
          duration: 0.7,
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

  // Timeline draw on scroll through the section
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
          end: "bottom 70%",
          scrub: 0.8,
        },
      }
    );
  }
}

/* ---------- Magnetic hover (buttons + cards) ---------- */
export function initMagnetic(reduced = false) {
  const g = gsap();
  if (!g || reduced) return;

  // Buttons — stronger magnetic pull on label
  document.querySelectorAll(".magnetic-btn").forEach((btn) => {
    const text = btn.querySelector(".magnetic-text") || btn;
    const strength = 18;
    const textStrength = 10;

    const move = (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      g.to(btn, {
        x: x * 0.28,
        y: y * 0.28,
        duration: 0.55,
        ease: "power3.out",
      });
      g.to(text, {
        x: x * 0.14,
        y: y * 0.14,
        duration: 0.55,
        ease: "power3.out",
      });
    };

    const leave = () => {
      g.to(btn, { x: 0, y: 0, duration: 0.75, ease: "elastic.out(1, 0.45)" });
      g.to(text, { x: 0, y: 0, duration: 0.75, ease: "elastic.out(1, 0.45)" });
    };

    btn.addEventListener("mousemove", move);
    btn.addEventListener("mouseleave", leave);
  });

  // Feature cards — lift + subtle magnetic drift
  document.querySelectorAll(".magnetic-card").forEach((card) => {
    const speed = parseFloat(card.dataset.speed || "0.7");

    const enter = () => {
      card.classList.add("is-hovered");
      g.to(card, {
        y: -10,
        scale: 1.012,
        duration: 0.55,
        ease: "power3.out",
      });
    };

    const move = (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      g.to(card, {
        x: x * 0.04 * speed,
        y: -10 + y * 0.03 * speed,
        rotateX: (-y / rect.height) * 3,
        rotateY: (x / rect.width) * 3,
        transformPerspective: 900,
        duration: 0.5,
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
        duration: 0.7,
        ease: "power3.out",
      });
    };

    card.addEventListener("mouseenter", enter);
    card.addEventListener("mousemove", move);
    card.addEventListener("mouseleave", leave);
  });
}
