import os
from processors.csv_processor import filter_by_stock
from processors.product_classifier import clasificar_productos
from processors.remove_duplicates import remove_duplicates
from processors.update_stock import update_stock  # O el nombre que tengas para actualizar stock
from processors.merge_csv_files import merge_csv_files


def main():
    input_file = os.path.join("input", "productos.csv")  # Archivo de entrada
    if not os.path.exists(input_file):
        print(f"❌ Error: No se encontró el archivo {input_file}")
        return

    print("📌 Procesando archivo CSV...")
    filtrado_file = filter_by_stock(input_file)

    if filtrado_file:
        print(f"✅ Archivo filtrado guardado en: {filtrado_file}")

        print("🔍 Clasificando productos en duplicados y no duplicados...")
        clasificar_productos(filtrado_file)

        print("🗑️ Eliminando duplicados...")
        remove_duplicates(filtrado_file)
        print("✅ Eliminación de duplicados completada.")

        print("🔄 Actualizando stock...")
        update_stock()
        print("✅ Actualización completada.")

        print("🔀 Combinando archivos CSV...")
        merge_csv_files()
        print("✅ Archivos combinados exitosamente.")
    else:
        print("❌ Error en el procesamiento.")


if __name__ == "__main__":
    main()
