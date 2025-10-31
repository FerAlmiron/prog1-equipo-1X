import curses
import os
import time
import re

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
        time.sleep(0.04)

    time.sleep(0.6)
    stdscr.clear()
    stdscr.refresh()
# --- Funciones de archivo ---
def cargar_inventario():
    inventario = []
    try:
        with open("inventario.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")
                if len(datos) == 4:
                    codigo, nombre, cantidad, precio = datos
                    inventario.append([codigo, nombre, int(cantidad), float(precio)])
    except FileNotFoundError:
        pass
    return inventario


def guardar_inventario(inventario):
    with open("inventario.txt", "w", encoding="utf-8") as f:
        for p in inventario:
            f.write(f"{p[0]},{p[1]},{p[2]},{p[3]}\n")


def registrar_transaccion(tipo, codigo, nombre, cantidad, monto):
    with open("balance.txt", "a", encoding="utf-8") as f:
        f.write(f"{tipo},{codigo},{nombre},{cantidad},{monto}\n")


def calcular_balance():
    total_compra = 0
    total_venta = 0
    try:
        with open("balance.txt", "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")
                if len(datos) == 5:
                    tipo, _, _, _, monto = datos
                    if tipo == "COMPRA":
                        total_compra += float(monto)
                    elif tipo == "VENTA":
                        total_venta += float(monto)
    except FileNotFoundError:
        pass
    return total_compra, total_venta


# --- Funciones auxiliares ---
def buscar_producto(codigo, inventario):
    for p in inventario:
        if p[0].lower() == codigo.lower():
            return p
    return None


