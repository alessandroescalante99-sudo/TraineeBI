import sqlite3
import requests

URL_BASE_DATOS = (
    "https://raw.githubusercontent.com/alessandroescalante99-sudo/BasesDeDatos/main/SuperTienda/BaseDeDatos_Original.db"
)

ARCHIVO_DB = "BaseDeDatos_Original.db"
ARCHIVO_SALIDA = "SuperTienda.csv"

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

def VentasPorRegion (ruta_db: str):
    conexion = sqlite3.connect(ruta_db)
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            WITH Ventas_Region AS (
                SELECT
                    g.Region,
                    SUM(dp.Ventas) AS Ventas_Totales,
                    COUNT(DISTINCT p.ID_Pedido) AS Cantidad_Pedidos
                FROM Detalle_Pedido dp
                INNER JOIN Pedidos p
                    ON dp.ID_Pedido = p.ID_Pedido
                INNER JOIN Clientes c
                    ON p.ID_Cliente = c.ID_Cliente
                INNER JOIN Cliente_Ubicacion cu
                    ON c.ID_Cliente = cu.ID_Cliente
                INNER JOIN Geografia g
                    ON cu.ID_Ubicacion = g.ID_Ubicacion
                GROUP BY g.Region
            ),
            Soporte_Region AS (
                SELECT
                    g.Region,
                    MIN(s.Satisfaccion) AS Peor_Satisfaccion
                FROM Soporte s
                INNER JOIN Clientes c
                    ON s.ID_Cliente = c.ID_Cliente
                INNER JOIN Cliente_Ubicacion cu
                    ON c.ID_Cliente = cu.ID_Cliente
                INNER JOIN Geografia g
                    ON cu.ID_Ubicacion = g.ID_Ubicacion
                GROUP BY g.Region
            )
            SELECT
                vr.Region,
                vr.Ventas_Totales,
                vr.Cantidad_Pedidos,
                sr.Peor_Satisfaccion
            FROM Ventas_Region vr
            LEFT JOIN Soporte_Region sr
                ON vr.Region = sr.Region
            ORDER BY vr.Ventas_Totales DESC;
            """
        )
        resultados = cursor.fetchall()
        for fila in resultados:
            print(fila)
        return resultados
    finally:
        conexion.close()

def VerTablas(ruta_db: str):
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
    finally:
        conexion.close()

def ConocerProductos (ruta_db: str):
    conexion = sqlite3.connect(ruta_db)
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
                PRAGMA table_info(Productos);
            """
        )
        resultados = cursor.fetchall()
        for filas in resultados:
            print(filas)
        return resultados
    finally:
        conexion.close()

def MayorPrecioTecnologia (ruta_db: str):
    conexion = sqlite3.connect(ruta_db)
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
                SELECT 
                    p.Nombre_Producto, 
                    p.Categoria, 
                    p.Precio_Lista
                FROM Productos p 
                WHERE Categoria = 'Tecnología'
                ORDER BY p.Precio_Lista desc 
                LIMIT 10;
            """
        )
        resultados = cursor.fetchall()
        for fila in resultados:
            print(fila)
        return resultados
    finally:
        conexion.close()

def ClientesRentables (ruta_db: str):
    conexion = sqlite3.connect(ruta_db)
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT
                c.ID_Cliente,
                c.Nombre_Cliente,
                SUM(dp.Cantidad) AS Pedidos_Totales,
                SUM(dp.Ventas) AS Ventas_Totales,
                SUM(dp.Ganancia) AS Ganancia_Totales
                FROM Detalle_Pedido dp
                INNER JOIN Pedidos p
                    ON dp.ID_Pedido = p.ID_Pedido
                INNER JOIN Clientes c
                    ON p.ID_Cliente = c.ID_Cliente
                GROUP BY c.ID_Cliente, c.Nombre_Cliente
                ORDER BY Ganancia_Totales DESC
                LIMIT 10;
            """
        )
        resultados = cursor.fetchall()
        for filas in resultados:
            print(filas)
        return resultados
    finally:
        conexion.close()

def correr():

    print(" ")
    print("Traer la Base de Datos")
    print(" ")
    ruta_db = extraer()

    print(" ")
    print("Ver las tablas de la Base de Datos")
    print(" ")
    DF_Vertablas = VerTablas(ruta_db)

    print(" ")
    print("Conocer la Tabla Productos")
    print(" ")
    DF_ConocerProductos = ConocerProductos(ruta_db)

    print(" ")
    print("Conocer los productos de mayor precio en la categoria Tecnologia")
    print(" ")
    DF_MayorPrecioTecnologia = MayorPrecioTecnologia(ruta_db)

    print(" ")
    print("Ventas y Ganancias generadas por Cliente")
    print(" ")
    DF_ClientesRentables = ClientesRentables(ruta_db)

    print(" ")
    print("Por Region calculamos las Ventas, Cantidad de pedidos y Ticket con menor satisfaccion")
    print(" ")
    DF_VentasPorRegion = VentasPorRegion(ruta_db)


if __name__ == "__main__":
    correr()