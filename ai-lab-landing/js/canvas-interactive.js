/**
 * Interactive canvas — soft light trail following the pointer.
 * Quiet, premium, no neon overload.
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
  /** @type {{x:number,y:number,life:number,max:number,r:number}[]} */
  const sparks = [];
  /** @type {{x:number,y:number}[]} */
  const trail = [];
  const TRAIL_MAX = 28;

  // Soft indigo palette
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
    const n = burst ? 10 : 2;
    for (let i = 0; i < n; i++) {
      sparks.push({
        x: x + (Math.random() - 0.5) * (burst ? 18 : 6),
        y: y + (Math.random() - 0.5) * (burst ? 18 : 6),
        life: 1,
        max: burst ? 0.9 + Math.random() * 0.4 : 0.55 + Math.random() * 0.25,
        r: burst ? 1.2 + Math.random() * 2.2 : 0.8 + Math.random() * 1.2,
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
    // soft vignette dots — static quiet field
    ctx.save();
    ctx.globalAlpha = 0.04;
    for (let i = 0; i < 18; i++) {
      const x = (Math.sin(i * 12.3) * 0.5 + 0.5) * width;
      const y = (Math.cos(i * 7.1) * 0.5 + 0.5) * height;
      ctx.beginPath();
      ctx.fillStyle = `rgb(${INDIGO.r},${INDIGO.g},${INDIGO.b})`;
      ctx.arc(x, y, 1.2, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  function drawTrail() {
    if (trail.length < 2) return;

    ctx.save();
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    for (let i = 1; i < trail.length; i++) {
      const p0 = trail[i - 1];
      const p1 = trail[i];
      const t = i / trail.length;
      const alpha = t * 0.35;
      const w = 1 + t * 6;

      ctx.beginPath();
      ctx.strokeStyle = `rgba(${INDIGO.r},${INDIGO.g},${INDIGO.b},${alpha})`;
      ctx.lineWidth = w;
      ctx.moveTo(p0.x, p0.y);
      ctx.lineTo(p1.x, p1.y);
      ctx.stroke();
    }

    // soft glow at tip
    if (pointer.active && pointer.x != null) {
      const g = ctx.createRadialGradient(
        pointer.x,
        pointer.y,
        0,
        pointer.x,
        pointer.y,
        48
      );
      g.addColorStop(0, `rgba(${INDIGO.r},${INDIGO.g},${INDIGO.b},0.16)`);
      g.addColorStop(0.45, `rgba(${INDIGO.r},${INDIGO.g},${INDIGO.b},0.05)`);
      g.addColorStop(1, "rgba(99,102,241,0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(pointer.x, pointer.y, 48, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
  }

  function drawSparks() {
    for (let i = sparks.length - 1; i >= 0; i--) {
      const s = sparks[i];
      s.life -= 0.016;
      if (s.life <= 0) {
        sparks.splice(i, 1);
        continue;
      }
      const a = (s.life / s.max) * 0.45;
      ctx.beginPath();
      ctx.fillStyle = `rgba(${INDIGO.r},${INDIGO.g},${INDIGO.b},${a})`;
      ctx.arc(s.x, s.y, s.r * (s.life / s.max + 0.3), 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function frame() {
    if (!running) return;
    // gentle fade for silk trail
    ctx.clearRect(0, 0, width, height);
    drawAmbient();

    // slowly decay trail when idle
    if (!pointer.active && trail.length) {
      if (Math.random() > 0.4) trail.shift();
    }

    drawTrail();
    drawSparks();
    raf = requestAnimationFrame(frame);
  }

  // Observe visibility — pause when offscreen
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

  // Center seed glow so empty state isn't blank
  pointer.x = width / 2;
  pointer.y = height / 2;
  trail.push({ x: pointer.x, y: pointer.y });

  running = true;
  raf = requestAnimationFrame(frame);
}