# --- Mostrar inventario ---
def mostrar_inventario(stdscr, inventario):
    stdscr.clear()
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()

    titulo = "📦 INVENTARIO ACTUAL 📦"
    cabecera = "Código   Nombre               Cantidad   Precio"

    # Calcular posiciones centradas
    x_titulo = w // 2 - len(titulo) // 2
    x_cabecera = w // 2 - len(cabecera) // 2
    y_inicio = h // 2 - (len(inventario) // 2) - 2

    # Mostrar título y cabecera
    stdscr.addstr(y_inicio - 2, x_titulo, titulo, curses.A_BOLD | curses.color_pair(2))
    stdscr.addstr(y_inicio, x_cabecera, cabecera, curses.A_BOLD)
    stdscr.addstr(y_inicio + 1, x_cabecera, "-" * len(cabecera))

    # Animar los productos uno por uno
    fila_y = y_inicio + 2
    for p in inventario:
        codigo, nombre, cantidad, precio = p
        color = curses.color_pair(1) if cantidad < 10 else curses.color_pair(0)

        linea = f"{codigo:<8}{nombre:<20}{cantidad:<10}{precio:<10.2f}"
        x_linea = w // 2 - len(linea) // 2
        stdscr.addstr(fila_y, x_linea, linea, color)
        stdscr.refresh()
        fila_y += 1
        curses.napms(80)  # Pequeña pausa entre líneas (80 ms)

    # Si el inventario está vacío
    if not inventario:
        msg = "🚫 No hay productos registrados."
        stdscr.addstr(h // 2, w // 2 - len(msg) // 2, msg, curses.color_pair(1) | curses.A_BOLD)

    # Mensaje final
    stdscr.addstr(fila_y + 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
    stdscr.refresh()
    stdscr.getch()


# --- Comprar producto ---
def comprar_producto(stdscr, inventario):
    stdscr.clear()
    curses.echo()
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()

    try:
        # --- Encabezado ---
        stdscr.addstr(0, 0, "=== Registrar Compra ===", curses.A_BOLD)

        # --- Código del producto ---
        stdscr.addstr(2, 0, "Código del producto: ")
        codigo = stdscr.getstr(2, 25, 20).decode("utf-8").strip()
        if not codigo:
            raise ValueError("El código no puede estar vacío.")
        if not re.match(r'^[A-Za-z0-9\-]+$', codigo):
            raise ValueError("El código solo puede contener letras, números o guiones (sin espacios ni símbolos).")

        # --- Validar duplicado ---
        existente = buscar_producto(codigo, inventario)
        if existente:
            raise ValueError(f"El código '{codigo}' ya existe en el inventario ({existente[1]}).")

        # --- Nombre ---
        stdscr.addstr(3, 0, "Nombre del producto: ")
        nombre = stdscr.getstr(3, 25, 20).decode("utf-8").strip()
        if not nombre:
            raise ValueError("El nombre no puede estar vacío.")

        # --- Cantidad ---
        stdscr.addstr(4, 0, "Cantidad comprada: ")
        cant_str = stdscr.getstr(4, 25, 10).decode("utf-8").strip()
        if not cant_str.isdigit():
            raise ValueError("La cantidad debe ser un número entero.")
        cantidad = int(cant_str)
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        # --- Precio ---
        stdscr.addstr(5, 0, "Precio unitario de compra: ")
        precio_str = stdscr.getstr(5, 30, 10).decode("utf-8").strip()
        if not precio_str:
            raise ValueError("El precio no puede estar vacío.")
        precio = float(precio_str)
        if precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")

        # --- Registrar producto ---
        inventario.append([codigo, nombre, cantidad, precio])
        guardar_inventario(inventario)
        registrar_transaccion("COMPRA", codigo, nombre, cantidad, precio * cantidad)

        # --- Animación visual ---
        stdscr.clear()
        msg = "💾 Guardando compra..."
        stdscr.addstr(h // 2 - 2, w // 2 - len(msg)//2, msg, curses.color_pair(2) | curses.A_BOLD)

        for i in range(0, 51):
            barra = "#" * i
            stdscr.addstr(h // 2, w // 2 - 25, f"[{barra:<50}] {i*2:>3}%", curses.color_pair(2))
            stdscr.refresh()
            curses.napms(25)

        stdscr.addstr(h // 2 + 2, w // 2 - 15, "✅ Compra registrada correctamente.", curses.color_pair(2))
        stdscr.refresh()
        curses.napms(1000)

    except ValueError as e:
        stdscr.addstr(8, 0, f"⚠️ Error: {e}", curses.color_pair(1))
    except Exception as e:
        stdscr.addstr(8, 0, f"⚠️ Error inesperado: {e}", curses.color_pair(1))
    finally:
        curses.noecho()
        curses.curs_set(0)
        stdscr.addstr(h - 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()

# --- Vender producto ---
def vender_producto(stdscr, inventario):
    stdscr.clear()
    curses.echo()
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()

    try:
        # --- Encabezado ---
        stdscr.addstr(0, 0, "=== Registrar Venta ===", curses.A_BOLD)

        # --- Código del producto ---
        stdscr.addstr(2, 0, "Código del producto: ")
        codigo = stdscr.getstr(2, 25, 20).decode("utf-8").strip()
        if not codigo:
            raise ValueError("El código no puede estar vacío.")

        # Buscar el producto
        producto = buscar_producto(codigo, inventario)
        if not producto:
            raise ValueError("El producto no existe en el inventario.")

        # --- Cantidad ---
        stdscr.addstr(3, 0, "Cantidad vendida: ")
        cant_str = stdscr.getstr(3, 25, 10).decode("utf-8").strip()
        if not cant_str.isdigit():
            raise ValueError("La cantidad debe ser un número entero.")
        cantidad = int(cant_str)
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        # Verificar stock disponible
        if producto[2] < cantidad:
            raise ValueError(f"No hay suficiente stock. (Stock actual: {producto[2]})")

        # --- Precio ---
        stdscr.addstr(4, 0, "Precio unitario de venta: ")
        precio_str = stdscr.getstr(4, 30, 10).decode("utf-8").strip()
        if not precio_str:
            raise ValueError("El precio no puede estar vacío.")
        precio = float(precio_str)
        if precio <= 0:
            raise ValueError("El precio debe ser mayor que cero.")

        # --- Actualizar inventario y registrar venta ---
        producto[2] -= cantidad
        guardar_inventario(inventario)
        registrar_transaccion("VENTA", codigo, producto[1], cantidad, precio * cantidad)

        # --- Animación de registro ---
        stdscr.clear()
        msg = "📦 Registrando venta..."
        stdscr.addstr(h // 2 - 2, w // 2 - len(msg)//2, msg, curses.color_pair(2) | curses.A_BOLD)
        stdscr.refresh()

        for i in range(0, 51):
            barra = "#" * i
            stdscr.addstr(h // 2, w // 2 - 25, f"[{barra:<50}] {i*2:>3}%", curses.color_pair(2))
            stdscr.refresh()
            curses.napms(25)

        stdscr.addstr(h // 2 + 2, w // 2 - 15, "✅ Venta registrada correctamente.", curses.color_pair(2))
        stdscr.refresh()
        curses.napms(1000)

    except ValueError as e:
        stdscr.addstr(8, 0, f"⚠️ Error: {e}", curses.color_pair(1))
    except Exception as e:
        stdscr.addstr(8, 0, f"⚠️ Error inesperado: {e}", curses.color_pair(1))
    finally:
        curses.noecho()
        curses.curs_set(0)
        stdscr.addstr(h - 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()

# --- Eliminar producto ---
def eliminar_producto(stdscr, inventario):
    stdscr.clear()
    curses.echo()
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()

    try:
        # --- Encabezado ---
        titulo = "=== Eliminar Producto del Inventario ==="
        stdscr.addstr(0, w // 2 - len(titulo)//2, titulo, curses.A_BOLD)

        # --- Solicitar código ---
        stdscr.addstr(2, 0, "Ingrese el código del producto a eliminar: ")
        codigo = stdscr.getstr(2, 45, 20).decode("utf-8").strip()

        if not codigo:
            raise ValueError("El código no puede estar vacío.")

        # --- Buscar producto ---
        encontrado = None
        for i, p in enumerate(inventario):
            if p[0].lower() == codigo.lower():
                encontrado = (i, p)
                break

        if not encontrado:
            raise ValueError("No se encontró ningún producto con ese código.")

        # --- Confirmación antes de eliminar ---
        stdscr.addstr(4, 0, f"¿Seguro que desea eliminar '{encontrado[1][1]}'? (s/n): ")
        tecla = stdscr.getch()
        if chr(tecla).lower() != "s":
            stdscr.addstr(6, 0, "Operación cancelada.", curses.color_pair(1))
            return

        # --- Eliminar producto ---
        inventario.pop(encontrado[0])
        guardar_inventario(inventario)

        # --- Animación visual ---
        stdscr.clear()
        msg = "🗑️ Eliminando producto..."
        stdscr.addstr(h // 2 - 2, w // 2 - len(msg)//2, msg, curses.color_pair(2) | curses.A_BOLD)
        stdscr.refresh()

        for i in range(0, 51):
            barra = "#" * i
            stdscr.addstr(h // 2, w // 2 - 25, f"[{barra:<50}] {i*2:>3}%", curses.color_pair(2))
            stdscr.refresh()
            curses.napms(25)

        stdscr.addstr(h // 2 + 2, w // 2 - 20, f"✅ Producto '{encontrado[1][1]}' eliminado correctamente.", curses.color_pair(2))
        stdscr.refresh()
        curses.napms(1000)

    except ValueError as e:
        stdscr.addstr(8, 0, f"⚠️ Error: {e}", curses.color_pair(1))
    except Exception as e:
        stdscr.addstr(8, 0, f"⚠️ Error inesperado: {e}", curses.color_pair(1))
    finally:
        curses.noecho()
        curses.curs_set(0)
        stdscr.addstr(h - 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()


# --- Mostrar balance ---
def mostrar_balance(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    h, w = stdscr.getmaxyx()

    # Calcular totales
    compras, ventas = calcular_balance()
    ganancia = ventas - compras

    # Colores
    color_ganancia = curses.color_pair(2) if ganancia >= 0 else curses.color_pair(1)

    # --- Encabezado ---
    titulo = "=== BALANCE GENERAL ==="
    stdscr.addstr(h // 2 - 6, w // 2 - len(titulo)//2, titulo, curses.A_BOLD)

    # --- Animación de conteo ---
    duracion = 40  # velocidad de animación
    total_compra_anim = 0
    total_venta_anim = 0

    for i in range(1, duracion + 1):
        total_compra_anim = compras * (i / duracion)
        total_venta_anim = ventas * (i / duracion)
        ganancia_anim = total_venta_anim - total_compra_anim

        stdscr.addstr(h // 2 - 3, w // 2 - 20, f"Total gastado en compras: ${total_compra_anim:10.2f}")
        stdscr.addstr(h // 2 - 2, w // 2 - 20, f"Total ganado en ventas:   ${total_venta_anim:10.2f}")
        stdscr.addstr(h // 2,     w // 2 - 20, f"Balance neto: ${ganancia_anim:10.2f}", color_ganancia)

        stdscr.refresh()
        curses.napms(25)

    # --- Mostrar valores finales ---
    stdscr.addstr(h // 2 - 3, w // 2 - 20, f"Total gastado en compras: ${compras:10.2f}")
    stdscr.addstr(h // 2 - 2, w // 2 - 20, f"Total ganado en ventas:   ${ventas:10.2f}")
    stdscr.addstr(h // 2,     w // 2 - 20, f"Balance neto: ${ganancia:10.2f}", color_ganancia | curses.A_BOLD)

    # Mensaje según resultado
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

    # Filtrar productos con bajo stock
    productos_bajos = [p for p in inventario if p[2] < 10]

    # Títulos
    titulo = "📦 NECESIDAD DE COMPRA 📦"
    subtitulo = "Productos con stock menor a 10 unidades"
    cabecera = "Código   Nombre                  Cantidad   Precio"

    stdscr.addstr(h // 2 - 8, w // 2 - len(titulo)//2, titulo, curses.A_BOLD | curses.color_pair(2))
    stdscr.addstr(h // 2 - 6, w // 2 - len(subtitulo)//2, subtitulo, curses.A_DIM)

    # Si no hay productos con bajo stock
    if not productos_bajos:
        msg = "✅ Todos los productos tienen suficiente stock."
        for i in range(1, len(msg)+1):
            stdscr.addstr(h // 2, w // 2 - len(msg)//2, msg[:i], curses.color_pair(2))
            stdscr.refresh()
            curses.napms(30)
        stdscr.addstr(h - 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
        stdscr.refresh()
        stdscr.getch()
        return

    # Cabecera centrada
    stdscr.addstr(h // 2 - 3, w // 2 - len(cabecera)//2, cabecera, curses.A_BOLD)
    stdscr.addstr(h // 2 - 2, w // 2 - len(cabecera)//2, "-" * len(cabecera))

    # --- Animación de productos ---
    fila_y = h // 2
    for p in productos_bajos:
        codigo, nombre, cantidad, precio = p
        linea = f"{codigo:<8}{nombre:<22}{cantidad:<10}{precio:<10.2f}"
        stdscr.addstr(fila_y, w // 2 - len(linea)//2, linea, curses.color_pair(1))
        stdscr.refresh()
        curses.napms(100)  # efecto progresivo
        fila_y += 1

    # --- Mensaje final animado ---
    msg = "⚠️  Reponer estos productos lo antes posible."
    for i in range(1, len(msg)+1):
        stdscr.addstr(fila_y + 2, w // 2 - len(msg)//2, msg[:i], curses.color_pair(1) | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(25)

    stdscr.addstr(h - 2, w // 2 - 20, "Presione una tecla para continuar...", curses.A_DIM)
    stdscr.refresh()
    stdscr.getch()

# --- Menú principal ---
def menu(stdscr):
    animacion_inicio(stdscr)  # 👈 Intro animada
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
                vender_producto(stdscr, inventario)
            elif seleccion == 3:
                eliminar_producto(stdscr, inventario)
            elif seleccion == 4:
                necesidad_compra(stdscr, inventario)
            elif seleccion == 5:
                mostrar_balance(stdscr)
            elif seleccion == 6:
                guardar_inventario(stdscr)
                break


if __name__ == "__main__":
    curses.wrapper(menu)
