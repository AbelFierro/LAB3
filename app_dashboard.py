import streamlit as st
import pandas as pd
import altair as alt
import numpy as np 

# --- CONFIGURACIÓN DE PÁGINA (DEBE SER EL PRIMER COMANDO DE STREAMLIT) ---
st.set_page_config(layout="wide")

# --- PASO 0: CARGAR DATOS REALES ---
@st.cache_data # Cachea la carga de datos
def cargar_datos_reales(ruta_archivo):
    try:
        df = pd.read_csv(ruta_archivo, index_col=0, encoding='latin1')
        # Asegurar tipos de datos consistentes para columnas de ID y atributos
        # que se usarán en filtros categóricos.
        cols_to_object = ['customer_id', 'product_id', 'cat1', 'cat2', 'cat3', 'brand', 'sku_size']
        for col in cols_to_object:
            if col in df.columns:
                df[col] = df[col].astype(str) # Convertir a string para manejo categórico uniforme
            else:
                # Si una columna de atributo principal no existe, la creamos vacía (como string)
                # para evitar errores posteriores, aunque esto es menos ideal que tenerla en el CSV.
                st.warning(f"Advertencia al cargar CSV: Columna '{col}' no encontrada. Se creará como vacía.")
                df[col] = pd.Series(dtype='object')


        # Verificar la columna 'periodo'
        if 'periodo' not in df.columns:
            st.error("La columna 'periodo' es esencial y no se encuentra en el CSV. Por favor, revisa tu archivo.")
            st.stop()
        if 'tn' not in df.columns:
            st.error("La columna 'tn' es esencial y no se encuentra en el CSV. Por favor, revisa tu archivo.")
            st.stop()
            
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo en la ruta: '{ruta_archivo}'.")
        st.info("Asegúrate de que el archivo CSV esté en la ubicación correcta o corrige la ruta.")
        st.stop()
    except UnicodeDecodeError: # Manejar específicamente el error de decodificación
        st.error(f"Error de codificación al leer '{ruta_archivo}'. El archivo podría no estar en 'latin1' o estar corrupto.")
        st.info("Verifica la codificación con la que se guardó el archivo. Se intentó leer con 'latin1'.")
        st.stop()    
    except Exception as e:
        st.error(f"Ocurrió un error al cargar '{ruta_archivo}': {e}")
        st.stop()

# Cambia 'data/df_sin.csv' por la ruta real a tu archivo si es diferente.
# Si tu archivo se llama 'archivo_maestro.csv' y está en 'archivos_maestros/':
df_sin = cargar_datos_reales('archivos_maestros/a_m_filtrado_prod_a_pred.csv') # <--- ¡USA TU RUTA AQUÍ!

st.title('Dashboard Interactivo de Ventas (TN)')

# --- PASO 1: PREPARAR DATOS AGREGADOS INICIALES (cacheado para eficiencia) ---
@st.cache_data
def preparar_datos_agregados(df_input):
    df_working = df_input.copy()

    # Las columnas de atributos ya deberían ser string por la función de carga.
    product_attribute_cols = ['product_id', 'cat1', 'cat2', 'cat3', 'brand', 'sku_size']
    df_product_attributes = pd.DataFrame()
    
    actual_product_attribute_cols = ['product_id']
    for col in product_attribute_cols[1:]:
        if col in df_working.columns:
            actual_product_attribute_cols.append(col)
            
    if len(actual_product_attribute_cols) > 1:
         # Asegurarse que no haya NaNs en product_id antes de drop_duplicates
        df_working_for_attrs = df_working[actual_product_attribute_cols].dropna(subset=['product_id'])
        df_product_attributes = df_working_for_attrs.drop_duplicates(subset=['product_id'])


    grouping_cols = ['periodo', 'product_id', 'customer_id']
    # Ya verificamos que estas columnas existen en cargar_datos_reales

    df_sum_intermediate = df_working.groupby(grouping_cols, as_index=False)['tn'].sum()

    if not df_product_attributes.empty:
        df_processed = pd.merge(df_sum_intermediate, df_product_attributes, on='product_id', how='left')
    else: # Si solo tenemos product_id como atributo
        df_processed = df_sum_intermediate
        # Rellenar otras columnas de atributos esperadas si no se pudieron unir
        for col in product_attribute_cols[1:]:
            if col not in df_processed.columns:
                df_processed[col] = "Desconocido" # O algún valor por defecto

    try:
        df_processed['periodo'] = pd.to_datetime(df_processed['periodo'].astype(str), format='%Y%m')
    except Exception as e:
        st.error(f"Error al convertir la columna 'periodo' a fecha: {e}")
        st.info("Asegúrate de que la columna 'periodo' en tu CSV esté en formato YYYYMM (ej. 201701).")
        st.stop()
        
    df_processed.dropna(subset=['periodo', 'tn'], inplace=True)
    return df_processed

