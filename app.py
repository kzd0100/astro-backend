from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe

app = Flask(__name__)
CORS(app)

# ----------------- Planet Rules -----------------
planet_signs = {
    "Sun": {"own": ["Leo"], "exalt": "Aries", "debilitate": "Libra"},
    "Moon": {"own": ["Cancer"], "exalt": "Taurus", "debilitate": "Scorpio"},
    "Mars": {"own": ["Aries", "Scorpio"], "exalt": "Capricorn", "debilitate": "Cancer"},
    "Mercury": {"own": ["Gemini", "Virgo"], "exalt": "Virgo", "debilitate": "Pisces"},
    "Jupiter": {"own": ["Sagittarius", "Pisces"], "exalt": "Cancer", "debilitate": "Capricorn"},
    "Venus": {"own": ["Taurus", "Libra"], "exalt": "Pisces", "debilitate": "Virgo"},
    "Saturn": {"own": ["Capricorn", "Aquarius"], "exalt": "Libra", "debilitate": "Aries"}
}

planets = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN
}

recommendations = {
    "Mercury": "Green Jade",
    "Venus": "Opal",
    "Mars": "Red Coral",
    "Jupiter": "Yellow Sapphire",
    "Saturn": "Blue Sapphire",
    "Moon": "Pearl",
    "Sun": "Ruby"
}

sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
              "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# ----------------- Helper Functions -----------------

def get_sign_name(degree):
    return sign_names[int(degree // 30)]

def get_house(planet_deg, asc_deg=75):  # 75° = 15° Gemini
    rel_deg = (planet_deg - asc_deg) % 360
    return int(rel_deg // 30) + 1

def evaluate_strength(planet, sign, house):
    score = 0
    info = planet_signs.get(planet, {})
    if sign == info.get("exalt"):
        score += 2
    elif sign == info.get("debilitate"):
        score -= 2
    elif sign in info.get("own", []):
        score += 1
    if house in [6, 8, 12]:
        score -= 1
    return score

# ----------------- Main Route -----------------

@app.route('/get_gemstone', methods=['POST'])
def get_gemstone():
    data = request.json
    dob = data['dob']  # format: YYYY-MM-DD
    time = data['time']  # format: HH:MM
    lat = float(data['lat'])
    lon = float(data['lon'])

    year, month, day = map(int, dob.split('-'))
    hour, minute = map(int, time.split(':'))
    jd = swe.julday(year, month, day, hour + minute/60)

    swe.set_topo(lon, lat, 0)
    swe.set_ephe_path('.')

    weak_planets = []
    for name, code in planets.items():
        pos, _ = swe.calc_ut(jd, code)
        degree = pos[0]
        sign = get_sign_name(degree)
        house = get_house(degree)

        score = evaluate_strength(name, sign, house)
        if score < 0:
            weak_planets.append(name)

    gems = [recommendations[p] for p in weak_planets if p in recommendations]

    return jsonify({
        "weak_planets": weak_planets,
        "recommended_gemstones": gems
    })

if __name__ == '__main__':
    app.run(debug=True)
