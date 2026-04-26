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
                  "Vas excelente 🌿 Tu huella de carbono está por debajo del promedio global. Esto significa que tus hábitos actuales ya tienen un impacto positivo. Aun así, podés mejorar aún más priorizando productos locales, reduciendo desperdicios y manteniendo el uso eficiente de energía en tu hogar.",
                  "Tu estilo de vida es bastante sostenible. Seguir usando transporte público, bicicleta o caminatas no solo mantiene baja tu huella, sino que también reduce contaminación urbana. Si querés optimizar aún más, podés revisar tu consumo energético en dispositivos electrónicos y reducir el uso innecesario en standby.",
                  "Estás en un buen camino ecológico 🌱 Podés reforzar tus hábitos eligiendo alimentos de menor impacto ambiental, evitando desperdicios de comida y reutilizando materiales cuando sea posible. Pequeños ajustes pueden hacer que tu huella sea aún más baja sin cambiar tu estilo de vida."
                ]
            elif total < 10:
                consejos = [
                  "Tu huella está cerca del promedio global ⚠️ Esto significa que hay oportunidades claras de mejora. Reducir el consumo de carne roja, optimizar el uso de electricidad en el hogar y disminuir viajes innecesarios en vehículo privado puede bajar significativamente tu impacto ambiental anual.",
                  "Podés mejorar bastante tu impacto ambiental con cambios simples pero constantes. Por ejemplo: usar más transporte público o bicicleta algunos días a la semana, reducir el consumo de productos de alta huella como carne roja, y elegir electrodomésticos eficientes energéticamente.",
                  "Estás en una zona intermedia 🌍 Para avanzar hacia un estilo de vida más sostenible, intentá planificar mejor tus desplazamientos para reducir viajes cortos en auto, moderar el consumo de energía en horas pico y aumentar el consumo de alimentos vegetales."
                ]
            else:
                consejos = [
                   "Tu huella de carbono es elevada 🔴 Esto suele estar relacionado con transporte frecuente en avión, alto consumo energético o una dieta con mucha carne roja. Reducir incluso parcialmente estos factores puede generar una disminución significativa en tu impacto anual.",
                   "Actualmente tu impacto ambiental supera el promedio global. Podés empezar priorizando cambios importantes como reducir vuelos de corta distancia, optar por transporte compartido o público, y revisar tu consumo energético en el hogar para identificar desperdicios.",
                   "Tu estilo de vida tiene un impacto alto en emisiones 🌍 Cambiar algunos hábitos clave puede hacer una gran diferencia: disminuir el consumo de carne roja, optimizar el uso de electricidad y reducir el uso de transporte individual motorizado. No hace falta cambiar todo de golpe, pero sí empezar por lo más pesado en emisiones."
                ]

            # Elegir uno aleatorio
            index = random.randint(0, len(consejos) - 1)
            advice = consejos[index]

    return render_template('ai.html', advice=advice)

if __name__ == "__main__":
    app.run(debug=True)
