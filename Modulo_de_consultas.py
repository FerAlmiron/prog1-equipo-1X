import curses
def mostrar_inventario(stdscr, inventario):
    stdscr.clear()
    headers = ["Código", "Nombre", "Cantidad", "Precio"]
    col_widths = [10, 20, 10, 10]
    # Encabezados
    x = 0
    for i, h in enumerate(headers):
        stdscr.addstr(0, x, h.ljust(col_widths[i]))
        x += col_widths[i]
    # Filas
    for row_idx, producto in enumerate(inventario, start=1):
        x = 0
        for i, valor in enumerate(producto):
            stdscr.addstr(row_idx, x, str(valor).ljust(col_widths[i]))
            x += col_widths[i]

    stdscr.refresh()
    stdscr.getch()
def buscar_producto(stdscr, inventario):
    stdscr.clear()
    stdscr.addstr(0, 0, "Buscar producto (código o nombre): ")
    curses.echo()  # habilita que lo que escribas se vea
    criterio = stdscr.getstr(1, 0, 20).decode("utf-8")  # lee input
    curses.noecho()  # desactiva la escritura visible

    resultados = []
    for i in range(len(inventario)):  # recorremos por índice
        producto = inventario[i]
        codigo = str(producto[0]).lower()
        nombre = str(producto[1]).lower()

        if criterio.lower() in codigo or criterio.lower() in nombre:
            resultados.append(producto)

    stdscr.clear()
    if resultados:
        mostrar_inventario(stdscr, resultados)  # reutilizamos tu función
    else:
        stdscr.addstr(0, 0, "No se encontró el producto.")
        stdscr.getch()