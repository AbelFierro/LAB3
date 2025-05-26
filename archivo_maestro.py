#Import de librerias basicas tablas y matrices
import numpy as np 
import pandas as pd 
import os

pathdata='data/'
filename1 = 'sell-in.txt'
filename2 = 'tb_productos.txt'


filepath = os.path.join(pathdata, filename1)
sell = pd.read_csv(filepath, sep="\t")


filepath = os.path.join(pathdata, filename2)
productos = pd.read_csv(filepath,sep="\t")

#Eliminamos productos duplicados ???
duplicados = productos[productos.duplicated('product_id', keep=False)]
print(duplicados.sort_values('product_id'))

productos_unicos = productos.drop_duplicates('product_id')

df=pd.merge(sell,productos_unicos,on='product_id',how='left')

def guardar_dataframe_a_csv(dataframe, nombre_archivo_csv, incluir_indice=False, codificacion='utf-8'):
    """
    Guarda un DataFrame de Pandas en un archivo CSV.

    Args:
        dataframe (pd.DataFrame): El DataFrame que quieres guardar.
        nombre_archivo_csv (str): El nombre (y ruta, si es necesario) del archivo CSV a crear.
                                  Ejemplo: 'mis_datos.csv' o 'ruta/a/mis_datos.csv'.
        incluir_indice (bool, optional): Si es True, incluye el índice del DataFrame en el CSV.
                                         Por defecto es False.
        codificacion (str, optional): La codificación a usar para el archivo CSV.
                                      Por defecto es 'utf-8'.
    """
    try:
        dataframe.to_csv(nombre_archivo_csv, index=incluir_indice, encoding=codificacion)
        print(f"DataFrame guardado exitosamente como '{nombre_archivo_csv}'")
    except Exception as e:
        print(f"Ocurrió un error al guardar el DataFrame como CSV: {e}")
        

# Para este ejemplo, crearé un df_sin de muestra (REEMPLAZA ESTO CON TU df_sin REAL):

# Nombre que quieres para tu archivo CSV
nombre_del_archivo = 'archivo_maestro.csv'

# Llamar a la función para guardar tu df_sin (usa tu df_sin real aquí)
# Si tu DataFrame se llama df_sin:
# guardar_dataframe_a_csv(df_sin, nombre_del_archivo)

# Para el ejemplo, usaré df_sin_ejemplo:
# guardar_dataframe_a_csv(df_sin, 'df_sin.csv')

# Si quieres guardarlo en una carpeta específica y con otra codificación:
# nombre_con_ruta = 'mi_carpeta/otro_nombre.csv'
guardar_dataframe_a_csv(df, 'archivos_maestros/archivo_maestro.csv', incluir_indice=True, codificacion='latin1')

df.info ()