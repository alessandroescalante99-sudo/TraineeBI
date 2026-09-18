"""
Pipeline ETL:

Extraccion     -> Descargo la base de datos SQLite desde GitHub
Transformacion -> Limpio, Estandarizo y Creo nuevas variables para los datos con pandas
Cargar         -> Exporto el resultado final a un archivo CSV
"""

import os
import sqlite3
import requests
import numpy as np
import pandas as pd

URL_BASE_DATOS = (
    "https://raw.githubusercontent.com/alessandroescalante99-sudo/"
    "Proyecto_Ventas_Rentabilidad/main/BaseDeDatos_Original.db"
)

ARCHIVO_DB = "BaseDeDatos_Original.db"
ARCHIVO_SALIDA = "SuperTienda.csv"

# Extraccion

def extraer(url: str = URL_BASE_DATOS, archivo_destino: str = ARCHIVO_DB) -> str:

    print(f"Descargando base de datos desde: {url}")
    response = requests.get(url)

    if response.status_code == 404:
        print("No encontrado (404).")
    if response.status_code == 500:
        print("Error del servidor (500).")
    if response.status_code != 200:
        print(f"Hubo un problema. Código: {response.status_code}")

    with open(archivo_destino, "wb") as archivo:
        archivo.write(response.content)

    print("Base de datos descargada correctamente.\n")
    return archivo_destino

def cargar_dataframe_unido(ruta_db: str) -> pd.DataFrame:

    conexion = sqlite3.connect(ruta_db)
    try:
        cursor = conexion.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        resultados = cursor.fetchall()
        tablas = []
        for t in resultados:
            nombre_tabla = t[0]
            tablas.append(nombre_tabla)

        print(f"Tablas disponibles: {tablas}\n")

        cursor.execute(
            """
            SELECT
                p.ID_Pedido,
                p.Fecha_Pedido,
                p.Fecha_Envio,
                p.Modo_Envio,
                p.Estado_Pedido,
                dp.ID_Detalle,
                dp.ID_Producto,
                dp.Cantidad,
                dp.Descuento,
                dp.Ventas,
                dp.Ganancia,
                pr.Nombre_Producto,
                pr.Categoria,
                pr.Subcategoria,
                pr.Marca,
                pr.Precio_Lista,
                pr.Costo_Unitario
            FROM Pedidos p
            JOIN Detalle_Pedido dp ON p.ID_Pedido = dp.ID_Pedido
            JOIN Productos pr ON dp.ID_Producto = pr.ID_Producto
            """
        )

        resultado = cursor.fetchall()
        columnas = []
        for col in cursor.description:
            nombre = col[0]
            columnas.append(nombre)

        df = pd.DataFrame(resultado, columns=columnas)

        print(f"DataFrame combinado: {len(df)} filas, {len(df.columns)} columnas.\n")
        return df
    finally:
        conexion.close()

# Transformacion

def transformar(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["Fecha_Pedido"] = pd.to_datetime(df["Fecha_Pedido"], errors="coerce")
    df["Fecha_Envio"] = pd.to_datetime(df["Fecha_Envio"], errors="coerce")

    columnas_numericas = [
        "Cantidad", "Descuento", "Ventas", "Ganancia",
        "Precio_Lista", "Costo_Unitario",
    ]
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    columnas_texto = [
        "Modo_Envio", "Estado_Pedido", "Nombre_Producto",
        "Categoria", "Subcategoria", "Marca",
    ]
    for col in columnas_texto:
        df[col] = df[col].fillna("sin dato").astype(str).str.lower().str.strip()

    # Variable calculada: NivelValor
    # Negativo: ganancia negativa
    # BajoValor: ganancia por debajo del 25%
    # MedioValor: ganancia entre el 25% y 75%
    # AltoValor: ganancia por encima del 75%

    condiciones = [
        df["Ganancia"] < 0,
        (df["Ganancia"] >= 0) & (df["Ganancia"] < 125.045),
        (df["Ganancia"] >= 125.045) & (df["Ganancia"] <= 884.485),
        df["Ganancia"] > 884.485,
    ]
    valores = ["Negativo", "BajoValor", "MedioValor", "AltoValor"]

    df["NivelValor"] = np.select(condiciones, valores, default="Sin Datos")

    print("Transformación completada.")
    print(f"Nulos por columna:\n{df.isna().sum()}\n")
    print(f"Duplicados: {df.duplicated().sum()}\n")

    return df

# Cargar

def cargar(df: pd.DataFrame, nombre_archivo: str = ARCHIVO_SALIDA) -> None:
    """Exporta el DataFrame final a un archivo CSV."""
    df.to_csv(
        nombre_archivo,
        index=False,
        sep=";",
        encoding="utf-8-sig",
        float_format="%.2f",
    )
    print(f"Dataset exportado correctamente como '{nombre_archivo}'")
    print(f"Directorio actual: {os.getcwd()}")

# PIPELINE COMPLETO

def correr_pipeline() -> None:
    ruta_db = extraer()
    df_crudo = cargar_dataframe_unido(ruta_db)
    df_limpio = transformar(df_crudo)
    cargar(df_limpio)

if __name__ == "__main__":
    correr_pipeline()
