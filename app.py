from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import random

app = Flask(__name__)
CORS(app)

# Factores de emisión (kg CO2 por unidad)
FACTORES = {
    "auto_km_semana": 0.21 * 52,        # kg CO2 por km/semana → anual
    "vuelos_cortos":  250,               # kg CO2 por vuelo <3h
    "vuelos_largos":  1500,              # kg CO2 por vuelo >3h
    "electricidad":   0.233 * 12,        # kg CO2 por kWh/mes → anual
    "gas_m3":         2.02 * 12,         # kg CO2 por m³/mes → anual
    "carne_roja":     2.7 * 52,          # kg CO2 por porción/semana → anual
    "pollo":          0.69 * 52,         # kg CO2 por porción/semana → anual
}

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None

    if request.method == "POST":
        datos = {k: float(request.form.get(k, 0)) for k in FACTORES}

        parciales = {k: datos[k] * FACTORES[k] / 1000 for k in FACTORES}  # → toneladas
        total = sum(parciales.values())

        if total < 5:
            nivel = ("Bajo 🌿", "Estás por debajo del promedio mundial. ¡Bien hecho!")
        elif total < 10:
            nivel = ("Medio ⚠️", "Cerca del promedio global. Hay margen para mejorar.")
        else:
            nivel = ("Alto 🔴", "Supera el promedio mundial. Considerá reducir vuelos y consumo de carne.")

        resultado = {"total": round(total, 2), "parciales": parciales, "nivel": nivel}

    return render_template("index.html", resultado=resultado)

@app.route('/ai', methods=['GET', 'POST'])
def ai_advice():
    advice = None
    if request.method == 'POST':
        total = float(request.form.get('total', 0))

        try:
            if total < 5:
                consejos = [
                    "¡Excelente! Tu huella es baja. Sigue usando transporte público.",
                    "Vas muy bien 🌿. Mantén hábitos como reciclar y reducir residuos.",
                    "Buen trabajo. Podés mejorar aún más usando energías renovables."
                ]
            elif total < 10:
                consejos = [
                    "Podés reducir vuelos y optimizar el uso de electricidad.",
                    "Intentá consumir menos carne roja y más opciones sostenibles.",
                    "Usar bici o transporte público puede bajar tu huella bastante."
                ]
            else:
                consejos = [
                    "Reducí viajes en avión ✈️ y priorizá transporte sostenible.",
                    "Cambiá a energías renovables y bajá el consumo eléctrico.",
                    "Disminuí el consumo de carne roja 🥩.",
                    "Optá por transporte público o compartido 🚗."
                ]

            # Elegir uno aleatorio
            index = random.randint(0, len(consejos) - 1)
            advice = consejos[index]

    return render_template('ai.html', advice=advice)

@app.route("/api/calculate", methods=["POST"])
def calculate():
    try:
        data = request.json

        # Obtener datos del body JSON
        datos = {k: float(data.get(k, 0)) for k in FACTORES}

        # Calcular toneladas
        parciales = {
            k: (datos[k] * FACTORES[k]) / 1000
            for k in FACTORES
        }

        total = sum(parciales.values())

        # Nivel
        if total < 5:
            nivel = {
                "label": "Bajo 🌿",
                "desc": "Estás por debajo del promedio mundial."
            }
        elif total < 10:
            nivel = {
                "label": "Medio ⚠️",
                "desc": "Cerca del promedio global."
            }
        else:
            nivel = {
                "label": "Alto 🔴",
                "desc": "Supera el promedio mundial."
            }

        return jsonify({
            "total": round(total, 2),
            "parciales": parciales,
            "nivel": nivel
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# 🔹 ROUTER 2: Consejos
@app.route("/api/advice", methods=["POST"])
def advice():
    try:
        data = request.json
        total = float(data.get("total", 0))

        if total < 5:
            consejos = [
                "Vas excelente 🌿. Mantené hábitos sostenibles.",
                "Tu impacto es bajo. Podés probar energías renovables.",
                "Seguís en buen camino. Reducí residuos para mejorar más."
            ]
        elif total < 10:
            consejos = [
                "Reducí consumo eléctrico ⚡.",
                "Comé menos carne roja 🥩.",
                "Usá transporte público o bici 🚲."
            ]
        else:
            consejos = [
                "Reducí vuelos ✈️ urgente.",
                "Pasate a energías renovables ⚡.",
                "Bajá consumo de carne roja 🥩.",
                "Movete en transporte sostenible 🚗."
            ]

        return jsonify({
            "advice": random.choice(consejos)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
