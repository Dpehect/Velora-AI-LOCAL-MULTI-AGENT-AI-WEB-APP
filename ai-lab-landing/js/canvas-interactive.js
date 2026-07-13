/**
 * Interactive canvas — soft indigo light trail following the pointer.
 * Quiet, premium, no neon overload. Quadratic curves for silk motion.
 */

export function initTrailCanvas(reduced = false) {
  const canvas = document.getElementById("trail-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d", { alpha: true });
  if (!ctx) return;

  let width = 0;
  let height = 0;
  let dpr = Math.min(window.devicePixelRatio || 1, 2);
  let raf = 0;
  let running = true;

  const pointer = { x: null, y: null, active: false };
  /** @type {{x:number,y:number,life:number,max:number,r:number,vx:number,vy:number}[]} */
  const sparks = [];
  /** @type {{x:number,y:number}[]} */
  const trail = [];
  const TRAIL_MAX = 36;

  const INDIGO = { r: 99, g: 102, b: 241 };

  function resize() {
    const rect = canvas.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function addSpark(x, y, burst = false) {
    const n = burst ? 14 : 2;
    for (let i = 0; i < n; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = burst ? 0.4 + Math.random() * 1.6 : 0.1 + Math.random() * 0.4;
      sparks.push({
        x: x + (Math.random() - 0.5) * (burst ? 16 : 5),
        y: y + (Math.random() - 0.5) * (burst ? 16 : 5),
        life: 1,
        max: burst ? 0.85 + Math.random() * 0.45 : 0.5 + Math.random() * 0.3,
        r: burst ? 1.1 + Math.random() * 2.4 : 0.7 + Math.random() * 1.1,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
      });
    }
  }

  function onPointer(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    pointer.x = clientX - rect.left;
    pointer.y = clientY - rect.top;
    pointer.active = true;

    trail.push({ x: pointer.x, y: pointer.y });
    if (trail.length > TRAIL_MAX) trail.shift();
    if (!reduced) addSpark(pointer.x, pointer.y, false);
  }

  function onLeave() {
    pointer.active = false;
  }

  function onClick(e) {
    if (reduced) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    addSpark(x, y, true);
  }

  function drawAmbient() {
    ctx.save();
    ctx.globalAlpha = 0.035;
    for (let i = 0; i < 20; i++) {
      const x = (Math.sin(i * 12.3 + 1.1) * 0.5 + 0.5) * width;
      const y = (Math.cos(i * 7.1 + 0.4) * 0.5 + 0.5) * height;
      ctx.beginPath();
      ctx.fillStyle = `rgb(${INDIGO.r},${INDIGO.g},${INDIGO.b})`;
      ctx.arc(x, y, 1.15, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  function drawTrail() {
    if (trail.length < 2) return;

    ctx.save();
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    // Soft outer glow path
    ctx.beginPath();
    ctx.moveTo(trail[0].x, trail[0].y);
    for (let i = 1; i < trail.length - 1; i++) {
      const midX = (trail[i].x + trail[i + 1].x) / 2;
      const midY = (trail[i].y + trail[i + 1].y) / 2;
      ctx.quadraticCurveTo(trail[i].x, trail[i].y, midX, midY);
    }
    const last = trail[trail.length - 1];
    ctx.lineTo(last.x, last.y);
    ctx.strokeStyle = `rgba(${INDIGO.r},${INDIGO.g},${INDIGO.b},0.08)`;
    ctx.lineWidth = 14;
    ctx.stroke();

    // Main silk stroke segments
    for (let i = 1; i < trail.length; i++) {
      const p0 = trail[i - 1];
      const p1 = trail[i];
      const t = i / trail.length;
      const alpha = t * 0.38;
      const w = 1.2 + t * 5.5;

      ctx.beginPath();
      ctx.strokeStyle = `rgba(${INDIGO.r},${INDIGO.g},${INDIGO.b},${alpha})`;
      ctx.lineWidth = w;
      ctx.moveTo(p0.x, p0.y);
      ctx.lineTo(p1.x, p1.y);
      ctx.stroke();
    }

    // Soft radial glow at tip
    if (pointer.active && pointer.x != null) {
      const g = ctx.createRadialGradient(
        pointer.x,
        pointer.y,
        0,
        pointer.x,
        pointer.y,
        56
      );
      g.addColorStop(0, `rgba(${INDIGO.r},${INDIGO.g},${INDIGO.b},0.18)`);
      g.addColorStop(0.4, `rgba(${INDIGO.r},${INDIGO.g},${INDIGO.b},0.06)`);
      g.addColorStop(1, "rgba(99,102,241,0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(pointer.x, pointer.y, 56, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
  }

  function drawSparks() {
    for (let i = sparks.length - 1; i >= 0; i--) {
      const s = sparks[i];
      s.life -= 0.014;
      s.x += s.vx;
      s.y += s.vy;
      s.vx *= 0.97;
      s.vy *= 0.97;
      if (s.life <= 0) {
        sparks.splice(i, 1);
        continue;
      }
      const a = (s.life / s.max) * 0.42;
      ctx.beginPath();
      ctx.fillStyle = `rgba(${INDIGO.r},${INDIGO.g},${INDIGO.b},${a})`;
      ctx.arc(s.x, s.y, s.r * (s.life / s.max + 0.28), 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function frame() {
    if (!running) return;
    ctx.clearRect(0, 0, width, height);
    drawAmbient();

    // Idle trail decay
    if (!pointer.active && trail.length) {
      if (Math.random() > 0.35) trail.shift();
    }

    drawTrail();
    drawSparks();
    raf = requestAnimationFrame(frame);
  }

  // Pause when offscreen
  const io = new IntersectionObserver(
    (entries) => {
      const visible = entries[0]?.isIntersecting;
      if (visible && !running) {
        running = true;
        raf = requestAnimationFrame(frame);
      } else if (!visible && running) {
        running = false;
        cancelAnimationFrame(raf);
      }
    },
    { threshold: 0.05 }
  );
  io.observe(canvas);

  resize();
  window.addEventListener("resize", resize);

  canvas.addEventListener("pointermove", onPointer);
  canvas.addEventListener("pointerenter", onPointer);
  canvas.addEventListener("pointerleave", onLeave);
  canvas.addEventListener("pointerdown", onClick);
  canvas.addEventListener(
    "touchmove",
    (e) => {
      e.preventDefault();
      onPointer(e);
    },
    { passive: false }
  );

  // Seed center so empty state has presence
  pointer.x = width / 2;
  pointer.y = height / 2;
  trail.push({ x: pointer.x, y: pointer.y });

  running = true;
  raf = requestAnimationFrame(frame);
}
