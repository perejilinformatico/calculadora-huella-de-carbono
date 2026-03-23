from flask import Flask, render_template, request

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


if __name__ == "__main__":
    app.run(debug=True)