from flask import Flask, request, jsonify
import swisseph as swe
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


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

    planets = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
        'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN
    }

    weak_planets = []
    for name, num in planets.items():
        pos, _ = swe.calc_ut(jd, num)
        degree = pos[0] % 30
        if degree < 5 or degree > 25:
            weak_planets.append(name)

    recommendations = {
        "Mercury": "Green Jade", "Venus": "Opal", "Mars": "Red Coral",
        "Jupiter": "Yellow Sapphire", "Saturn": "Blue Sapphire",
        "Moon": "Pearl", "Sun": "Ruby"
    }

    gems = [recommendations[p] for p in weak_planets if p in recommendations]

    return jsonify({"weak_planets": weak_planets, "recommended_gemstones": gems})

if __name__ == '__main__':
    app.run(debug=True)
