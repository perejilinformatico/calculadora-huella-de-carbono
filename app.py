from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

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

        except Exception as e:
            advice = f"Error al obtener consejo: {str(e)}"

    return render_template('ai.html', advice=advice)

if __name__ == "__main__":
    app.run(debug=True)
