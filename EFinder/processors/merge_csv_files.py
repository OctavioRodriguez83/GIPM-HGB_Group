import csv
import os


def merge_csv_files(output_dir_base="output"):
    """
    Combina dos archivos CSV:
      - 'productos_duplicadosFF_Actualizados.csv' (archivo 1)
      - 'productos_no_duplicados.csv' (archivo 2)

    El resultado se guarda como 'productos_combinados.csv' en el directorio de salida.
    Se genera un log detallado del proceso en 'merge_log.txt'.
    """
    # Obtener el directorio de salida más reciente (ej: productos_20230325_153045)
    output_dirs = sorted([d for d in os.listdir(output_dir_base) if d.startswith("productos_")], reverse=True)
    if not output_dirs:
        print("❌ No se encontró el directorio de salida del paso anterior.")
        return None
    output_dir = os.path.join(output_dir_base, output_dirs[0])

    # Definir rutas de archivos
    file1 = os.path.join(output_dir, "productos_duplicadosFF_Actualizados.csv")
    file2 = os.path.join(output_dir, "productos_no_duplicados.csv")
    output_file = os.path.join(output_dir, "productos_combinados.csv")
    log_file_path = os.path.join(output_dir, "merge_log.txt")

    # Inicializar contadores para estadísticas
    counter_file1 = 0
    counter_file2 = 0
    total_written = 0

    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write("=== Merge CSV Files Log ===\n")
        log_file.write(f"Directorio de salida utilizado: {output_dir}\n\n")

        try:
            with open(output_file, "w", newline="", encoding="utf-8") as outfile:
                writer = csv.writer(outfile)

                # Procesar el primer archivo
                with open(file1, "r", encoding="utf-8") as f1:
                    reader1 = csv.reader(f1)
                    header = next(reader1)  # Leer encabezado
                    writer.writerow(header)  # Escribir encabezado en el archivo combinado
                    log_file.write(f"Cabecera tomada de {file1}: {header}\n")

                    for row in reader1:
                        writer.writerow(row)
                        counter_file1 += 1
                        total_written += 1

                log_file.write(f"Total de registros leídos y escritos desde {file1}: {counter_file1}\n")

                # Procesar el segundo archivo
                with open(file2, "r", encoding="utf-8") as f2:
                    reader2 = csv.reader(f2)
                    header2 = next(reader2)  # Leer y descartar la cabecera del segundo archivo
                    log_file.write(f"Cabecera descartada de {file2}: {header2}\n")

                    for row in reader2:
                        writer.writerow(row)
                        counter_file2 += 1
                        total_written += 1

                log_file.write(f"Total de registros leídos y escritos desde {file2}: {counter_file2}\n")
                log_file.write(f"\nTotal registros combinados escritos en {output_file}: {total_written}\n")
                log_file.write("Archivos combinados exitosamente.\n")

            print("Archivos combinados exitosamente. Archivo generado:", output_file)
            return output_file
        except Exception as e:
            log_file.write(f"Error durante el proceso de combinación: {str(e)}\n")
            print("❌ Error durante el proceso de combinación:", str(e))
            return None


if __name__ == "__main__":
    merge_csv_files()
