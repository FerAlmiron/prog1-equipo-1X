import curses

# --- Funciones del inventario ---

def mostrar_inventario(stdscr, inventario):
    stdscr.clear()
    stdscr.addstr(0, 0, "Código   Nombre               Cantidad   Precio\n")
    stdscr.addstr(1, 0, "-" * 50)
    fila = 2
    for producto in inventario:
        codigo, nombre, cantidad, precio = producto
        stdscr.addstr(fila, 0, f"{codigo:<8}{nombre:<20}{cantidad:<10}{precio:<10.2f}")
        fila += 1
    stdscr.addstr(fila + 1, 0, "Presione una tecla para continuar...")
    stdscr.getch()


def buscar_producto(stdscr, inventario):
    stdscr.clear()
    stdscr.addstr(0, 0, "Buscar producto por código o nombre: ")
    curses.echo()
    criterio = stdscr.getstr(1, 0, 20).decode("utf-8").lower()
    curses.noecho()

    resultados = []
    for p in inventario:
        if criterio in p[0].lower() or criterio in p[1].lower():
            resultados.append(p)

    stdscr.clear()
    if resultados:
        mostrar_inventario(stdscr, resultados)
    else:
        stdscr.addstr(0, 0, "No se encontró el producto.")
        stdscr.getch()


def eliminar_producto(stdscr, inventario):
    stdscr.clear()
    stdscr.addstr(0, 0, "Ingrese el código o nombre del producto a eliminar: ")
    curses.echo()
    criterio = stdscr.getstr(1, 0, 20).decode("utf-8").lower()
    curses.noecho()

    for i, p in enumerate(inventario):
        if criterio in p[0].lower() or criterio in p[1].lower():
            eliminado = inventario.pop(i)
            stdscr.addstr(3, 0, f"Producto '{eliminado[1]}' eliminado correctamente.")
            guardar_inventario(inventario)
            stdscr.getch()
            return

    stdscr.addstr(3, 0, "No se encontró el producto.")
    stdscr.getch()


def agregar_producto(stdscr, inventario):
    stdscr.clear()
    stdscr.addstr(0, 0, "Agregar nuevo producto:")
    curses.echo()

    stdscr.addstr(2, 0, "Código: ")
    codigo = stdscr.getstr(2, 10, 20).decode("utf-8")

    stdscr.addstr(3, 0, "Nombre: ")
    nombre = stdscr.getstr(3, 10, 20).decode("utf-8")

    stdscr.addstr(4, 0, "Cantidad: ")
    cantidad = int(stdscr.getstr(4, 10, 10).decode("utf-8"))

    stdscr.addstr(5, 0, "Precio: ")
    precio = float(stdscr.getstr(5, 10, 10).decode("utf-8"))

    curses.noecho()

    inventario.append([codigo, nombre, cantidad, precio])
    guardar_inventario(inventario)
    stdscr.addstr(7, 0, f"Producto '{nombre}' agregado con éxito.")
    stdscr.getch()


# --- Funciones de archivo (lectura y escritura básica) ---

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
            linea = f"{p[0]},{p[1]},{p[2]},{p[3]}\n"
            f.write(linea)


# --- Menú principal ---

def menu(stdscr):
    inventario = cargar_inventario()
    opciones = [
        "1. Mostrar inventario",
        "2. Buscar producto",
        "3. Agregar producto",
        "4. Eliminar producto",
        "5. Salir"
    ]

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "=== CONTROL DE STOCK ===\n", curses.A_BOLD)
        for i, op in enumerate(opciones, start=2):
            stdscr.addstr(i, 0, op)
        stdscr.addstr(8, 0, "Seleccione una opción: ")

        key = stdscr.getch()

        if key == ord('1'):
            mostrar_inventario(stdscr, inventario)
        elif key == ord('2'):
            buscar_producto(stdscr, inventario)
        elif key == ord('3'):
            agregar_producto(stdscr, inventario)
        elif key == ord('4'):
            eliminar_producto(stdscr, inventario)
        elif key == ord('5'):
            guardar_inventario(inventario)
            break


# --- Inicio del programa ---
if __name__ == "__main__":
    curses.wrapper(menu)
