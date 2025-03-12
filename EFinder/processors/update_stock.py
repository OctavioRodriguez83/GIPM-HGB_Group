import csv
import os


# Clase para representar un producto (para actualización de stock)
class Producto:
    def __init__(self, sku, descripcion, stock):
        self.sku = sku.strip()
        self.descripcion = descripcion.strip()
        try:
            self.stock = int(stock)
        except ValueError:
            self.stock = 0


def leer_productos_csv(file_path):
    productos = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Saltar encabezado
        for row in reader:
            if len(row) == 3:
                productos.append(Producto(row[0], row[1], row[2]))
    return productos


def guardar_productos_csv(productos, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SKU", "Descripción", "Stock"])
        for producto in productos:
            writer.writerow([producto.sku, producto.descripcion, producto.stock])


def update_stock():
    output_base = "output"
    # Obtener el directorio de salida más reciente
    output_dirs = sorted([d for d in os.listdir(output_base) if d.startswith("productos_")], reverse=True)
    if not output_dirs:
        print("❌ No se encontró el directorio de salida del paso anterior.")
        return None
    output_dir = os.path.join(output_base, output_dirs[0])
    log_path = os.path.join(output_dir, "log.txt")

    # Definir rutas
    archivo_ref = os.path.join(output_dir, "productos_duplicadosF.csv")
    archivo_actualizar = os.path.join("input", "productos_duplicadosFF.csv")
    archivo_salida = os.path.join(output_dir, "productos_duplicadosFF_Actualizados.csv")

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write("=== Update Stock Log ===\n")
        log_file.write(f"Archivo de referencia: {archivo_ref}\n")
        log_file.write(f"Archivo a actualizar: {archivo_actualizar}\n")

    if not os.path.exists(archivo_ref):
        print(f"❌ No se encontró el archivo de referencia: {archivo_ref}")
        return None
    if not os.path.exists(archivo_actualizar):
        print(f"❌ No se encontró el archivo a actualizar: {archivo_actualizar}")
        return None

    productos_ref = leer_productos_csv(archivo_ref)
    productos_actualizar = leer_productos_csv(archivo_actualizar)
    ref_dict = {producto.sku: producto for producto in productos_ref}

    updated_count = 0
    for producto in productos_actualizar:
        if producto.sku in ref_dict:
            producto.stock = ref_dict[producto.sku].stock
            updated_count += 1

    guardar_productos_csv(productos_actualizar, archivo_salida)

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"Total productos de referencia: {len(productos_ref)}\n")
        log_file.write(f"Total productos actualizados: {updated_count}\n")
        log_file.write(f"Archivo actualizado guardado: {archivo_salida}\n\n")

    print("Archivo actualizado guardado como:", archivo_salida)
    return archivo_salida


if __name__ == "__main__":
    update_stock()
