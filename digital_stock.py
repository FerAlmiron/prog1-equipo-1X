# digital_stock.py
import curses
import os
import time
import re
import json
from typing import List, Dict, Optional, Tuple

INVENTARIO_FILE = "inventario.json"
BALANCE_FILE = "balance.json"

# ---------------- Core (no-UI) - funciones reutilizables ----------------

def cargar_inventario(filename: str = INVENTARIO_FILE) -> List[Dict]:
    """Carga inventario desde JSON; devuelve lista de dicts."""
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            # Validar formato básico
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    return []


def guardar_inventario(inventario: List[Dict], filename: str = INVENTARIO_FILE):
    """Guarda inventario en JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(inventario, f, ensure_ascii=False, indent=2)


def registrar_transaccion(tipo: str, codigo: str, nombre: str, cantidad: int, monto: float, filename: str = BALANCE_FILE):
    """Registra una transacción en un archivo JSON manteniendo una lista de objetos."""
    trans = {
        "tipo": tipo,
        "codigo": codigo,
        "nombre": nombre,
        "cantidad": cantidad,
        "monto": monto,
        "ts": time.time()
    }
    bal = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                bal = json.load(f) or []
        except json.JSONDecodeError:
            bal = []
    bal.append(trans)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(bal, f, ensure_ascii=False, indent=2)


def calcular_balance(filename: str = BALANCE_FILE) -> Tuple[float, float]:
    """Calcula totales a partir del archivo de balance."""
    total_compra = 0.0
    total_venta = 0.0
    if not os.path.exists(filename):
        return total_compra, total_venta
    with open(filename, "r", encoding="utf-8") as f:
        try:
            datos = json.load(f)
        except json.JSONDecodeError:
            datos = []
    for t in datos:
        tipo = t.get("tipo", "")
        monto = float(t.get("monto", 0))
        if tipo == "COMPRA":
            total_compra += monto
        elif tipo == "VENTA":
            total_venta += monto
    return total_compra, total_venta


def buscar_producto(codigo: str, inventario: List[Dict]) -> Optional[Dict]:
    """Búsqueda iterativa case-insensitive por código."""
    codigo = codigo.lower()
    for p in inventario:
        if p.get("codigo", "").lower() == codigo:
            return p
    return None


def buscar_producto_recursivo(codigo: str, inventario: List[Dict], idx: int = 0) -> Optional[Dict]:
    """Ejemplo de búsqueda recursiva por código."""
    if idx >= len(inventario):
        return None
    if inventario[idx].get("codigo", "").lower() == codigo.lower():
        return inventario[idx]
    return buscar_producto_recursivo(codigo, inventario, idx + 1)


def stock_total_recursivo(inventario: List[Dict], idx: int = 0) -> int:
    """Suma recursiva de cantidades (ejemplo de recursividad)."""
    if idx >= len(inventario):
        return 0
    return inventario[idx].get("cantidad", 0) + stock_total_recursivo(inventario, idx + 1)


def agregar_producto(inventario: List[Dict], producto: Dict, inventario_file: str = INVENTARIO_FILE, balance_file: str = BALANCE_FILE):
    """Agrega un producto nuevo y registra compra."""
    # Validaciones mínimas
    if not producto.get("codigo") or not producto.get("nombre"):
        raise ValueError("Código y nombre requeridos.")
    if buscar_producto(producto["codigo"], inventario):
        raise ValueError("Código duplicado.")
    inventario.append(producto)
    guardar_inventario(inventario, inventario_file)
    registrar_transaccion("COMPRA", producto["codigo"], producto["nombre"], producto["cantidad"], producto["cantidad"] * producto["precio"], balance_file)


def vender_producto_logico(codigo: str, cantidad: int, precio_unitario: float, inventario: List[Dict], inventario_file: str = INVENTARIO_FILE, balance_file: str = BALANCE_FILE):
    """Realiza la venta en la lógica (no UI). Lanza ValueError si falla."""
    if cantidad <= 0:
        raise ValueError("Cantidad debe ser mayor a cero.")
    producto = buscar_producto(codigo, inventario)
    if not producto:
        raise ValueError("Producto no existe.")
    if producto["cantidad"] < cantidad:
        raise ValueError("Stock insuficiente.")
    producto["cantidad"] -= cantidad
    guardar_inventario(inventario, inventario_file)
    registrar_transaccion("VENTA", producto["codigo"], producto["nombre"], cantidad, cantidad * precio_unitario, balance_file)


def eliminar_producto_logico(codigo: str, inventario: List[Dict], inventario_file: str = INVENTARIO_FILE):
    """Elimina producto por código."""
    for i, p in enumerate(inventario):
        if p.get("codigo", "").lower() == codigo.lower():
            inventario.pop(i)
            guardar_inventario(inventario, inventario_file)
            return p
    raise ValueError("Producto no encontrado.")


def obtener_productos_bajo_stock(inventario: List[Dict], umbral: int = 10) -> List[Dict]:
    """Devuelve lista de productos con cantidad < umbral (usa lambda)."""
    filt = list(filter(lambda x: x.get("cantidad", 0) < umbral, inventario))
    # ordenar por cantidad ascendente con lambda
    return sorted(filt, key=lambda x: x.get("cantidad", 0))


# ---------------- Interfaz curses (UI) ----------------

def animacion_inicio(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    h, w = stdscr.getmaxyx()
    titulo = "SISTEMA DE CONTROL DE STOCK"
    subtitulo = "DigitalStock."

    stdscr.clear()
    stdscr.addstr(h // 2 - 3, w // 2 - len(titulo) // 2,
                  titulo, curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(h // 2 - 1, w // 2 - len(subtitulo) // 2,
                  subtitulo, curses.color_pair(3))
    stdscr.refresh()
    time.sleep(0.6)

    for i in range(0, 51):
        barra = "#" * i
        stdscr.addstr(h // 2 + 2, w // 2 - 25,
                      f"[{barra:<50}] {i*2:>3}%", curses.color_pair(2))
        stdscr.refresh()
        time.sleep(0.02)

    time.sleep(0.4)
    stdscr.clear()
    stdscr.refresh()


def mostrar_inventario(stdscr, inventario):
    stdscr.clear()
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()

    titulo = "📦 INVENTARIO ACTUAL 📦"
    cabecera = "Código   Nombre               Cantidad   Precio"
    x_titulo = w // 2 - len(titulo) // 2
    x_cabecera = w // 2 - len(cabecera) // 2
    y_inicio = max(3, h // 2 - (len(inventario) // 2) - 4)

    stdscr.addstr(y_inicio - 2, x_titulo, titulo, curses.A_BOLD | curses.color_pair(2))
    stdscr.addstr(y_inicio, x_cabecera, cabecera, curses.A_BOLD)
    stdscr.addstr(y_inicio + 1, x_cabecera, "-" * len(cabecera))

    # ordenar por nombre usando lambda
    productos = sorted(inventario, key=lambda p: p.get("nombre", "").lower())

    fila_y = y_inicio + 2
    for p in productos:
        linea = f"{p.get('codigo',''):<8}{p.get('nombre',''):<20}{p.get('cantidad',0):<10}{p.get('precio',0):<10.2f}"
        x_linea = w // 2 - len(linea) // 2
        color = curses.color_pair(1) if p.get("cantidad", 0) < 10 else curses.A_NORMAL
        stdscr.addstr(fila_y, x_linea, linea, color)
        fila_y += 1
        stdscr.refresh()
        curses.napms(40)

    if not inventario:
        msg = "🚫 No hay productos registrados."
        stdscr.addstr(h // 2, w // 2 - len(msg) // 2, msg, curses.color_pair(1) | curses.A_BOLD)

    stdscr.addstr(h - 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
    stdscr.refresh()
    stdscr.getch()


def comprar_producto(stdscr, inventario):
    stdscr.clear()
    curses.echo()
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()

    try:
        stdscr.addstr(0, 0, "=== Registrar Compra ===", curses.A_BOLD)

        stdscr.addstr(2, 0, "Código del producto: ")
        codigo = stdscr.getstr(2, 25, 20).decode("utf-8").strip()
        if not codigo or not re.match(r'^[A-Za-z0-9\-]+$', codigo):
            raise ValueError("Código inválido (letras, números, guiones).")

        if buscar_producto(codigo, inventario):
            raise ValueError("Código ya existe.")

        stdscr.addstr(3, 0, "Nombre del producto: ")
        nombre = stdscr.getstr(3, 25, 30).decode("utf-8").strip()
        if not nombre:
            raise ValueError("Nombre vacío.")

        stdscr.addstr(4, 0, "Cantidad comprada: ")
        cant_str = stdscr.getstr(4, 25, 10).decode("utf-8").strip()
        if not cant_str.isdigit():
            raise ValueError("Cantidad debe ser entero.")
        cantidad = int(cant_str)
        if cantidad <= 0:
            raise ValueError("Cantidad debe ser > 0.")

        stdscr.addstr(5, 0, "Precio unitario de compra: ")
        precio_str = stdscr.getstr(5, 30, 15).decode("utf-8").strip()
        precio = float(precio_str)
        if precio <= 0:
            raise ValueError("Precio debe ser > 0.")

        producto = {"codigo": codigo, "nombre": nombre, "cantidad": cantidad, "precio": precio}
        agregar_producto(inventario, producto)

        stdscr.clear()
        msg = "💾 Compra registrada correctamente."
        stdscr.addstr(h // 2, w // 2 - len(msg)//2, msg, curses.color_pair(2) | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(800)

    except ValueError as e:
        stdscr.addstr(8, 0, f"⚠️ Error: {e}", curses.color_pair(1))
    except Exception as e:
        stdscr.addstr(8, 0, f"⚠️ Error inesperado: {e}", curses.color_pair(1))
    finally:
        curses.noecho()
        curses.curs_set(0)
        stdscr.addstr(h - 2, 0, "Presione una tecla para continuar...", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()


def vender_producto_ui(stdscr, inventario):
    stdscr.clear()
    curses.echo()
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()

    try:
        stdscr.addstr(0, 0, "=== Registrar Venta ===", curses.A_BOLD)
        stdscr.addstr(2, 0, "Código del producto: ")
        codigo = stdscr.getstr(2, 25, 20).decode("utf-8").strip()
        if not codigo:
            raise ValueError("Código vacío.")

        producto = buscar_producto(codigo, inventario)
        if not producto:
            raise ValueError("Producto no encontrado.")

        stdscr.addstr(3, 0, f"Stock actual: {producto['cantidad']}")
        stdscr.addstr(4, 0, "Cantidad vendida: ")
        cant_str = stdscr.getstr(4, 25, 10).decode("utf-8").strip()
        if not cant_str.isdigit():
            raise ValueError("Cantidad inválida.")
        cantidad = int(cant_str)
        if cantidad <= 0:
            raise ValueError("Cantidad debe ser > 0.")
        if producto["cantidad"] < cantidad:
            raise ValueError("Stock insuficiente.")

        stdscr.addstr(5, 0, "Precio unitario de venta: ")
        precio_str = stdscr.getstr(5, 30, 15).decode("utf-8").strip()
        precio = float(precio_str)
        if precio <= 0:
            raise ValueError("Precio inválido.")

        vender_producto_logico(codigo, cantidad, precio, inventario)

        stdscr.clear()
        msg = "✅ Venta registrada correctamente."
        stdscr.addstr(h // 2, w // 2 - len(msg)//2, msg, curses.color_pair(2) | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(800)

    except ValueError as e:
        stdscr.addstr(8, 0, f"⚠️ Error: {e}", curses.color_pair(1))
    except Exception as e:
        stdscr.addstr(8, 0, f"⚠️ Error inesperado: {e}", curses.color_pair(1))
    finally:
        curses.noecho()
        curses.curs_set(0)
        stdscr.addstr(h - 2, 0, "Presione una tecla para continuar...", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()


def eliminar_producto_ui(stdscr, inventario):
    stdscr.clear()
    curses.echo()
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()
    try:
        titulo = "=== Eliminar Producto del Inventario ==="
        stdscr.addstr(0, w // 2 - len(titulo)//2, titulo, curses.A_BOLD)

        stdscr.addstr(2, 0, "Ingrese el código del producto a eliminar: ")
        codigo = stdscr.getstr(2, 45, 20).decode("utf-8").strip()
        if not codigo:
            raise ValueError("Código vacío.")

        producto = buscar_producto(codigo, inventario)
        if not producto:
            raise ValueError("Producto no encontrado.")

        stdscr.addstr(4, 0, f"¿Seguro que desea eliminar '{producto['nombre']}'? (s/n): ")
        tecla = stdscr.getch()
        if chr(tecla).lower() != "s":
            stdscr.addstr(6, 0, "Operación cancelada.", curses.color_pair(1))
            stdscr.getch()
            return

        eliminar_producto_logico(codigo, inventario)

        stdscr.clear()
        msg = f"✅ Producto '{producto['nombre']}' eliminado."
        stdscr.addstr(h // 2, w // 2 - len(msg)//2, msg, curses.color_pair(2) | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(700)

    except ValueError as e:
        stdscr.addstr(8, 0, f"⚠️ Error: {e}", curses.color_pair(1))
    except Exception as e:
        stdscr.addstr(8, 0, f"⚠️ Error inesperado: {e}", curses.color_pair(1))
    finally:
        curses.noecho()
        curses.curs_set(0)
        stdscr.addstr(h - 2, 0, "Presione una tecla para continuar...", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()


def mostrar_balance_ui(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()

    compras, ventas = calcular_balance()
    ganancia = ventas - compras
    color_ganancia = curses.color_pair(2) if ganancia >= 0 else curses.color_pair(1)

    titulo = "=== BALANCE GENERAL ==="
    stdscr.addstr(h // 2 - 6, w // 2 - len(titulo)//2, titulo, curses.A_BOLD)

    duracion = 30
    for i in range(1, duracion + 1):
        total_compra_anim = compras * (i / duracion)
        total_venta_anim = ventas * (i / duracion)
        ganancia_anim = total_venta_anim - total_compra_anim

        stdscr.addstr(h // 2 - 3, w // 2 - 20, f"Total gastado en compras: ${total_compra_anim:10.2f}")
        stdscr.addstr(h // 2 - 2, w // 2 - 20, f"Total ganado en ventas:   ${total_venta_anim:10.2f}")
        stdscr.addstr(h // 2,     w // 2 - 20, f"Balance neto: ${ganancia_anim:10.2f}", color_ganancia)
        stdscr.refresh()
        curses.napms(20)

    stdscr.addstr(h // 2 - 3, w // 2 - 20, f"Total gastado en compras: ${compras:10.2f}")
    stdscr.addstr(h // 2 - 2, w // 2 - 20, f"Total ganado en ventas:   ${ventas:10.2f}")
    stdscr.addstr(h // 2,     w // 2 - 20, f"Balance neto: ${ganancia:10.2f}", color_ganancia | curses.A_BOLD)

    if ganancia > 0:
        msg = "💰 ¡Excelente! El negocio está en ganancia."
    elif ganancia == 0:
        msg = "⚖️  El balance está equilibrado."
    else:
        msg = "📉 Cuidado, hay pérdida en el balance."

    stdscr.addstr(h // 2 + 3, w // 2 - len(msg)//2, msg, color_ganancia | curses.A_BOLD)
    stdscr.addstr(h - 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
    stdscr.refresh()
    stdscr.getch()


def necesidad_compra(stdscr, inventario):
    stdscr.clear()
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()

    productos_bajos = obtener_productos_bajo_stock(inventario, umbral=10)

    titulo = "📦 NECESIDAD DE COMPRA 📦"
    subtitulo = "Productos con stock menor a 10 unidades"
    cabecera = "Código   Nombre                  Cantidad   Precio"

    stdscr.addstr(h // 2 - 8, w // 2 - len(titulo)//2, titulo, curses.A_BOLD | curses.color_pair(2))
    stdscr.addstr(h // 2 - 6, w // 2 - len(subtitulo)//2, subtitulo, curses.A_DIM)

    if not productos_bajos:
        msg = "✅ Todos los productos tienen suficiente stock."
        for i in range(1, len(msg)+1):
            stdscr.addstr(h // 2, w // 2 - len(msg)//2, msg[:i], curses.color_pair(2))
            stdscr.refresh()
            curses.napms(20)
        stdscr.addstr(h - 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
        stdscr.getch()
        return

    stdscr.addstr(h // 2 - 3, w // 2 - len(cabecera)//2, cabecera, curses.A_BOLD)
    stdscr.addstr(h // 2 - 2, w // 2 - len(cabecera)//2, "-" * len(cabecera))

    fila_y = h // 2
    for p in productos_bajos:
        linea = f"{p.get('codigo',''):<8}{p.get('nombre',''):<22}{p.get('cantidad',0):<10}{p.get('precio',0):<10.2f}"
        stdscr.addstr(fila_y, w // 2 - len(linea)//2, linea, curses.color_pair(1))
        stdscr.refresh()
        curses.napms(80)
        fila_y += 1

    msg = "⚠️  Reponer estos productos lo antes posible."
    for i in range(1, len(msg)+1):
        stdscr.addstr(fila_y + 2, w // 2 - len(msg)//2, msg[:i], curses.color_pair(1) | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(15)

    stdscr.addstr(h - 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
    stdscr.refresh()
    stdscr.getch()


def menu(stdscr):
    animacion_inicio(stdscr)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    inventario = cargar_inventario()
    opciones = [
        "Mostrar inventario",
        "Comprar producto",
        "Vender producto",
        "Eliminar producto",
        "Necesidad de compra",
        "Mostrar balance",
        "Salir"
    ]
    seleccion = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.border()

        titulo = "=== CONTROL DE STOCK EXOLGAN S.A. ==="
        stdscr.addstr(1, w//2 - len(titulo)//2, titulo, curses.color_pair(1) | curses.A_BOLD)

        for i, op in enumerate(opciones):
            x = w//2 - len(op)//2
            y = h//2 - len(opciones)//2 + i
            if i == seleccion:
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(y, x, f"> {op} <")
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                stdscr.addstr(y, x, f"  {op}  ")

        stdscr.refresh()

        tecla = stdscr.getch()

        if tecla == curses.KEY_UP and seleccion > 0:
            seleccion -= 1
        elif tecla == curses.KEY_DOWN and seleccion < len(opciones) - 1:
            seleccion += 1
        elif tecla in [10, 13]:  # Enter
            if seleccion == 0:
                mostrar_inventario(stdscr, inventario)
            elif seleccion == 1:
                comprar_producto(stdscr, inventario)
            elif seleccion == 2:
                vender_producto_ui(stdscr, inventario)
            elif seleccion == 3:
                eliminar_producto_ui(stdscr, inventario)
            elif seleccion == 4:
                necesidad_compra(stdscr, inventario)
            elif seleccion == 5:
                mostrar_balance_ui(stdscr)
            elif seleccion == 6:
                guardar_inventario(inventario)
                break


if __name__ == "__main__":
    curses.wrapper(menu)