df_agg_inicial = preparar_datos_agregados(df_sin)

# --- PASO 2: FILTROS EN LA BARRA LATERAL (SIDEBAR) ---
st.sidebar.header('Filtros')

# Filtro de Rango de Fechas
df_filtrado_streamlit = df_agg_inicial.copy()

if not df_agg_inicial.empty and 'periodo' in df_agg_inicial.columns and not df_agg_inicial['periodo'].dropna().empty:
    min_fecha_datos = df_agg_inicial['periodo'].min().date()
    max_fecha_datos = df_agg_inicial['periodo'].max().date()
    
    valor_inicial_fecha_inicio = min_fecha_datos
    valor_inicial_fecha_fin = max_fecha_datos

    if pd.isna(valor_inicial_fecha_inicio): valor_inicial_fecha_inicio = pd.Timestamp('today').date() - pd.DateOffset(years=1)
    if pd.isna(valor_inicial_fecha_fin): valor_inicial_fecha_fin = pd.Timestamp('today').date()
    if valor_inicial_fecha_inicio > valor_inicial_fecha_fin : valor_inicial_fecha_inicio = valor_inicial_fecha_fin

    fecha_inicio = st.sidebar.date_input('Fecha Inicio:', 
                                         value=valor_inicial_fecha_inicio, 
                                         min_value=min_fecha_datos if not pd.isna(min_fecha_datos) else valor_inicial_fecha_inicio, 
                                         max_value=max_fecha_datos if not pd.isna(max_fecha_datos) else valor_inicial_fecha_fin,
                                         key='fecha_inicio')
    fecha_fin = st.sidebar.date_input('Fecha Fin:', 
                                      value=valor_inicial_fecha_fin, 
                                      min_value=min_fecha_datos if not pd.isna(min_fecha_datos) else valor_inicial_fecha_inicio, 
                                      max_value=max_fecha_datos if not pd.isna(max_fecha_datos) else valor_inicial_fecha_fin,
                                      key='fecha_fin')

    if fecha_inicio and fecha_fin:
        if fecha_inicio > fecha_fin:
            st.sidebar.error('Error: La fecha de inicio no puede ser posterior a la fecha de fin.')
        else:
            df_filtrado_streamlit = df_agg_inicial[
                (df_agg_inicial['periodo'] >= pd.to_datetime(fecha_inicio)) &
                (df_agg_inicial['periodo'] <= pd.to_datetime(fecha_fin))
            ]
else:
    st.sidebar.warning("No hay datos de 'periodo' para filtrar por fecha.")


# Filtros Desplegables en Cascada
ALL_OPTION_LABEL = "--- Todos ---"

ordered_filter_cols = {
    'customer_id': 'Cliente:',
    'cat1': 'Categoría 1:',
    'cat2': 'Categoría 2:',
    'cat3': 'Categoría 3:',
    'brand': 'Marca (Brand):',
    'sku_size': 'Tamaño SKU:',
    'product_id': 'Producto ID:'
}

df_para_opciones = df_filtrado_streamlit.copy()

