# Velora AI Lab — Landing Page

Apple Intelligence tarzı, temiz ve premium bir landing page. Cyberpunk / neon değil — yumuşak beyaz, bol whitespace, zarif tipografi.

## Stack

| Teknoloji | Kullanım |
|-----------|----------|
| **Lenis** | Ultra smooth scroll |
| **GSAP + ScrollTrigger** | Hero stagger, reveal, timeline, magnetic hover |
| **Tailwind CSS** | Layout & utility |
| **backdrop-filter** | Glass navbar, kartlar, CTA |
| **tsParticles** | Hafif ambient arka plan (düşük yoğunluk) |
| **Canvas 2D** | “Deneyimle” interaktif ışık izi |

3D / Three.js / React Three Fiber **yok**.

## Renk paleti

| Rol | Değer |
|-----|--------|
| Ana arka plan | `#FAFAFA` |
| Kart / cam | Beyaz + blur |
| Vurgu | Soft Indigo `#6366F1` |
| Metin | `#1D1D1F` / `#6E6E73` |

## Çalıştırma

ES modules nedeniyle yerel sunucu gerekir (`file://` sorun çıkarabilir):

```powershell
cd ai-lab-landing

# Python
python -m http.server 5173

# veya Node
npx --yes serve -l 5173
```

Tarayıcı: [http://localhost:5173](http://localhost:5173)

## Bölümler

1. **Navbar** — şeffaf → scroll’da blur + küçülme (GSAP + backdrop-filter)
2. **Hero** — staggered GSAP giriş + soft particles + ambient orbs
3. **Features** — 4 glass kart, magnetic lift + hafif tilt
4. **How it Works** — 4 adım, ScrollTrigger sol/sağ reveal + timeline çizgisi
5. **Deneyimle** — Canvas pointer trail + tıklama parıltısı
6. **CTA + Footer**

## Dosya yapısı

```
ai-lab-landing/
  index.html
  css/styles.css
  js/
    main.js              # bootstrap
    lenis-setup.js       # smooth scroll
    animations.js        # GSAP systems
    particles.js         # tsParticles
    canvas-interactive.js
  README.md
```

## Notlar

- `prefers-reduced-motion` desteklenir (animasyonlar sadeleşir, Lenis kapanır).
- Kütüphaneler CDN üzerinden yüklenir (internet gerekir).
- Animasyonlar yavaş ve premium; abartısız.
