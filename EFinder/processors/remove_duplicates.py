import csv
import os
from datetime import datetime


def remove_duplicates(input_file, output_dir_base="output"):
    def _process(in_path, out_path, log_path):
        unique_records = {}
        counter_total = 0
        counter_unique = 0

        with open(in_path, 'r', encoding='utf-8') as infile, \
                open(out_path, 'w', newline='', encoding='utf-8') as outfile, \
                open(log_path, 'w', encoding='utf-8') as log_file:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            header = next(reader)  # Leer encabezado
            writer.writerow(header)  # Escribir encabezado en el archivo final

            log_file.write("=== Remove Duplicates Log ===\n")
            log_file.write(f"Iniciando proceso para eliminar duplicados en {in_path}\n\n")

            for row in reader:
                counter_total += 1
                sku = row[0]  # SKU en la primera columna

                if sku not in unique_records:
                    unique_records[sku] = row
                    counter_unique += 1

            # Escribir productos únicos en el archivo de salida
            for record in unique_records.values():
                writer.writerow(record)

            # Escribir resumen en el log
            log_file.write("\n=== Remove Logs ===\n")
            log_file.write(f"Total registros leídos: {counter_total}\n")
            log_file.write(f"Total registros únicos: {counter_unique}\n")
            log_file.write(f"Archivo generado correctamente: {out_path}\n")

        return out_path

    # Obtener el directorio más reciente generado por el primer script
    existing_dirs = sorted([d for d in os.listdir(output_dir_base) if d.startswith("productos_")], reverse=True)
    if not existing_dirs:
        print("❌ No se encontró el directorio de salida del paso anterior.")
        return None

    output_dir = os.path.join(output_dir_base, existing_dirs[0])  # Tomar el más reciente
    input_file_path = os.path.join(output_dir, "productos_duplicados.csv")
    output_file_path = os.path.join(output_dir, "productos_duplicadosF.csv")
    log_file_path = os.path.join(output_dir, "log.txt")

    if not os.path.exists(input_file_path):
        print(f"❌ Error: No se encontró el archivo {input_file_path}")
        return None

    return _process(input_file_path, output_file_path, log_file_path)
