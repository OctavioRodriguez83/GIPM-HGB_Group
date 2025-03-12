import csv
import os
from datetime import datetime


def process_pipeline(input_file, output_dir_base, step_name, process_function):
    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_dir_base, f"productos_{fecha_actual}")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"{step_name}.csv")
    try:
        return process_function(input_file, output_file)
    except Exception as e:
        print(f"Error en {step_name}: {str(e)}")
        return None


# Filtrar por stock con logs
def filter_by_stock(input_file, output_dir_base="output"):
    def _process(in_path, out_path):
        # Definir la ruta del log en el mismo directorio que el archivo de salida
        log_path = os.path.join(os.path.dirname(out_path), "log.txt")
        total_rows = 0
        written_rows = 0
        with open(in_path, 'r', encoding='utf-8') as infile, \
                open(out_path, 'w', newline='', encoding='utf-8') as outfile, \
                open(log_path, 'a', encoding='utf-8') as log_file:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            header = next(reader)  # Leer encabezado
            writer.writerow(header)
            log_file.write("=== Filter by Stock Log ===\n")
            log_file.write(f"Input file: {in_path}\n")
            for row in reader:
                total_rows += 1
                if len(row) > 2 and row[2].strip() != "0":
                    writer.writerow(row)
                    written_rows += 1
            log_file.write(f"Total rows read: {total_rows}\n")
            log_file.write(f"Total rows written (stock != 0): {written_rows}\n")
            log_file.write(f"Output file: {out_path}\n\n")
        return out_path

    return process_pipeline(input_file, output_dir_base, "filtrado_stock", _process)
