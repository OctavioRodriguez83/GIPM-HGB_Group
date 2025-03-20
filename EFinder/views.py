import os
import csv
import re
from datetime import datetime
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# ---------------------------
# Funciones de Utilidad
# ---------------------------
def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def create_output_dir():
    """Crea la carpeta de salida en el escritorio con nombre 'productos_YYYYMMDD_HHMMSS'"""
    desktop_path = get_desktop_path()
    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(desktop_path, f"productos_{fecha_actual}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

# Create your views here.

# ---------------------------
# Views de la Aplicación
# ---------------------------

# Temporal Home Page View
#@login_required
def home(request):
    return render(request, 'home.html')

def inv_eu(request):
    return render(request, 'EFinder/inv_eu.html')

# ---------------------------
# Funciones para el procesamiento de archivos CSV
# ---------------------------

# ---------------------------
# Paso 1: Filtrar por Stock
# ---------------------------
def filter_by_stock(input_file, output_file, log_file):
    total_rows = 0
    written_rows = 0
    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', newline='', encoding='utf-8') as outfile, \
            open(log_file, 'a', encoding='utf-8') as logf:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        header = next(reader)  # Leer encabezado
        writer.writerow(header)
        logf.write("=== Filter by Stock Log ===\n")
        logf.write(f"Input file: {input_file}\n")
        for row in reader:
            total_rows += 1
            if len(row) > 2 and row[2].strip() != "0":
                writer.writerow(row)
                written_rows += 1
        logf.write(f"Total rows read: {total_rows}\n")
        logf.write(f"Rows written (stock != 0): {written_rows}\n")
        logf.write(f"Output file: {output_file}\n\n")
    return output_file


# ---------------------------
# Paso 2: Clasificar Productos
# ---------------------------
class Producto:
    def __init__(self, sku, descripcion, stock):
        self.sku = sku.strip()
        self.descripcion = descripcion.strip()
        self.stock = stock.strip()


def contiene_sku_exacto(texto, sku):
    regex = re.compile(rf"(^|\W){re.escape(sku)}(\W|$)", re.IGNORECASE)
    return bool(regex.search(texto))


def guardar_productos_csv(archivo, productos):
    with open(archivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["SKU", "Descripción", "Stock"])
        for p in productos:
            writer.writerow([p.sku, p.descripcion, p.stock])


def clasificar_productos(input_file, duplicados_file, no_duplicados_file, log_file):
    productos = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        next(reader)  # Saltar encabezado
        with open(log_file, 'a', encoding='utf-8') as logf:
            logf.write("=== Clasificar Productos Log ===\n")
            logf.write(f"Input file: {input_file}\n")
        for row in reader:
            if len(row) >= 3:
                productos.append(Producto(row[0], row[1], row[2]))
    productos_duplicados = []
    productos_no_duplicados = []
    skus_duplicados = set()
    for p in productos:
        es_duplicado = False
        for q in productos:
            if p.sku != q.sku and contiene_sku_exacto(q.descripcion, p.sku):
                es_duplicado = True
                skus_duplicados.add(p.sku)
                skus_duplicados.add(q.sku)
                productos_duplicados.append(p)
                productos_duplicados.append(q)
                break
        if not es_duplicado:
            productos_no_duplicados.append(p)
    # Eliminar de los no duplicados los que ya aparecen como duplicados
    productos_no_duplicados = [p for p in productos_no_duplicados if p.sku not in skus_duplicados]
    guardar_productos_csv(duplicados_file, productos_duplicados)
    guardar_productos_csv(no_duplicados_file, productos_no_duplicados)
    with open(log_file, 'a', encoding='utf-8') as logf:
        logf.write(f"Total products processed: {len(productos)}\n")
        logf.write(f"Duplicates found: {len(productos_duplicados)}\n")
        logf.write(f"Non-duplicates: {len(productos_no_duplicados)}\n")
        logf.write(f"Duplicados file: {duplicados_file}\n")
        logf.write(f"No duplicados file: {no_duplicados_file}\n\n")
    return duplicados_file, no_duplicados_file


# ---------------------------
# Paso 3: Eliminar Duplicados
# ---------------------------
def remove_duplicates(input_file, output_file, log_file):
    unique_records = {}
    counter_total = 0
    counter_unique = 0
    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', newline='', encoding='utf-8') as outfile, \
            open(log_file, 'a', encoding='utf-8') as logf:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        header = next(reader)
        writer.writerow(header)
        logf.write("=== Remove Duplicates Log ===\n")
        logf.write(f"Input file: {input_file}\n")
        for row in reader:
            counter_total += 1
            sku = row[0]
            if sku not in unique_records:
                unique_records[sku] = row
                counter_unique += 1
        for record in unique_records.values():
            writer.writerow(record)
        logf.write(f"Total rows read: {counter_total}\n")
        logf.write(f"Unique rows: {counter_unique}\n")
        logf.write(f"Output file: {output_file}\n\n")
    return output_file


# ---------------------------
# Paso 4: Actualizar Stock
# ---------------------------
class ProductoStock:
    def __init__(self, sku, descripcion, stock):
        self.sku = sku.strip()
        self.descripcion = descripcion.strip()
        try:
            self.stock = int(stock)
        except:
            self.stock = 0


def leer_productos_csv(file_path):
    productos = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Saltar encabezado
        for row in reader:
            if len(row) == 3:
                productos.append(ProductoStock(row[0], row[1], row[2]))
    return productos


def guardar_productos_csv_stock(productos, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SKU", "Descripción", "Stock"])
        for p in productos:
            writer.writerow([p.sku, p.descripcion, p.stock])


def update_stock(archivo_ref, archivo_actualizar, archivo_salida, log_file):
    with open(log_file, "a", encoding="utf-8") as logf:
        logf.write("=== Update Stock Log ===\n")
        logf.write(f"Reference file: {archivo_ref}\n")
        logf.write(f"File to update: {archivo_actualizar}\n")
    if not os.path.exists(archivo_ref) or not os.path.exists(archivo_actualizar):
        with open(log_file, "a", encoding="utf-8") as logf:
            logf.write("Error: Reference or update file not found.\n\n")
        return None
    productos_ref = leer_productos_csv(archivo_ref)
    productos_actualizar = leer_productos_csv(archivo_actualizar)
    ref_dict = {p.sku: p for p in productos_ref}
    updated_count = 0
    for p in productos_actualizar:
        if p.sku in ref_dict:
            p.stock = ref_dict[p.sku].stock
            updated_count += 1
    guardar_productos_csv_stock(productos_actualizar, archivo_salida)
    with open(log_file, "a", encoding="utf-8") as logf:
        logf.write(f"Total reference products: {len(productos_ref)}\n")
        logf.write(f"Products updated: {updated_count}\n")
        logf.write(f"Output file: {archivo_salida}\n\n")
    return archivo_salida


# ---------------------------
# Paso 5: Fusionar CSV
# ---------------------------
def merge_csv_files(file1, file2, output_file, log_file):
    counter_file1 = 0
    counter_file2 = 0
    total_written = 0
    with open(log_file, "a", encoding="utf-8") as logf:
        logf.write("=== Merge CSV Files Log ===\n")
    with open(output_file, "w", newline="", encoding="utf-8") as outfile, \
            open(log_file, "a", encoding="utf-8") as logf:
        writer = csv.writer(outfile)
        # Procesar primer archivo
        with open(file1, "r", encoding="utf-8") as f1:
            reader1 = csv.reader(f1)
            header = next(reader1)
            writer.writerow(header)
            logf.write(f"Header from {file1}: {header}\n")
            for row in reader1:
                writer.writerow(row)
                counter_file1 += 1
                total_written += 1
        logf.write(f"Records from {file1}: {counter_file1}\n")
        # Procesar segundo archivo (se descarta la cabecera)
        with open(file2, "r", encoding="utf-8") as f2:
            reader2 = csv.reader(f2)
            header2 = next(reader2)
            logf.write(f"Skipped header from {file2}: {header2}\n")
            for row in reader2:
                writer.writerow(row)
                counter_file2 += 1
                total_written += 1
        logf.write(f"Records from {file2}: {counter_file2}\n")
        logf.write(f"Total records merged: {total_written}\n")
        logf.write("Merge completed successfully.\n\n")
    return output_file


# ---------------------------
# Pipeline Completo: Generador de Progreso
# ---------------------------
def process_pipeline_generator(productos_path, duplicados_input_path):
    yield "Creando carpeta de salida..."
    output_dir = create_output_dir()
    log_file = os.path.join(output_dir, "log.txt")
    yield f"Carpeta de salida creada: {output_dir}"

    # Paso 1: Filtrar por stock
    yield "Iniciando filtrado por stock..."
    filtrado_file = os.path.join(output_dir, "filtrado_stock.csv")
    filter_by_stock(productos_path, filtrado_file, log_file)
    yield f"Filtrado completado. Archivo: {filtrado_file}"

    # Paso 2: Clasificar productos
    yield "Iniciando clasificación de productos..."
    duplicados_file = os.path.join(output_dir, "productos_duplicados.csv")
    no_duplicados_file = os.path.join(output_dir, "productos_no_duplicados.csv")
    clasificar_productos(filtrado_file, duplicados_file, no_duplicados_file, log_file)
    yield f"Clasificación completada. Duplicados: {duplicados_file}, No duplicados: {no_duplicados_file}"

    # Paso 3: Eliminar duplicados
    yield "Iniciando eliminación de duplicados..."
    duplicadosF_file = os.path.join(output_dir, "productos_duplicadosF.csv")
    remove_duplicates(duplicados_file, duplicadosF_file, log_file)
    yield f"Eliminación completada. Archivo: {duplicadosF_file}"

    # Paso 4: Actualizar stock
    yield "Iniciando actualización de stock..."
    duplicadosFF_actualizados = os.path.join(output_dir, "productos_duplicadosFF_Actualizados.csv")
    update_stock(duplicadosF_file, duplicados_input_path, duplicadosFF_actualizados, log_file)
    yield f"Actualización completada. Archivo: {duplicadosFF_actualizados}"

    # Paso 5: Fusionar archivos CSV
    yield "Iniciando fusión de archivos CSV..."
    productos_combinados = os.path.join(output_dir, "productos_combinados.csv")
    merge_csv_files(duplicadosFF_actualizados, no_duplicados_file, productos_combinados, log_file)
    yield f"Fusión completada. Archivo: {productos_combinados}"

    # Mensaje final con el path para que se muestre y se copie
    yield f"FINAL: Revisa la carpeta: {output_dir}"


# La vista que transmite el progreso permanece igual:
def process_files_view(request):
    desktop_path = get_desktop_path()
    input_dir = os.path.join(desktop_path, "input")
    productos_path = os.path.join(input_dir, "productos.csv")
    duplicados_input_path = os.path.join(input_dir, "productos_duplicadosFF.csv")
    if not os.path.exists(productos_path):
        yield "<div class='alert alert-danger'>Error: No se encontró el archivo productos.csv en la carpeta de entrada.</div>"
        return
    # Inicia la estructura HTML
    yield "<div class='list-group'>"
    for progress in process_pipeline_generator(productos_path, duplicados_input_path):
        yield f"<div class='list-group-item'>{progress}</div>"
    yield "</div>"


# ---------------------------
# Vista para subir archivos y ejecutar el pipeline
# ---------------------------
@csrf_exempt
@csrf_exempt
def upload_csv(request):
    if request.method == "POST":
        productos_csv = request.FILES.get("productos")
        duplicados_csv = request.FILES.get("productos_duplicadosFF")
        if not productos_csv or not duplicados_csv:
            return JsonResponse({"error": "Faltan archivos"}, status=400)
        desktop_path = get_desktop_path()
        input_dir = os.path.join(desktop_path, "input")
        os.makedirs(input_dir, exist_ok=True)
        productos_path = os.path.join(input_dir, "productos.csv")
        duplicados_path = os.path.join(input_dir, "productos_duplicadosFF.csv")
        with open(productos_path, "wb") as f:
            f.write(productos_csv.read())
        with open(duplicados_path, "wb") as f:
            f.write(duplicados_csv.read())
        return StreamingHttpResponse(process_files_view(request), content_type="text/html")
    return render(request, "EFinder/inv_eu.html")
