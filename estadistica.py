import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Dashboard Estadístico", layout="wide")

st.title("Estadística - Datos agrupados")
st.markdown("Ingresa tus clases, límites y frecuencias.")

# config
with st.sidebar:
    st.header("⚙️ Configuración")
    num_clases = st.number_input("Número de Clases", min_value=1, max_value=20, value=5, step=1)
    tipo_datos = st.radio("Cálculo de Varianza", ["Muestra (n-1)", "Población (n)"])

st.subheader("1. Entrada de Datos")
st.caption("Llena la tabla con tus intervalos y frecuencias absolutas.")

# inicializar datframe
if "df_input" not in st.session_state or len(st.session_state.df_input) != num_clases:
    st.session_state.df_input = pd.DataFrame({
        "Límite Inferior": [0.0] * num_clases,
        "Límite Superior": [0.0] * num_clases,
        "Frecuencia (fi)": [0.0] * num_clases
    })

# editor de datos
df_editor = st.data_editor(
    st.session_state.df_input,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True
)

if st.button("Calcular y generar gráficas", type="primary"):
    # listas
    lim_inf = df_editor["Límite Inferior"].tolist()
    lim_sup = df_editor["Límite Superior"].tolist()
    frec_abs = df_editor["Frecuencia (fi)"].tolist()
    
    n = round(sum(frec_abs), 2)
    
    if n == 0:
        st.error("La suma de las frecuencias no puede ser cero.")
        st.stop()
        
    num_clases_actual = len(lim_inf)
    
    # mate
    marcas_clase = []
    frec_acum = []
    frec_rel = []
    xi_fi = []
    
    acum = 0
    for i in range(num_clases_actual):
        # xi
        suma_lims = round(lim_inf[i] + lim_sup[i], 2)
        mc = round(suma_lims / 2, 2)
        marcas_clase.append(mc)
        
        # Fi
        acum = round(acum + frec_abs[i], 2)
        frec_acum.append(acum)
        
        # hi
        rel = round(frec_abs[i] / n, 2)
        frec_rel.append(rel)
        
        # xi * fi
        xf = round(mc * frec_abs[i], 2)
        xi_fi.append(xf)
        
    # calculos estadisticos
    suma_xi_fi = round(sum(xi_fi), 2)
    media = round(suma_xi_fi / n, 2)
    
    # Me
    pos_mediana = round(n / 2, 2)
    clase_mediana_idx = 0
    for i in range(num_clases_actual):
        if frec_acum[i] >= pos_mediana:
            clase_mediana_idx = i
            break
            
    li_med = lim_inf[clase_mediana_idx]
    f_med = frec_abs[clase_mediana_idx]
    F_ant_med = frec_acum[clase_mediana_idx - 1] if clase_mediana_idx > 0 else 0
    amplitud_med = round(lim_sup[clase_mediana_idx] - li_med, 2)
    
    fraccion = (pos_mediana - F_ant_med) / f_med if f_med != 0 else 0
    mediana = round(li_med + (fraccion * amplitud_med), 2)
    
    # Mo
    max_frec = max(frec_abs)
    clase_moda_idx = frec_abs.index(max_frec)
    li_mod = lim_inf[clase_moda_idx]
    f_mod = frec_abs[clase_moda_idx]
    f_ant_mod = frec_abs[clase_moda_idx - 1] if clase_moda_idx > 0 else 0
    f_sig_mod = frec_abs[clase_moda_idx + 1] if clase_moda_idx < num_clases_actual - 1 else 0
    amplitud_mod = round(lim_sup[clase_moda_idx] - li_mod, 2)
    
    d1 = round(f_mod - f_ant_mod, 2)
    d2 = round(f_mod - f_sig_mod, 2)
    suma_d = round(d1 + d2, 2)
    
    div_mod = round(d1 / suma_d, 2) if suma_d != 0 else 0
    moda = round(li_mod + round(div_mod * amplitud_mod, 2), 2)
    
    # varianza y desviación (calculos)
    var_list = []
    for i in range(num_clases_actual):
        resta = round(marcas_clase[i] - media, 2)
        cuadrado = round(resta ** 2, 2)
        prod = round(cuadrado * frec_abs[i], 2)
        var_list.append(prod)
        
    suma_var = round(sum(var_list), 2)
    divisor_var = (n - 1) if "Muestra" in tipo_datos else n
    varianza = round(suma_var / divisor_var, 2)
    desviacion = round(varianza ** 0.5, 2)
    
    st.divider()
    st.subheader("2. Resultados Estadísticos")
    
    # resultados resultados
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Media", media)
    col2.metric("Mediana", mediana)
    col3.metric("Moda", moda)
    col4.metric(f"Varianza ({'s²' if 'Muestra' in tipo_datos else 'σ²'})", varianza)
    col5.metric(f"Desviación ({'s' if 'Muestra' in tipo_datos else 'σ'})", desviacion)
    
    # tabla final
    st.markdown("#### Tabla de Frecuencias Completa")
    df_resultados = pd.DataFrame({
        "Intervalo": [f"[{lim_inf[i]}, {lim_sup[i]}{']' if i == num_clases_actual-1 else ')'}" for i in range(num_clases_actual)],
        "xi": marcas_clase,
        "fi": frec_abs,
        "Fi": frec_acum,
        "hi": frec_rel,
        "xi*fi": xi_fi,
        "(xi-x̄)²*fi": var_list
    })
    st.dataframe(df_resultados, use_container_width=True)
    
    # graficas ploty
    st.divider()
    st.subheader("3. Dashboard Visual")
    
    c1, c2 = st.columns(2)
    
    # histograma
    anchos = [round(lim_sup[i] - lim_inf[i], 2) for i in range(num_clases_actual)]
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Bar(
        x=df_resultados["Intervalo"],
        y=frec_abs,
        marker_color='#2C3E50',
        marker_line_color='black',
        marker_line_width=1.5
    ))
    fig_hist.update_layout(title="Histograma de Frecuencias", bargap=0, xaxis_title="Intervalos", yaxis_title="Frecuencia")
    c1.plotly_chart(fig_hist, use_container_width=True)
    
    # poligono
    ancho_promedio = anchos[0]
    x_poly = [round(marcas_clase[0] - ancho_promedio, 2)] + marcas_clase + [round(marcas_clase[-1] + ancho_promedio, 2)]
    y_poly = [0] + frec_abs + [0]
    
    fig_poly = go.Figure()
    fig_poly.add_trace(go.Scatter(
        x=x_poly, y=y_poly, 
        mode='lines+markers', 
        fill='tozeroy', 
        marker=dict(size=8, color='#E74C3C'),
        line=dict(width=3, color='#E74C3C')
    ))
    fig_poly.update_layout(title="Polígono de Frecuencias", xaxis_title="Marcas de Clase", yaxis_title="Frecuencia")
    c2.plotly_chart(fig_poly, use_container_width=True)
    
    # ojiva
    x_ojiva = [lim_inf[0]] + lim_sup
    y_ojiva = [0] + frec_acum
    
    fig_ojiva = go.Figure()
    fig_ojiva.add_trace(go.Scatter(
        x=x_ojiva, y=y_ojiva, 
        mode='lines+markers', 
        marker=dict(size=8, color='#27AE60'),
        line=dict(width=3, color='#27AE60')
    ))
    fig_ojiva.update_layout(title="Ojiva (Frecuencias Acumuladas)", xaxis_title="Límites Superiores", yaxis_title="Frecuencia Acumulada")
    c1.plotly_chart(fig_ojiva, use_container_width=True)
    
    # pastel
    fig_pie = go.Figure(data=[go.Pie(
        labels=df_resultados["Intervalo"], 
        values=frec_rel, 
        hole=.3,
        textinfo='label+percent',
        marker_colors=['#A9CCE3', '#F9E79F', '#A2D9CE', '#F5B041', '#D7BDE2', '#F1948A', '#E5E7E9']
    )])
    fig_pie.update_layout(title="Proporción de Frecuencias")
    c2.plotly_chart(fig_pie, use_container_width=True)