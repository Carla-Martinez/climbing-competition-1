import streamlit as st
import pandas as pd
import os
from streamlit_autorefresh import st_autorefresh  # Componente necesario

# --- PB iniciales ---
competidores = {
    "Unax": 5.35,
    "Ivan": 7.149,
    "Leslie": 6.66,
    "Leire": 7.32,
    "Haize": 8.67,
    "Aida": 9.35,
    "Maria": 7.98,
    "Alberto": 5.409,
    "Miquel": 5.230,
    "Alex Rivas": 5.41,
    "Alejo": 5.47,
    "Carla": 6.96,
    "Ola": 6.51,
    "Oriol": 5.47,
    "Julia": 8.80,
    "Víctor": 5.97
}

CSV_FILE = "resultados.csv"

# --- Función de puntuación ---
def puntuar(pb, tiempo, nuevo_pb):
    dif = abs(tiempo - pb)
    puntos = 0
    if dif <= 0.1:
        puntos = 3
    elif dif <= 0.2:
        puntos = 2
    elif dif <= 0.3:
        puntos = 1
    else:
        puntos = 0
    if nuevo_pb:
        puntos += 4
    return puntos
    if dif <= 0.1: puntos = 3
    elif dif <= 0.2: puntos = 2
    elif dif <= 0.3: puntos = 1
    else: puntos = 0
    return puntos + (4 if nuevo_pb else 0)

st.title("🏆 Competición de Escalada - Ranking en Vivo")

# Auto-refresco cada 5 segundos
_ = st_autorefresh(interval=5000, key="refresh")


st_autorefresh = st.autorefresh(interval=5000, key="refresh")  # cada 5000 ms = 5s

# --- Cargar resultados ---
# Carga resultados desde CSV
if os.path.exists(CSV_FILE):
    df_historial = pd.read_csv(CSV_FILE)
    resultados = {nombre: [] for nombre in competidores.keys()}
    for _, row in df_historial.iterrows():
        resultados[row["Competidor"]].append((row["Tipo"], row["Valor"] if not pd.isna(row["Valor"]) else None))
        resultados[row["Competidor"]].append((row["Tipo"], row["Valor"]))
else:
    resultados = {nombre: [] for nombre in competidores.keys()}

# --- Entrada dinámica ---
col1, col2, col3 = st.columns([2,2,2])
# Formulario de entrada
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    nombre = st.selectbox("Escoge competidor", list(competidores.keys()))
with col2:
    opcion = st.radio("Resultado", ["Tiempo", "DNF"], horizontal=True)
with col3:
    tiempo = None
    if opcion == "Tiempo":
        tiempo = st.number_input("Nuevo tiempo (s)", min_value=0.0, step=0.01)
    tiempo = st.number_input("Nuevo tiempo (s)", min_value=0.0, step=0.01) if opcion == "Tiempo" else None

col4, col5, col6 = st.columns(3)
with col4:
    if st.button("➕ Añadir intento"):
        if opcion == "Tiempo" and tiempo > 0:
            resultados[nombre].append(("tiempo", tiempo))
            st.success(f"{nombre}: tiempo {tiempo:.2f}s añadido")
        elif opcion == "DNF":
            resultados[nombre].append(("dnf", None))
            st.warning(f"{nombre}: DNF añadido")

        # Guardar en CSV
        rows = []
        for n, intentos in resultados.items():
            for t, v in intentos:
                rows.append({"Competidor": n, "Tipo": t, "Valor": v})
        resultados[nombre].append(("tiempo", tiempo) if opcion == "Tiempo" and tiempo > 0 else ("dnf", None))
        st.success(f"{nombre}: {'tiempo ' + f'{tiempo:.2f}s' if opcion == 'Tiempo' else 'DNF'} añadido")
        rows = [{"Competidor": n, "Tipo": t, "Valor": v} for n, intentos in resultados.items() for t, v in intentos]
        pd.DataFrame(rows).to_csv(CSV_FILE, index=False)

with col5:
    if st.button("↩️ Deshacer último intento"):
        if resultados[nombre]:
            ultimo = resultados[nombre].pop()
            st.info(f"Último intento de {nombre} eliminado ({'DNF' if ultimo[0]=='dnf' else f'{ultimo[1]:.2f}s'})")

            # Guardar cambios
            rows = []
            for n, intentos in resultados.items():
                for t, v in intentos:
                    rows.append({"Competidor": n, "Tipo": t, "Valor": v})
            rows = [{"Competidor": n, "Tipo": t, "Valor": v} for n, intentos in resultados.items() for t, v in intentos]
            pd.DataFrame(rows).to_csv(CSV_FILE, index=False)
        else:
            st.error(f"{nombre} no tiene intentos para borrar")
def puntuar(pb, tiempo, nuevo_pb):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        resultados = {nombre: [] for nombre in competidores.keys()}
        st.success("Historial borrado, ¡competición reiniciada!")
        st.info("Historial borrado. Competición reiniciada.")

# --- Cálculo de puntos y ranking ---
# Cálculo de ranking
resultados_finales = []
for nombre, pb in competidores.items():
    intentos = resultados[nombre]
    puntos_totales = 0
    puntos = 0
    mejor = pb
    dnfs = 0
    for tipo, valor in intentos:
        if tipo == "tiempo":
            nuevo_pb = valor < mejor
            if len(intentos) > 7:
                puntos_totales += 0
            else:
                puntos_totales += puntuar(pb, valor, nuevo_pb)
                if nuevo_pb:
                    mejor = valor
        elif tipo == "dnf":
            if len(intentos) <= 7:
                puntos += puntuar(pb, valor, nuevo_pb)
                mejor = valor if nuevo_pb else mejor
        else:
            dnfs += 1
            penalizacion = -1
            if dnfs == 1:
                puntos_totales += 0
            elif dnfs > 1:
                puntos_totales += penalizacion
            if dnfs > 7 or len(intentos) > 7:
                puntos_totales += 0
    
            if dnfs > 1:
                puntos -= 1

    resultados_finales.append({
        "Competidor": nombre,
        "PB inicial": pb,
        "Intentos": len(intentos),
        "DNFs": dnfs,
        "Puntos": puntos_totales
        "Puntos": puntos
    })

df = pd.DataFrame(resultados_finales).sort_values(by="Puntos", ascending=False)

st.subheader("📊 Clasificación en Vivo")
st.table(df.reset_index(drop=True))

# --- Mostrar historial individual ---
st.subheader("📜 Historial de intentos")
for nombre, intentos in resultados.items():
    historial = []
    for tipo, valor in intentos:
        if tipo == "tiempo":
            historial.append(f"{valor:.2f}s")
        else:
            historial.append("DNF")
    historial = [f"{valor:.2f}s" if t == "tiempo" else "DNF" for t, valor in intentos]
    st.write(f"**{nombre}**: {', '.join(historial) if historial else 'Sin intentos'}")
