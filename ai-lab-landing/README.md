# AI Lab — Landing Page

Apple Intelligence tarzı, temiz ve premium bir landing page.

## Stack

| Teknoloji | Kullanım |
|-----------|----------|
| **Lenis** | Ultra smooth scroll |
| **GSAP + ScrollTrigger** | Hero, reveal, timeline, magnetic hover |
| **Tailwind CSS** | Layout & utility |
| **backdrop-filter** | Glass navbar & kartlar |
| **tsParticles** | Hafif arka plan |
| **Canvas** | “Deneyimle” interaktif ışık izi |

3D / Three.js **yok**.

## Çalıştırma

Statik dosyalar; yerel bir sunucu ile açın (ES modules nedeniyle `file://` sorun çıkarabilir):

```powershell
cd C:\Users\USER\Desktop\tries\localmultiagent\ai-lab-landing

# Python
python -m http.server 5173

# veya Node
npx --yes serve -l 5173
```

Tarayıcı: [http://localhost:5173](http://localhost:5173)

## Bölümler

1. **Navbar** — şeffaf → scroll’da blur + küçülme  
2. **Hero** — staggered GSAP giriş + soft particles  
3. **Features** — 4 glass kart, magnetic lift  
4. **How it Works** — ScrollTrigger + timeline çizgisi  
5. **Deneyimle** — Canvas pointer trail  
6. **CTA + Footer**

## Renkler

- Arka plan: `#FAFAFA`
- Vurgu: `#6366F1` (soft indigo)
- Metin: koyu gri tonlar (`#1D1D1F` / `#6E6E73`)

## Notlar

- `prefers-reduced-motion` desteklenir.
- CDN üzerinden kütüphaneler yüklenir (internet gerekir).