for col_name, display_label in ordered_filter_cols.items():
    if col_name in df_para_opciones.columns and not df_para_opciones.empty:
        # Las columnas ya deberían ser string desde la carga o preparación.
        # Nos aseguramos que no haya NaN antes de unique() para las opciones.
        opciones_disponibles = sorted(df_para_opciones[col_name].dropna().unique().tolist())
        opciones = [ALL_OPTION_LABEL] + opciones_disponibles
        
        if len(opciones) > 1:
            # Usar st.session_state para mantener la selección si las opciones cambian pero la selección sigue válida
            default_index = 0
            session_key = f'select_{col_name}_value'
            if session_key in st.session_state and st.session_state[session_key] in opciones:
                default_index = opciones.index(st.session_state[session_key])

            seleccion = st.sidebar.selectbox(display_label, 
                                             options=opciones, 
                                             index=default_index, # Para intentar mantener la selección
                                             key=f'select_{col_name}')
            st.session_state[session_key] = seleccion # Guardar la selección actual

            if seleccion != ALL_OPTION_LABEL:
                df_filtrado_streamlit = df_filtrado_streamlit[df_filtrado_streamlit[col_name] == seleccion]
                df_para_opciones = df_para_opciones[df_para_opciones[col_name] == seleccion]
    elif col_name not in df_para_opciones.columns:
         st.sidebar.warning(f"Columna '{col_name}' no disponible para filtrar en los datos actuales.")


# --- PASO 3: MOSTRAR DATOS FILTRADOS Y GRÁFICO ---
st.subheader(f'Mostrando {len(df_filtrado_streamlit)} filas de datos filtrados (máx. 20 en tabla)')
if not df_filtrado_streamlit.empty:
    st.dataframe(df_filtrado_streamlit.head(20))
else:
    st.warning("No hay datos para mostrar con los filtros seleccionados.")

st.subheader('Gráfico de Ventas (TN)')

# ESTRATEGIA PARA DATOS GRANDES: MUESTREO ANTES DE GRAFICAR
MAX_ROWS_FOR_CHART = 4000 # Límite de filas para pasar a Altair directamente
df_para_grafico = df_filtrado_streamlit

if len(df_filtrado_streamlit) > MAX_ROWS_FOR_CHART:
    st.warning(f"Los datos filtrados ({len(df_filtrado_streamlit)} filas) son muchos para graficar interactivamente de forma óptima. Se mostrará una muestra aleatoria de {MAX_ROWS_FOR_CHART} filas en el gráfico.")
    df_para_grafico = df_filtrado_streamlit.sample(n=MAX_ROWS_FOR_CHART, random_state=42)


if not df_para_grafico.empty:
    # Quitar alt.data_transformers.disable_max_rows() globalmente
    # Permitir que Altair use sus transformadores por defecto si es necesario (aunque aquí ya muestreamos)
    # alt.data_transformers.enable('default') # Opcional, ya que hemos muestreado

    chart = alt.Chart(df_para_grafico).mark_bar().encode(
        x=alt.X('periodo:T', title='Periodo', axis=alt.Axis(format='%Y-%m')),
        y=alt.Y('sum(tn):Q', title='TN (Toneladas)'),
        color=alt.Color('product_id:N', title='Producto ID'),
        tooltip=[ # Tooltip simplificado para reducir tamaño
            alt.Tooltip('periodo:T', format='%Y-%m', title='Periodo'),
            alt.Tooltip('product_id:N', title='Producto'),
            # alt.Tooltip('customer_id:N', title='Customer ID'), # Comentado para reducir tamaño
            alt.Tooltip('sum(tn):Q', title='TN Total Seleccionado'),
            # alt.Tooltip('cat1:N', title='Cat1'), # Comentado
            # alt.Tooltip('brand:N', title='Marca') # Comentado
        ]
    ).properties(
        height=450
    ).interactive() # Añadir interactividad básica al gráfico como zoom y pan

    st.altair_chart(chart, use_container_width=True)
elif not df_filtrado_streamlit.empty and df_para_grafico.empty:
    st.info("La muestra de datos para el gráfico resultó vacía (esto es poco común si MAX_ROWS_FOR_CHART > 0).")
else:
    st.info("El gráfico está vacío porque no hay datos que coincidan con los filtros seleccionados.")

