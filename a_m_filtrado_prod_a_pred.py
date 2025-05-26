import numpy as np 
import pandas as pd 
import os

def guardar_dataframe_a_csv(dataframe, nombre_archivo_csv, incluir_indice=False, codificacion='utf-8'):
    """
    Guarda un DataFrame de Pandas en un archivo CSV.

    Args:
        dataframe (pd.DataFrame): El DataFrame que quieres guardar.
        nombre_archivo_csv (str): El nombre (y ruta, si es necesario) del archivo CSV a crear.
        incluir_indice (bool, optional): Si es True, incluye el índice del DataFrame en el CSV.
                                         Por defecto es False.
        codificacion (str, optional): La codificación a usar para el archivo CSV.
                                      Por defecto es 'utf-8'.
    """
    try:
        # Asegurarse de que el directorio de salida exista
        directorio_salida = os.path.dirname(nombre_archivo_csv)
        if directorio_salida and not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
            print(f"Directorio creado: {directorio_salida}")

        dataframe.to_csv(nombre_archivo_csv, index=incluir_indice, encoding=codificacion)
        print(f"DataFrame guardado exitosamente como '{nombre_archivo_csv}'")
    except Exception as e:
        print(f"Ocurrió un error al guardar el DataFrame como CSV: {e}")

# --- Configuración de Rutas y Nombres de Archivo ---
# Ajusta pathdata si tus archivos están en una ubicación diferente
# Por ejemplo, si el script está en 'Labo III/' y tus carpetas son 'Labo III/data/' y 'Labo III/archivos_maestros/':

carpeta_datos_maestro = 'archivos_maestros/' # Carpeta para archivo_maestro.csv
carpeta_datos_productos_txt = 'data/'       # Carpeta para productos_a_predecir.txt
pathdata_salida = 'archivos_maestros/' # Asumiendo que quieres guardar la salida aquí

nombre_archivo_maestro = 'archivo_maestro.csv'
nombre_archivo_productos_a_predecir = 'productos_a_predecir.txt' 
nombre_archivo_filtrado_salida = 'a_m_filtrado_prod_a_pred.csv'

# Construir rutas completas
ruta_archivo_maestro = os.path.join(carpeta_datos_maestro, nombre_archivo_maestro)
ruta_productos_a_predecir = os.path.join(carpeta_datos_productos_txt, nombre_archivo_productos_a_predecir)
ruta_archivo_salida_completa = os.path.join(pathdata_salida, nombre_archivo_filtrado_salida)

# --- Carga de Datos ---
try:
    print(f"Cargando archivo maestro desde: {ruta_archivo_maestro}")
   
    df_maestro = pd.read_csv(ruta_archivo_maestro, sep=',') 
    print("Archivo maestro cargado exitosamente.")
    # Asegurar que la columna product_id sea del tipo correcto (int si es posible)
    if 'product_id' in df_maestro.columns:
        # Intentar convertir a int, si falla, mantener como está (podría ser object/string)
        try:
            df_maestro['product_id'] = df_maestro['product_id'].astype(int)
        except ValueError:
            print("Advertencia: No se pudo convertir 'product_id' en archivo_maestro a entero. Se usará como string.")
            df_maestro['product_id'] = df_maestro['product_id'].astype(str)
    else:
        raise ValueError("La columna 'product_id' no se encuentra en archivo_maestro.csv")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo maestro en '{ruta_archivo_maestro}'. Verifica la ruta y el nombre del archivo.")
    exit() # Salir del script si el archivo principal no se encuentra
except Exception as e:
    print(f"Ocurrió un error al cargar '{ruta_archivo_maestro}': {e}")
    exit()

try:
    print(f"Cargando lista de productos a predecir desde: {ruta_productos_a_predecir}")
    # El archivo productos_a_predecir.txt tiene un encabezado 'product_id' y una lista de IDs.
    
    df_productos_a_predecir = pd.read_csv(ruta_productos_a_predecir) 
    print("Lista de productos a predecir cargada exitosamente.")
    
    # Asegurar que la columna product_id sea del tipo correcto y renombrar si es necesario
    if df_productos_a_predecir.columns[0] != 'product_id' and len(df_productos_a_predecir.columns) == 1:
        print(f"Advertencia: La primera columna en '{nombre_archivo_productos_a_predecir}' no se llama 'product_id'. Se asumirá que es la columna de product_id.")
        df_productos_a_predecir.columns = ['product_id']
        
    if 'product_id' in df_productos_a_predecir.columns:
         # Intentar convertir a int, si falla, mantener como está
        try:
            df_productos_a_predecir['product_id'] = df_productos_a_predecir['product_id'].astype(int)
        except ValueError:
            print("Advertencia: No se pudo convertir 'product_id' en productos_a_predecir a entero. Se usará como string.")
            df_productos_a_predecir['product_id'] = df_productos_a_predecir['product_id'].astype(str)
            # Si df_maestro['product_id'] se quedó como int, necesitamos consistencia
            if df_maestro['product_id'].dtype == np.int64:
                 df_maestro['product_id'] = df_maestro['product_id'].astype(str)
                 print("Se convirtió 'product_id' de archivo_maestro a string para consistencia.")

    else:
        raise ValueError(f"La columna 'product_id' no se encuentra en '{nombre_archivo_productos_a_predecir}' o el archivo no tiene el formato esperado.")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo de productos a predecir en '{ruta_productos_a_predecir}'. Verifica la ruta y el nombre del archivo.")
    exit()
except Exception as e:
    print(f"Ocurrió un error al cargar '{nombre_archivo_productos_a_predecir}': {e}")
    exit()

# --- Filtrado de Productos ---
# Asegurar que ambos DataFrames tienen la columna 'product_id' y son del mismo tipo antes de filtrar
if 'product_id' in df_maestro.columns and 'product_id' in df_productos_a_predecir.columns:
    # Convertir la lista de IDs de productos a predecir a un set para una búsqueda más eficiente
    ids_a_predecir = set(df_productos_a_predecir['product_id'])
    
    # Filtrar el DataFrame maestro
    productos_filtrados = df_maestro[df_maestro['product_id'].isin(ids_a_predecir)]
    
    print(f"\nNúmero de filas en archivo maestro original: {len(df_maestro)}")
    print(f"Número de IDs de producto únicos a predecir: {len(ids_a_predecir)}")
    print(f"Número de filas después de filtrar por productos a predecir: {len(productos_filtrados)}")

    # --- Guardar el DataFrame Filtrado ---
    # Usando los parámetros que especificaste: incluir_indice=True, codificacion='latin1'
    guardar_dataframe_a_csv(productos_filtrados, ruta_archivo_salida_completa, incluir_indice=True, codificacion='latin1')

    # --- Mostrar Información del DataFrame Filtrado ---
    print("\nInformación del DataFrame de productos filtrados:")
    productos_filtrados.info()
    print("\nPrimeras 5 filas de productos_filtrados:")
    print(productos_filtrados.head())
else:
    print("Error: La columna 'product_id' no está presente en uno o ambos DataFrames después de la carga.")

