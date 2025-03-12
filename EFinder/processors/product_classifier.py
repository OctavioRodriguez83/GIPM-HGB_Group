import csv
import os
import re
from datetime import datetime


class Producto:
    def __init__(self, sku, descripcion, stock):
        self.sku = sku.strip()  # Limpiar espacios
        self.descripcion = descripcion.strip()
        self.stock = stock.strip()


def contiene_sku_exacto(texto, sku):
    """
    Verifica si el SKU aparece en la descripción como una palabra separada.
    """
    regex = re.compile(rf"(^|\W){re.escape(sku)}(\W|$)", re.IGNORECASE)
    return bool(regex.search(texto))


def clasificar_productos(input_file, output_dir_base="output"):
    """
    Clasifica los productos en duplicados y no duplicados.
    Usa el directorio de salida generado en el primer paso.
    Genera dos archivos: 'productos_duplicados.csv' y 'productos_no_duplicados.csv'
    y escribe logs en 'log.txt'.
    """
    # Usar el directorio de salida más reciente
    existing_dirs = sorted([d for d in os.listdir(output_dir_base) if d.startswith("productos_")], reverse=True)
    if not existing_dirs:
        print("❌ No se encontró el directorio de salida del paso anterior.")
        return None, None
    output_dir = os.path.join(output_dir_base, existing_dirs[0])

    duplicados_file = os.path.join(output_dir, "productos_duplicados.csv")
    no_duplicados_file = os.path.join(output_dir, "productos_no_duplicados.csv")
    log_path = os.path.join(output_dir, "log.txt")

    productos = []
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            header = next(reader)  # Leer encabezado
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write("=== Clasificar Productos Log ===\n")
                log_file.write(f"Input file: {input_file}\n")
            for row in reader:
                if len(row) >= 3:
                    productos.append(Producto(row[0], row[1], row[2]))
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {input_file}")
        return None, None

    productos_duplicados = []
    productos_no_duplicados = []
    skus_duplicados = set()

    for producto in productos:
        es_duplicado = False
        for otro_producto in productos:
            if producto.sku != otro_producto.sku and contiene_sku_exacto(otro_producto.descripcion, producto.sku):
                es_duplicado = True
                skus_duplicados.add(producto.sku)
                skus_duplicados.add(otro_producto.sku)
                productos_duplicados.append(producto)
                productos_duplicados.append(otro_producto)
                break
        if not es_duplicado:
            productos_no_duplicados.append(producto)

    # Eliminar de no duplicados los que ya aparecieron como duplicados
    productos_no_duplicados = [p for p in productos_no_duplicados if p.sku not in skus_duplicados]

    guardar_productos_csv(duplicados_file, productos_duplicados)
    guardar_productos_csv(no_duplicados_file, productos_no_duplicados)

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"Total productos procesados: {len(productos)}\n")
        log_file.write(f"Total duplicados encontrados: {len(productos_duplicados)}\n")
        log_file.write(f"Total no duplicados: {len(productos_no_duplicados)}\n")
        log_file.write(f"Archivos generados:\n - {duplicados_file}\n - {no_duplicados_file}\n\n")

    print(f"Archivos generados:\n - {duplicados_file}\n - {no_duplicados_file}")
    return duplicados_file, no_duplicados_file


def guardar_productos_csv(archivo, productos):
    """ Guarda una lista de productos en un archivo CSV """
    try:
        with open(archivo, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["SKU", "Descripción", "Stock"])
            for producto in productos:
                writer.writerow([producto.sku, producto.descripcion, producto.stock])
    except IOError as e:
        print(f"Error al escribir en el archivo {archivo}: {e}")
