import requests
from bs4 import BeautifulSoup

ENERGY_PER_MB = 0.2   # Wh per MB (approx)
CO2_PER_KWH = 400     # grams CO2 per kWh (global avg)

def _grade(score: int):
    if score >= 80:
        return "Excellent 🌿", "success"
    elif score >= 60:
        return "Good ✅", "primary"
    elif score >= 40:
        return "Average ⚠️", "warning"
    else:
        return "Poor ❌", "danger"

def analyze_website(url):
    try:
        response = requests.get(url, timeout=12, headers={
            "User-Agent": "EcoWeb/1.0 (+student-project)"
        })
        response.raise_for_status()

        html_bytes = response.text.encode("utf-8")
        page_size_mb = len(html_bytes) / (1024 * 1024)

        soup = BeautifulSoup(response.text, "html.parser")
        images = len(soup.find_all("img"))
        scripts = len(soup.find_all("script"))
        videos = len(soup.find_all("video"))
        links = len(soup.find_all("a"))

        # Energy + CO2 (base estimate using HTML only)
        energy_used_wh = page_size_mb * ENERGY_PER_MB
        co2_g = (energy_used_wh / 1000) * CO2_PER_KWH

        # --- Green Score model (balanced, not too harsh) ---
        green_score = 100
        green_score -= page_size_mb * 12
        green_score -= scripts * 0.6
        green_score -= images * 0.4
        green_score -= videos * 6

        green_score = max(0, min(100, int(green_score)))
        rating_text, rating_badge = _grade(green_score)

        # --- Simulated Optimization (Before vs After) ---
        # Assumptions: compress images + bundle JS + remove unused assets
        # This is for demo impact; in future version it can be actual optimization.
        optimized_size_mb = max(0.02, page_size_mb * 0.60)  # 40% reduction
        optimized_energy_wh = optimized_size_mb * ENERGY_PER_MB
        optimized_co2_g = (optimized_energy_wh / 1000) * CO2_PER_KWH

        co2_saved_g = max(0.0, co2_g - optimized_co2_g)
        saved_percent = 0
        if co2_g > 0:
            saved_percent = int((co2_saved_g / co2_g) * 100)

        # --- Real-life Equivalents (for judges) ---
        # Phone charge ~ 12 Wh (typical smartphone ~ 3000-4000mAh at ~3.7V)
        phone_charges = co2_saved_g / ((12 / 1000) * CO2_PER_KWH) if CO2_PER_KWH else 0

        # LED bulb 10W for X minutes -> energy = (10W * minutes/60)/1000 kWh
        # Convert energy saved from size difference:
        energy_saved_wh = max(0.0, energy_used_wh - optimized_energy_wh)
        led_minutes = (energy_saved_wh / 10) * 60 if energy_saved_wh > 0 else 0  # 10W bulb

        # Trees equivalent (rough awareness metric)
        trees = co2_g / 21  # ~21g/day absorbed per tree (approx)

        # --- AI Tips (actionable) ---
        tips = []
        if page_size_mb > 2:
            tips.append("Compress images and remove unused assets to reduce page size.")
        if scripts > 8:
            tips.append("Bundle/minify JavaScript and remove unused libraries.")
        if images > 20:
            tips.append("Convert images to WebP/AVIF and use lazy-loading.")
        if videos > 0:
            tips.append("Avoid autoplay videos and use lower resolution by default.")
        if links > 150:
            tips.append("Reduce unnecessary redirects and heavy tracking on linked pages.")
        if not tips:
            tips.append("This page looks fairly optimized 🌱 Try reducing scripts for an even better score.")

        return {
            "url": url,
            "size": round(page_size_mb, 2),
            "co2": round(co2_g, 4),
            "score": green_score,
            "rating": rating_text,
            "rating_badge": rating_badge,
            "images": images,
            "scripts": scripts,
            "videos": videos,
            "links": links,
            "trees": round(trees, 3),

            # before/after
            "opt_size": round(optimized_size_mb, 2),
            "opt_co2": round(optimized_co2_g, 4),
            "co2_saved": round(co2_saved_g, 4),
            "saved_percent": saved_percent,

            # equivalents
            "phone_charges": round(phone_charges, 2),
            "led_minutes": int(led_minutes),

            "tips": tips
        }

    except Exception as e:
        print("Error:", e)
        return None
