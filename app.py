from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Factores de emisión (kg CO2 por unidad)
FACTORES = {
    "auto_km_semana": 0.21 * 52,
    "vuelos_cortos": 250,
    "vuelos_largos": 1500,
    "electricidad": 0.233 * 12,
    "gas_m3": 2.02 * 12,
    "carne_roja": 2.7 * 52,
    "pollo": 0.69 * 52,
}

# 🧮 Calcular huella
@app.route("/api/calcular", methods=["POST"])
def calcular():
    data = request.json

    parciales = {
        k: float(data.get(k, 0)) * FACTORES[k] / 1000
        for k in FACTORES
    }

    total = sum(parciales.values())

    if total < 5:
        nivel = {
            "tipo": "Bajo 🌿",
            "mensaje": "Estás por debajo del promedio mundial. ¡Bien hecho!"
        }
    elif total < 10:
        nivel = {
            "tipo": "Medio ⚠️",
            "mensaje": "Cerca del promedio global. Hay margen para mejorar."
        }
    else:
        nivel = {
            "tipo": "Alto 🔴",
            "mensaje": "Supera el promedio mundial. Considerá reducir vuelos y consumo de carne."
        }

    return jsonify({
        "total": round(total, 2),
        "parciales": parciales,
        "nivel": nivel
    })

# 🤖 Consejos tipo IA
@app.route("/api/ai", methods=["POST"])
def ai_advice():
    data = request.json
    total = float(data.get("total", 0))

    if total < 5:
        advice = "¡Excelente! Tu huella de carbono es baja. Sigue así 🌱"
    elif total < 10:
        advice = "Nivel moderado. Reducí vuelos y optimizá energía ⚡"
    else:
        advice = "Nivel alto. Bajá carne roja, vuelos y consumo energético 🔴"

    return jsonify({
        "advice": advice
    })

# 🧪 Ruta de prueba
@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"message": "Backend funcionando 🚀"})

if __name__ == "__main__":
    app.run(debug=True)
