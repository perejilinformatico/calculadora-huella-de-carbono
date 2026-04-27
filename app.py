from flask import Flask, render_template, request, jsonify, session
import requests
import random
 
app = Flask(__name__)
app.secret_key = 'huella_carbono_2026'  # Clave para sesiones
 
 
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

# Recomendaciones específicas por factor dominante
RECOMENDACIONES = {
    "auto_km_semana": [
        "Tu mayor emisión viene del uso del auto. Considerá usar transporte público 2-3 días a la semana o compartir viajes. Cada km que evites en auto reduce directamente tu huella de carbono.",
        "El transporte es tu factor más pesado. Podés: cambiar a vehículos eléctricos, usar bicicleta para distancias cortas, o combinar auto con transporte público en trayectos largos.",
        "Reducir km en auto es tu prioridad. Trabajar desde casa un día por semana, usar transporte colectivo o compartir auto con compañeros puede disminuir significativamente tu huella anual."
    ],
    "vuelos_cortos": [
        "✈️ Tus vuelos cortos representan una parte importante de tu huella. Considerá reemplazarlos con transporte terrestre (tren, bus) cuando sea posible.",
        "✈️ Los vuelos están entre tus mayores emisiones. Para viajes cortos (<1000km), el tren o bus son mucho más sostenibles. Reservá los vuelos para distancias donde no hay alternativa.",
        "✈️ Limitar vuelos cortos podría ser tu mayor ahorro. Si es posible, concentrá tus viajes en menos ocasiones pero más largas para optimizar."
    ],
    "vuelos_largos": [
        "Tus vuelos largos generan una huella significativa. Considerá reducir la frecuencia o compensar con proyectos de neutralización de carbono.",
        "Los vuelos de larga distancia son tu factor dominante. Si es laboral, negocia teletrabajo parcial. Si es turismo, planificá viajes menos frecuentes pero más extensos.",
        "Tu mayor impacto viene de vuelos largos. Aunque son inevitables a veces, podés reducir frecuencia, elegir vuelos directos (más eficientes) y compensar emisiones."
    ],
    "electricidad": [
        "Tu consumo eléctrico es alto. Instalá paneles solares, usa LED en toda la casa, desconectá equipos en standby y aprovechá la luz natural.",
        "La electricidad es tu mayor emisión. Revisa qué electrodomésticos consumen más energía. Los aires acondicionados y calefactores son generalmente los culpables.",
        "Optimizá tu consumo eléctrico: cambiá a energías renovables si es posible, usa electrodomésticos eficientes (clase A), y reduce el uso de calefacción/refrigeración extrema."
    ],
    "gas_m3": [
        "Tu consumo de gas para calefacción es alto. Mejorá el aislamiento térmico, usa calefacción inteligente y considerá cambiar a calefactores eléctricos eficientes.",
        "El gas representa tu mayor emisión. Bajá la temperatura 1-2°C, usá ropa abrigada en invierno, sella grietas en ventanas y puertas para retener calor.",
        "Reducir gas es clave para tu huella. Instalá termostatos inteligentes para controlar mejor la temperatura, o cambià a bombas de calor más eficientes."
    ],
    "carne_roja": [
        "Tu consumo de carne roja es tu factor más contaminante. Reducir a 1-2 veces por semana puede bajar mucho tu huella. Probá alternativas como pollo, pescado o proteínas vegetales.",
        "La carne roja que consumís genera muchas emisiones. Intentá hacer 'Lunes sin Carne' o cambiar gradualmente a dietas flexitarianas con más vegetales.",
        "Tu mayor impacto viene de la dieta. La carne roja tiene 3-4 veces más emisiones que el pollo. Reemplazá varias porciones por legumbres, frutos secos o vegetales."
    ],
    "pollo": [
        "Tu consumo de pollo es significativo. Aunque es mejor que la carne roja, reducir porciones e incluir más proteínas vegetales (lentejas, garbanzos) puede ayudar.",
        "El pollo es mejor que la carne roja, pero aún tiene impacto. Combinalo más con huevos, legumbres y frutos secos para una dieta más equilibrada.",
        "Aumentá tu consumo de proteína vegetal: legumbres, tofu y frutos secos tienen mucha menos huella que cualquier carne. Probá recetas vegetarianas 2-3 veces a la semana."
    ]
}
 
@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
 
    if request.method == "POST":
        datos = {k: float(request.form.get(k, 0)) for k in FACTORES}
 
        parciales = {k: datos[k] * FACTORES[k] / 1000 for k in FACTORES}  # → toneladas
        total = sum(parciales.values())
 
        if total < 5:
            nivel = ("Bajo", "Estás por debajo del promedio mundial. ¡Bien hecho!")
        elif total < 10:
            nivel = ("Medio", "Cerca del promedio global. Hay margen para mejorar.")
        else:
            nivel = ("Alto", "Supera el promedio mundial. Considerá reducir vuelos y consumo de carne.")
 
        resultado = {"total": round(total, 2), "parciales": parciales, "nivel": nivel}
        
        # Guardar los parciales en sesión para /ai
        session['parciales'] = {k: round(v, 2) for k, v in parciales.items()}
        session['total'] = round(total, 2)
 
    return render_template("index.html", resultado=resultado)
 
@app.route('/ai', methods=['GET', 'POST'])
def ai_advice():
    advice = None
    
    # Recuperar los parciales de la sesión
    parciales = session.get('parciales', {})
    
    if parciales:
        # Encontrar cuál es el factor con más emisiones
        factor_maximo = max(parciales, key=parciales.get)
        
        # Obtener recomendaciones para el factor dominante
        if factor_maximo in RECOMENDACIONES:
            consejos = RECOMENDACIONES[factor_maximo]
            advice = {
                'recomendacion': consejos[random.randint(0, len(consejos) - 1)],
                'factor': factor_maximo,
                'emision': parciales[factor_maximo]
            }
        else:
            advice = {
                'recomendacion': "Todos tus factores están balanceados. Mantené buenos hábitos en varias áreas.",
                'factor': None,
                'emision': 0
            }
 
    return render_template('ai.html', advice=advice)
 
if __name__ == "__main__":
    app.run()