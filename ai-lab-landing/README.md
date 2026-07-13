# Velora AI Lab — Landing Page

Apple Intelligence–inspired landing page: soft white canvas, generous whitespace, elegant type. Not cyberpunk or neon.

## Stack

| Tech | Role |
|------|------|
| **Lenis** | Ultra-smooth scroll |
| **GSAP + ScrollTrigger** | Hero stagger, reveals, timeline, magnetic hover |
| **Tailwind CSS** | Layout & utilities |
| **backdrop-filter** | Glass navbar, cards, CTA |
| **tsParticles** | Light ambient background |
| **Canvas 2D** | Interactive light trail |

No Three.js / R3F.

## Brand

| Asset | Path |
|-------|------|
| Logo mark | `assets/logo-mark.svg` |
| Full wordmark | `assets/logo.svg` |
| Favicon | `assets/logo-mark.svg` |

Soft indigo mark: abstract **V** arc + intelligence node on a glass tile.

## Run locally

```powershell
cd ai-lab-landing
python -m http.server 5173
```

Open [http://localhost:5173](http://localhost:5173)

## Sections

1. Navbar — transparent → blur on scroll  
2. Hero — staggered GSAP entrance  
3. Features — 4 glass cards, magnetic lift  
4. How it works — 4 steps + timeline  
5. Experience — canvas trail  
6. CTA + Footer  

## Palette

- Background: `#FAFAFA`
- Accent: `#6366F1`
- Text: `#1D1D1F` / `#6E6E73`

UI copy is **English**. `prefers-reduced-motion` is supported.
