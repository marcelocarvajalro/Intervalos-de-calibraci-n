# Librerías
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta
import datetime
import math

st.set_page_config(layout="wide")
st.title("Evaluador de Intervalos de Calibración")

# Barra lateral izquierda
st.sidebar.header("Cálculo de Intervalos de Calibración")
metodo = st.sidebar.selectbox("Seleccione el método de evaluación",
                              ["Escalera (Error medio)", "Escalera (Error)", "Cartas de Control"])

# ------------------------------------------------------------------------------------------------------------

if metodo == "Escalera (Error)":
    st.title("Método de Escalera")
    st.sidebar.subheader("Datos para Método de Escalera")

    ajuste = st.sidebar.selectbox("¿El equipo actualmente se ajustó?", ["No", "Sí"])

    if ajuste == "Sí":
        st.error("El método de escalera no se puede aplicar con equipos actualmente ajustados.")
        st.write("Se recomienda utilizar el último intervalo de calibración o el recomendado por el fabricante.")
    else:

        try:
            fecha_anterior = st.sidebar.date_input(
                "Fecha de calibración anterior",
                value=datetime.date(2000, 1, 1),
                key="fecha1",
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date(2100, 12, 31),
                help="🗓️ Esta es la fecha del certificado de calibración anterior al vigente. Seleccione la fecha desde el calendario. No escriba números manualmente."

            )
            if not isinstance(fecha_anterior, datetime.date):
                st.error(
                    f"La Fecha de calibración no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
                st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
                st.stop()

        except Exception:
            st.error(
                f"La Fecha de calibración no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
            st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
            st.stop()

        try:
            fecha_registro = st.sidebar.date_input(
                "Fecha de calibración actual",
                value=fecha_anterior + timedelta(days=1),
                key="fecha",
                min_value=fecha_anterior + timedelta(days=1),
                max_value=datetime.date(2100, 12, 31),
                help="🗓️ Esta es la fecha del certificado de calibración vigente, es decir, de la última calibración realizada. Seleccione la fecha desde el calendario. No escriba números manualmente."
            )
            if not isinstance(fecha_registro, datetime.date):
                st.error(
                    f"La Fecha de calibración no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
                st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
                st.stop()

        except Exception:
            st.error(
                f"La Fecha de calibración no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
            st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
            st.stop()

        error = st.sidebar.number_input("Error medio [mm]", value=0.0025, format="%.5f")
        incertidumbre = st.sidebar.number_input("Incertidumbre expandida [mm]", value=0.0005, format="%.5f")
        if incertidumbre < 0:
            st.error("La incertidumbre expandida debe ser mayor o igual a cero.")

        error_max = st.sidebar.number_input("Error máximo permitido [mm]", value=0.0030, format="%.5f")
        if error_max < 0:
            st.error("El error máximo permitido debe ser mayor o igual a cero.")

        fecha_inicial_global = fecha_anterior
        fecha_final_global = fecha_registro
        delta_dias_global = (fecha_final_global - fecha_inicial_global).days
        delta_anios_global = delta_dias_global / 365.25

        intervalo_anterior = delta_anios_global
        if delta_dias_global <= 0:
            st.error("El intervalo anterior debe ser mayor o igual a 1 día.")

        if incertidumbre >= 0 and error_max >= 0 and delta_dias_global > 0:

            # Límites ±80% del error máximo permitido
            limite_superior = +0.8 * error_max
            limite_inferior = -0.8 * error_max

            # Recomendación
            if (error - incertidumbre) <= (-1 * error_max):
                intervalo_recomendado = 0
                recomendacion = "El equipo alcanzó o excede el EMP. Se recomienda hacer un ajuste mecánico del equipo y calibrar inmediatamente. Use el intervalo de calibración recomendado por el fabricante."

            elif (error + incertidumbre) >= (error_max):
                intervalo_recomendado = 0
                recomendacion = "El equipo alcanzó o excede el EMP. Se recomienda hacer un ajuste mecánico del equipo y calibrar inmediatamente. Use el intervalo de calibración recomendado por el fabricante."

            elif ((error + incertidumbre) < limite_superior) and (error - incertidumbre) > limite_inferior:
                intervalo_recomendado = intervalo_anterior * 1.5
                nueva_fecha = fecha_final_global + timedelta(days=(intervalo_recomendado * 365.25))
                recomendacion = "Ampliar el intervalo en 50%"

            else:
                intervalo_recomendado = intervalo_anterior * 0.5
                nueva_fecha = fecha_final_global + timedelta(days=(intervalo_recomendado * 365.25))
                recomendacion = "Reducir el intervalo en 50%"

            # Layout
            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("Resultado")
                st.write(f"**Error medio:** {error:.5f} mm")
                st.write(f"**Límite de control superior (EMP*80%):** {limite_superior:.5f} mm")
                st.write(f"**Límite de control inferior (–EMP*80%):** {limite_inferior:.5f} mm")
                st.write(f"**Intervalo anterior:** {intervalo_anterior:.2f} años")
                if intervalo_recomendado == 0:
                    st.write(f"**Recomendación:** {recomendacion}")
                else:
                    st.write(f"**Recomendación:** {recomendacion}")
                    st.write(f"**Intervalo recomendado:** {intervalo_recomendado:.2f} años")
                    st.write(f"La fecha recomendada para la próxima calibración es: {nueva_fecha.strftime('%d/%m/%Y')}")

            with col2:
                st.subheader("Visualización")
                fig, ax = plt.subplots()
                ax.axhline(limite_superior, color='orange', linestyle='--', label='Límite Superior (EMP * 80%)')
                ax.axhline(limite_inferior, color='orange', linestyle='--', label='Límite Inferior (-EMP * 80%)')
                ax.axhline(error_max, color='gray', linestyle='--', label='+EMP')
                ax.axhline(-error_max, color='gray', linestyle='--', label='-EMP')
                ax.errorbar(
                    x=[0],
                    y=[error],
                    yerr=incertidumbre,
                    fmt='o',
                    color='blue',
                    markersize=10,
                    label='Error ± U'
                )
                ax.set_xticks([0])
                ax.set_xticklabels(["Error"])
                ax.set_ylim(-error_max * 1.2, error_max * 1.2)
                ax.set_ylabel("Límites de control [mm]")
                ax.set_title("Evaluación por Método de Escalera")
                ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=2)
                st.pyplot(fig)

# ------------------------------------------------------------------------------------------------------------

elif metodo == "Escalera (Error medio)":
    st.title("Método de Escalera")
    st.sidebar.subheader("Datos para Método de Escalera")

    ajuste = st.sidebar.selectbox("¿El equipo actualmente se ajustó?", ["No", "Sí"])

    if ajuste == "Sí":
        st.error("El método de escalera no se puede aplicar con equipos actualmente ajustados.")
        st.write("Se recomienda utilizar el último intervalo de calibración o el recomendado por el fabricante.")
    else:

        try:
            fecha_anterior = st.sidebar.date_input(
                "Fecha de calibración anterior",
                value=datetime.date(2000, 1, 1),
                key="fecha1",
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date(2100, 12, 31),
                help="🗓️ Esta es la fecha del certificado de calibración anterior al vigente. Seleccione la fecha desde el calendario. No escriba números manualmente."
            )
            if not isinstance(fecha_anterior, datetime.date):
                st.error(
                    f"La Fecha de calibración no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
                st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
                st.stop()

        except Exception:
            st.error(
                f"La Fecha de calibración no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
            st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
            st.stop()

        try:
            fecha_registro = st.sidebar.date_input(
                "Fecha de calibración actual",
                value=fecha_anterior + timedelta(days=1),
                key="fecha",
                min_value=fecha_anterior + timedelta(days=1),
                max_value=datetime.date(2100, 12, 31),
                help="🗓️ Esta es la fecha del certificado de calibración vigente, es decir, de la última calibración realizada. Seleccione la fecha desde el calendario. No escriba números manualmente."
            )
            if not isinstance(fecha_registro, datetime.date):
                st.error(
                    f"La Fecha de calibración no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
                st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
                st.stop()

        except Exception:
            st.error(
                f"La Fecha de calibración no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
            st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
            st.stop()

        error = st.sidebar.number_input("Error medio [mm]", value=0.0025, format="%.5f")
        error_max = st.sidebar.number_input("Error máximo permitido [mm]", value=0.0030, format="%.5f")
        if error_max < 0:
            st.error("El error máximo permitido debe ser mayor o igual a cero.")

        fecha_inicial_global = fecha_anterior
        fecha_final_global = fecha_registro
        delta_dias_global = (fecha_final_global - fecha_inicial_global).days
        delta_anios_global = delta_dias_global / 365.25

        intervalo_anterior = delta_anios_global

        if delta_dias_global <= 0:
            st.error("El intervalo anterior debe ser mayor o igual a 1 día.")

        if error_max >= 0 and delta_dias_global > 0:

            # Límites ±80% del error máximo permitido
            limite_superior = +0.8 * error_max
            limite_inferior = -0.8 * error_max

            # Recomendación
            if (error) <= (-1 * error_max):
                intervalo_recomendado = 0
                recomendacion = "El equipo excede el EMP. Se recomienda hacer un ajuste mecánico del equipo y calibrar inmediatamente. Use el intervalo de calibración recomendado por el fabricante."

            elif (error) >= (error_max):
                intervalo_recomendado = 0
                recomendacion = "El equipo excede el EMP. Se recomienda hacer un ajuste mecánico del equipo y calibrar inmediatamente. Use el intervalo de calibración recomendado por el fabricante."

            elif ((error) < limite_superior) and (error) > limite_inferior:
                intervalo_recomendado = intervalo_anterior * 1.5
                nueva_fecha = fecha_final_global + timedelta(days=(intervalo_recomendado * 365.25))
                recomendacion = "Ampliar el intervalo en 50%"
            else:
                intervalo_recomendado = intervalo_anterior * 0.5
                nueva_fecha = fecha_final_global + timedelta(days=(intervalo_recomendado * 365.25))
                recomendacion = "Reducir el intervalo en 50%"

            # Layout
            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("Resultado")
                st.write(f"**Error medio:** {error:.5f} mm")
                st.write(f"**Límite de control superior (EMP*80%):** {limite_superior:.5f} mm")
                st.write(f"**Límite de control inferior (–EMP*80%):** {limite_inferior:.5f} mm")
                st.write(f"**Intervalo anterior:** {intervalo_anterior:.2f} años")
                if intervalo_recomendado == 0:
                    st.write(f"**Recomendación:** {recomendacion}")
                else:
                    st.write(f"**Recomendación:** {recomendacion}")
                    st.write(f"**Intervalo recomendado:** {intervalo_recomendado:.2f} años")
                    st.write(f"La fecha recomendada para la próxima calibración es: {nueva_fecha.strftime('%d/%m/%Y')}")

            with col2:
                st.subheader("Visualización")
                fig, ax = plt.subplots()
                ax.axhline(limite_superior, color='orange', linestyle='--', label='Límite Superior (EMP * 80%)')
                ax.axhline(limite_inferior, color='orange', linestyle='--', label='Límite Inferior (-EMP * 80%)')
                ax.axhline(error_max, color='gray', linestyle='--', label='+EMP')
                ax.axhline(-error_max, color='gray', linestyle='--', label='-EMP')
                ax.plot([0], [error], marker='o', markersize=10, color='blue', label='Error medio')

                ax.set_xticks([0])
                ax.set_xticklabels(["Error medio"])
                ax.set_ylim(-error_max * 1.2, error_max * 1.2)
                ax.set_ylabel("Límites de control [mm]")
                ax.set_title("Evaluación por Método de Escalera")
                ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=2)
                st.pyplot(fig)

# ------------------------------------------------------------------------------------------------------------

elif metodo == "Cartas de Control":
    st.title("Método de Cartas de Control")
    st.sidebar.subheader("Datos para método de cartas de control")

    ajuste = st.sidebar.selectbox("¿El equipo actualmente se ajustó?", ["No", "Sí"])

    if ajuste == "No":

        num_puntos = st.sidebar.number_input("Cantidad de puntos críticos", min_value=1, value=2)
        if num_puntos <= 0:
            st.error("Debe haber al menos un punto crítico de calibración.")

        num_fechas = st.sidebar.number_input("Cantidad de fechas de calibración", min_value=2, value=2)
        if num_fechas < 2:
            st.error("Debe haber al menos dos períodos registrados para obtener la deriva.")

        if num_puntos > 0 and num_fechas > 1:

            st.sidebar.subheader("Fechas de calibración")

            fechas = []
            for i in range(num_fechas):
                try:
                    fecha = st.sidebar.date_input(
                        f"Fecha {i + 1} de calibración",
                        key=f"fecha_{i}",
                        min_value=datetime.date(1900, 1, 1),
                        max_value=datetime.date(2100, 12, 31)
                    )
                    if not isinstance(fecha, datetime.date):
                        st.error(
                            f"La Fecha {i + 1} no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
                        st.sidebar.caption(
                            "🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
                        st.stop()
                    fechas.append(fecha)
                except Exception:
                    st.error(
                        f"La Fecha {i + 1} no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
                    st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
                    st.stop()

            for i in range(1, len(fechas)):
                if fechas[i] <= fechas[i - 1]:
                    st.error(f"La Fecha {i + 1} debe ser mayor que la Fecha {i}.")
                    st.stop()

            if len(set(fechas)) != len(fechas):
                st.error("Las fechas de calibración no deben repetirse.")
                st.stop()

            tolerancia_global = st.sidebar.number_input(
                "Tolerancia [mm]",
                min_value=0.0,
                format="%.5f",
                value=0.1
            )

            puntos = []
            for p in range(num_puntos):
                st.subheader(f"Punto {p + 1}")

                # Valor nominal
                valor_nominal = st.number_input(
                    f"Valor nominal del Punto {p + 1} [mm]",
                    min_value=0.50,
                    format="%.2f",
                    key=f"nom_{p}"
                )

                if valor_nominal < 0.50:
                    st.error("El mínimo punto de calibración para el equipo es 0,50 mm.")

                if valor_nominal >= 0.50:

                    # Errores por fecha

                    errores = []
                    for i in range(num_fechas):
                        e = st.number_input(
                            f"Error en {fechas[i]} [mm] - Punto {p + 1}",
                            key=f"e_{p}_{i}",
                            format="%.5f"
                        )
                        errores.append(e)

                    puntos.append({
                        "valor_nominal": valor_nominal,
                        "errores": errores,
                        "tolerancia": tolerancia_global
                    })

            st.subheader("Resultados individuales por punto")
            intervalos = []
            derivas = []
            for p, punto in enumerate(puntos):

                error_inicial = punto["errores"][0]
                error_final = punto["errores"][-1]

                fecha_inicial = fechas[0]
                fecha_final = fechas[-1]
                delta_dias = (fecha_final - fecha_inicial).days
                delta_anios = delta_dias / 365.25  # convertir a años

                if delta_anios == 0:
                    st.error(f"Las fechas para Punto {p + 1} no pueden ser iguales.")
                    continue

                deriva = abs((error_final - error_inicial) / delta_anios)
                intervalo = punto["tolerancia"] / deriva if deriva != 0 else float("inf")

                intervalos.append(intervalo)
                derivas.append(deriva)

                st.markdown(f"**Punto {p + 1} (Nominal: {punto['valor_nominal']:.2f} mm):**")
                st.write(f"- Deriva acumulada: {deriva:.5f} mm/año")
                st.write(f"- Tolerancia: {punto['tolerancia']:.5f} mm")
                st.write(
                    f"- Intervalo recomendado para el punto {punto['valor_nominal']:.2f} mm: {intervalo:.2f} años. ")

            inter_min = sorted(intervalos)[0]
            deriva_max = max(derivas)
            fecha_inicial_global = fechas[0]
            fecha_final_global = fechas[-1]
            delta_dias_global = (fecha_final_global - fecha_inicial_global).days
            delta_anios_global = delta_dias_global / 365.25

            st.subheader("Resultado final")

            if deriva_max > tolerancia_global:
                nuevo_intervalo = 0  # evitar valores negativos
                st.warning("IMPORTANTE: la deriva acumulada es mayor o igual al 80% de la tolerancia.")
                st.write(f"Se recomienda hacer un ajuste mecánico del equipo y calibrar inmediatamente.")
                st.write(f"Para la próxima calibración use el intervalo de calibración recomendado por el fabricante.")

            elif deriva_max >= 0.8 * tolerancia_global and delta_anios_global >= 0.8 * inter_min:
                nuevo_intervalo = inter_min - delta_anios_global
                if nuevo_intervalo <= 0:
                    nuevo_intervalo = 0  # evitar valores negativos
                    st.warning(
                        "IMPORTANTE: la deriva acumulada es mayor o igual al 80% de la tolerancia y el tiempo que ha derivado es mayor o igual al 80% del intervalo de calibración cálculado por este método ya que no se han hecho ajustes. "
                        "No ajustar aumenta el riesgo de que la deriva sobrepase la tolerancia.")
                    st.write(f"Intervalo recomendado para el equipo: {nuevo_intervalo:.2f} años")
                    st.write(f"Se recomienda hacer un ajuste mecánico del equipo y calibrar inmediatamente.")
                else:

                    if math.isinf(nuevo_intervalo):
                        st.warning(
                            "No hubo deriva entre las fechas. No se puede estimar una fecha de próxima calibración, use el intervalo recomendado por el fabricante.")
                    else:
                        st.write(f"El intervalo recomendado para el equipo sería: {inter_min:.2f} años.")
                        st.warning(
                            "IMPORTANTE: la deriva acumulada es mayor o igual al 80% de la tolerancia y el tiempo que ha derivado es mayor o igual al 80% del intervalo de calibración cálculado por este método ya que no se han hecho ajustes. "
                            "Utilizar este intervalo aumenta el riesgo de que la deriva sobrepase la tolerancia, por eso se ajusta restando el tiempo transcurrido.")

                        dias_intervalo = int(nuevo_intervalo * 365.25)
                        fecha_proxima = fecha_final_global + timedelta(days=dias_intervalo)
                        st.write(
                            f"Entonces el intervalo ajustado recomendado para el equipo es: {nuevo_intervalo:.2f} años")
                        st.write(
                            f"La fecha recomendada para la próxima calibración es: {fecha_proxima.strftime('%d/%m/%Y')}")
                        st.write(
                            f"Además, como el quipo ya tiene una deriva mayor o igual al 80% de la tolerancia, se recomienda tambien hacer un ajuste mecánico del equipo.")

            elif deriva_max >= 0.8 * tolerancia_global and delta_anios_global < 0.8 * inter_min:

                if math.isinf(inter_min):
                    st.warning(
                        "No hubo deriva entre las fechas. No se puede estimar una fecha de próxima calibración, use el intervalo recomendado por el fabricante.")
                else:
                    st.write(f"Intervalo recomendado para el equipo: {inter_min:.2f} años")
                    dias_intervalo = int(inter_min * 365.25)
                    fecha_proxima = fecha_final_global + timedelta(days=dias_intervalo)
                    st.write(
                        f"La fecha recomendada para la próxima calibración es: {fecha_proxima.strftime('%d/%m/%Y')}")
                    st.write(
                        f"Además, el quipo ya tiene una deriva mayor o igual al 80% de la tolerancia, se recomienda tambien hacer un ajuste mecánico del equipo.")

            elif deriva_max < 0.8 * tolerancia_global and delta_anios_global >= 0.8 * inter_min:

                if math.isinf(inter_min):
                    st.warning(
                        "No hubo deriva entre las fechas. No se puede estimar una fecha de próxima calibración, use el intervalo recomendado por el fabricante.")
                else:

                    st.write(f"Intervalo recomendado para el equipo: {inter_min:.2f} años")
                    dias_intervalo = int(inter_min * 365.25)
                    fecha_proxima = fecha_final_global + timedelta(days=dias_intervalo)
                    st.write(
                        f"La fecha recomendada para la próxima calibración es: {fecha_proxima.strftime('%d/%m/%Y')}")

            else:

                if math.isinf(inter_min):
                    st.warning(
                        "No hubo deriva entre las fechas. No se puede estimar una fecha de próxima calibración, use el intervalo recomendado por el fabricante.")
                else:
                    st.write(f"Intervalo recomendado para el equipo: {inter_min:.2f} años")
                    dias_intervalo = int(inter_min * 365.25)
                    fecha_proxima = fecha_final_global + timedelta(days=dias_intervalo)
                    st.write(
                        f"La fecha recomendada para la próxima calibración es: {fecha_proxima.strftime('%d/%m/%Y')}")
    else:
        try:
            fecha_ajuste = st.sidebar.date_input(
                "Fecha con ajuste",
                value=datetime.date(2000, 1, 1),
                key="fecha_ajuste",
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date(2100, 12, 31)
            )
            if not isinstance(fecha_ajuste, datetime.date):
                st.error(
                    f"La Fecha de ajuste no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
                st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
                st.stop()

        except Exception:
            st.error(
                f"La Fecha de ajuste no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
            st.sidebar.caption("🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
            st.stop()

        if fecha_ajuste == datetime.date.today():
            st.error(
                "Se recomienda utilizar el último intervalo de calibración utilizado o el recomendado por el fabricante.")
        else:
            num_puntos = st.sidebar.number_input("Cantidad de puntos críticos", min_value=1, value=2)
            if num_puntos <= 0:
                st.error("Debe haber al menos un punto crítico de calibración.")

            num_fechas = st.sidebar.number_input("Cantidad de fechas de calibración", min_value=2, value=2)
            if num_fechas <= 1:
                st.error("Debe haber al menos dos períodos registrados para obtener la deriva.")

            if num_puntos > 0 and num_fechas > 1:

                st.sidebar.subheader("Fechas de calibración")

                fechas = [fecha_ajuste]
                st.sidebar.write(f"Fecha 1 (ajuste): {fecha_ajuste.strftime('%d/%m/%Y')}")
                # Los demás registros se ingresan como fechas posteriores al ajuste
                for i in range(1, num_fechas):
                    try:
                        fecha_i = st.sidebar.date_input(
                            f"Fecha {i + 1} de calibración",
                            key=f"fecha_{i}",
                            min_value=fechas[i - 1] + timedelta(days=1),
                            max_value=datetime.date(2100, 12, 31)
                        )
                        if not isinstance(fecha_i, datetime.date):
                            st.error(
                                f"La Fecha {i + 1} no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
                            st.sidebar.caption(
                                "🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
                            st.stop()
                        fechas.append(fecha_i)

                    except Exception:
                        st.error(
                            f"La Fecha {i + 1} no es válida. Debe seleccionar una fecha con formato AAAA/MM/DD o YYYY/MM/DD.")
                        st.sidebar.caption(
                            "🗓️ Seleccione la fecha desde el calendario. No escriba números manualmente.")
                        st.stop()

                # Validaciones: orden y unicidad
                for i in range(1, len(fechas)):
                    if fechas[i] <= fechas[i - 1]:
                        st.error(f"La Fecha {i + 1} debe ser mayor que la Fecha {i}.")
                        st.stop()

                if len(set(fechas)) != len(fechas):
                    st.error("Las fechas de calibración no deben repetirse.")
                    st.stop()

                tolerancia_global = st.sidebar.number_input(
                    "Tolerancia [mm]",
                    min_value=0.0,
                    format="%.5f",
                    value=0.1
                )
                puntos = []
                for p in range(num_puntos):
                    st.subheader(f"Punto {p + 1}")

                    # Valor nominal
                    valor_nominal = st.number_input(
                        f"Valor nominal del Punto {p + 1} [mm]",
                        min_value=0.50,
                        format="%.2f",
                        key=f"nom_{p}"
                    )

                    if valor_nominal < 0.50:
                        st.error("El mínimo punto de calibración para el equipo es 0,50 mm.")

                    if valor_nominal >= 0.50:

                        # Errores por año
                        errores = []
                        for i in range(num_fechas):
                            if i == 0:
                                st.write(
                                    f"Error en {fechas[i].strftime('%d/%m/%Y')} [mm] - Punto {p + 1}: 0.00000 (ajuste)")
                                errores.append(0.0)
                            else:
                                e = st.number_input(
                                    f"Error en {fechas[i].strftime('%d/%m/%Y')} [mm] - Punto {p + 1}",
                                    key=f"e_{p}_{i}",
                                    format="%.5f"
                                )
                                errores.append(e)

                        puntos.append({
                            "valor_nominal": valor_nominal,
                            "errores": errores,
                            "tolerancia": tolerancia_global
                        })

                st.subheader("Resultados individuales por punto")
                intervalos = []
                derivas = []
                for p, punto in enumerate(puntos):

                    error_inicial = punto["errores"][0]
                    error_final = punto["errores"][-1]

                    fecha_inicial = fechas[0]
                    fecha_final = fechas[-1]
                    delta_dias = (fecha_final - fecha_inicial).days
                    delta_anios = delta_dias / 365.25  # más preciso

                    if delta_anios == 0:
                        st.error(f"Las fechas para Punto {p + 1} no pueden ser iguales.")
                        continue

                    deriva = abs((error_final - error_inicial) / delta_anios)
                    intervalo = punto["tolerancia"] / deriva if deriva != 0 else float("inf")

                    intervalos.append(intervalo)
                    derivas.append(deriva)
                    st.markdown(f"**Punto {p + 1} (Nominal: {punto['valor_nominal']:.2f} mm):**")
                    st.write(f"- Deriva acumulada: {deriva:.5f} mm/año")
                    st.write(f"- Tolerancia: {punto['tolerancia']:.5f} mm")
                    st.write(
                        f"- Intervalo recomendado para el punto {punto['valor_nominal']:.2f} mm: {intervalo:.2f} años. ")

                inter_min = sorted(intervalos)[0]
                deriva_max = max(derivas)
                fecha_inicial_global = fechas[0]
                fecha_final_global = fechas[-1]
                delta_dias_global = (fecha_final_global - fecha_inicial_global).days
                delta_anios_global = delta_dias_global / 365.25

                st.subheader("Resultado final")

                if deriva_max > tolerancia_global:
                    nuevo_intervalo = 0  # evitar valores negativos
                    st.warning("IMPORTANTE: la deriva acumulada es mayor que la tolerancia.")
                    st.write(f"Se recomienda hacer un ajuste mecánico del equipo y calibrar inmediatamente.")
                    st.write(
                        f"Para la próxima calibración use el intervalo de calibración recomendado por el fabricante.")

                elif (deriva_max >= 0.8 * tolerancia_global) and (
                        deriva_max < tolerancia_global) and delta_anios_global >= 0.8 * inter_min:
                    nuevo_intervalo = inter_min - delta_anios_global
                    if nuevo_intervalo <= 0:
                        nuevo_intervalo = 0  # evitar valores negativos
                        st.warning(
                            "IMPORTANTE: la deriva acumulada es mayor o igual al 80% de la tolerancia y el tiempo que ha derivado es mayor o igual al 80% del intervalo de calibración cálculado por este método ya que no se han hecho ajustes. "
                            "No ajustar aumenta el riesgo de que la deriva sobrepase la tolerancia.")
                        st.write(f"Intervalo recomendado para el equipo: {nuevo_intervalo:.2f} años")
                        st.write(f"Se recomienda hacer un ajuste mecánico del equipo y calibrar inmediatamente.")
                        st.write(
                            f"Para la próxima calibración use el intervalo de calibración recomendado por el fabricante.")
                    else:

                        if math.isinf(nuevo_intervalo):
                            st.warning(
                                "No hubo deriva entre las fechas. No se puede estimar una fecha de próxima calibración, use el intervalo recomendado por el fabricante.")
                        else:
                            st.write(f"El intervalo recomendado para el equipo sería: {inter_min:.2f} años.")
                            st.warning(
                                "IMPORTANTE: la deriva acumulada es mayor o igual al 80% de la tolerancia y el tiempo que ha derivado es mayor o igual al 80% del intervalo de calibración cálculado por este método ya que no se han hecho ajustes. "
                                "Utilizar este intervalo aumenta el riesgo de que la deriva sobrepase la tolerancia, por eso se ajusta restando el tiempo transcurrido.")

                            dias_intervalo = int(nuevo_intervalo * 365.25)
                            fecha_proxima = fecha_final_global + timedelta(days=dias_intervalo)
                            st.write(
                                f"Entonces el intervalo ajustado recomendado para el equipo es: {nuevo_intervalo:.2f} años")
                            st.write(
                                f"La fecha recomendada para la próxima calibración es: {fecha_proxima.strftime('%d/%m/%Y')}")
                            st.write(
                                f"Además, como el quipo ya tiene una deriva mayor o igual al 80% de la tolerancia, se recomienda tambien hacer un ajuste mecánico del equipo.")

                elif deriva_max >= 0.8 * tolerancia_global and delta_anios_global < 0.8 * inter_min:

                    if math.isinf(inter_min):
                        st.warning(
                            "No hubo deriva entre las fechas. No se puede estimar una fecha de próxima calibración, use el intervalo recomendado por el fabricante.")
                    else:
                        st.write(f"Intervalo recomendado para el equipo: {inter_min:.2f} años")
                        dias_intervalo = int(inter_min * 365.25)
                        fecha_proxima = fecha_final_global + timedelta(days=dias_intervalo)
                        st.write(
                            f"La fecha recomendada para la próxima calibración es: {fecha_proxima.strftime('%d/%m/%Y')}")
                        st.write(
                            f"Además, el quipo ya tiene una deriva mayor o igual al 80% de la tolerancia, se recomienda tambien hacer un ajuste mecánico del equipo.")

                elif deriva_max < 0.8 * tolerancia_global and delta_anios_global >= 0.8 * inter_min:

                    if math.isinf(inter_min):
                        st.warning(
                            "No hubo deriva entre las fechas. No se puede estimar una fecha de próxima calibración, use el intervalo recomendado por el fabricante.")
                    else:

                        st.write(f"Intervalo recomendado para el equipo: {inter_min:.2f} años")
                        dias_intervalo = int(inter_min * 365.25)
                        fecha_proxima = fecha_final_global + timedelta(days=dias_intervalo)
                        st.write(
                            f"La fecha recomendada para la próxima calibración es: {fecha_proxima.strftime('%d/%m/%Y')}")

                else:

                    if math.isinf(inter_min):
                        st.warning(
                            "No hubo deriva entre las fechas. No se puede estimar una fecha de próxima calibración, use el intervalo recomendado por el fabricante.")
                    else:
                        st.write(f"Intervalo recomendado para el equipo: {inter_min:.2f} años")
                        dias_intervalo = int(inter_min * 365.25)
                        fecha_proxima = fecha_final_global + timedelta(days=dias_intervalo)
                        st.write(
                            f"La fecha recomendada para la próxima calibración es: {fecha_proxima.strftime('%d/%m/%Y')}")