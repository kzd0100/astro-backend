from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe

app = Flask(__name__)
CORS(app)

# ----------------- Planet Rules -----------------
planet_signs = {
    "Sun": {"own": ["Leo"], "exalt": "Aries", "debilitate": "Libra", "enemy": ["Aquarius", "Capricorn"]},
    "Moon": {"own": ["Cancer"], "exalt": "Taurus", "debilitate": "Scorpio", "enemy": ["Capricorn", "Aquarius"]},
    "Mars": {"own": ["Aries", "Scorpio"], "exalt": "Capricorn", "debilitate": "Cancer", "enemy": ["Gemini", "Taurus"]},
    "Mercury": {"own": ["Gemini", "Virgo"], "exalt": "Virgo", "debilitate": "Pisces", "enemy": ["Sagittarius", "Pisces"]},
    "Jupiter": {"own": ["Sagittarius", "Pisces"], "exalt": "Cancer", "debilitate": "Capricorn", "enemy": ["Capricorn", "Libra"]},
    "Venus": {"own": ["Taurus", "Libra"], "exalt": "Pisces", "debilitate": "Virgo", "enemy": ["Aries", "Scorpio"]},
    "Saturn": {"own": ["Capricorn", "Aquarius"], "exalt": "Libra", "debilitate": "Aries", "enemy": ["Sun", "Moon", "Mars"]}
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

def get_house(planet_deg, asc_deg=75):  # Asc ~15° Gemini (3rd sign)
    rel_deg = (planet_deg - asc_deg) % 360
    return int(rel_deg // 30) + 1

def is_retrograde(planet_code, jd):
    flags = swe.calc_ut(jd, planet_code, flag=swe.FLG_SPEED)[1]
    return flags[0] < 0  # negative speed = retrograde

def is_combust(planet_deg, sun_deg):
    diff = abs((planet_deg - sun_deg + 360) % 360)
    return diff < 8  # within 8 degrees of Sun = combust

def evaluate_strength(planet, sign, house, is_retro, combust):
    score = 0
    info = planet_signs.get(planet, {})

    if sign == info.get("exalt"):
        score += 2
    elif sign == info.get("debilitate"):
        score -= 2
    elif sign in info.get("own", []):
        score += 1
    elif sign in info.get("enemy", []):
        score -= 1

    if house in [6, 8, 12]:
        score -= 1
    if is_retro:
        score -= 1
    if combust:
        score -= 1

    return score

# ----------------- Main Route -----------------

@app.route('/get_gemstone', methods=['POST'])
def get_gemstone():
    data = request.json
    dob = data['dob']
    time = data['time']
    lat = float(data['lat'])
    lon = float(data['lon'])

    year, month, day = map(int, dob.split('-'))
    hour, minute = map(int, time.split(':'))
    jd = swe.julday(year, month, day, hour + minute / 60)

    swe.set_topo(lon, lat, 0)
    swe.set_ephe_path('.')

    weak_planets = []

    sun_deg, _ = swe.calc_ut(jd, swe.SUN)

    for name, code in planets.items():
        pos, _ = swe.calc_ut(jd, code)
        degree = pos[0]
        sign = get_sign_name(degree)
        house = get_house(degree)
        retro = is_retrograde(code, jd)
        combust = is_combust(degree, sun_deg[0])

        score = evaluate_strength(name, sign, house, retro, combust)
        if score < 0:
            weak_planets.append(name)

    gems = [recommendations[p] for p in weak_planets if p in recommendations]

    return jsonify({
        "weak_planets": weak_planets,
        "recommended_gemstones": gems
    })

if __name__ == '__main__':
    app.run(debug=True)
