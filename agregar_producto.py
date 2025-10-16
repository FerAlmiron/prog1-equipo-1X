import curses

def agregar_producto(stdscr):
stdscr.clear()

# Código
stdscr.addstr(0, 0, "Ingrese código: ")
codigo = int(stdscr.getstr(0, 20, 10)) # convierte directo a int

# Nombre
stdscr.addstr(1, 0, "Ingrese nombre: ")
nombre = stdscr.getstr(1, 20, 20).decode("utf-8") # texto -> decode

# Cantidad
stdscr.addstr(2, 0, "Ingrese cantidad: ")
cantidad = int(stdscr.getstr(2, 20, 10)) # int directo

# Precio
stdscr.addstr(3, 0, "Ingrese precio: ")
precio = float(stdscr.getstr(3, 20, 10)) # float directo

# Mostrar lo ingresado
stdscr.clear()
stdscr.addstr(0, 0, f"Producto agregado:")
stdscr.addstr(1, 0, f"Código: {codigo}")
stdscr.addstr(2, 0, f"Nombre: {nombre}")
stdscr.addstr(3, 0, f"Cantidad: {cantidad}")
stdscr.addstr(4, 0, f"Precio: {precio}")
stdscr.refresh()
stdscr.getch()

curses.wrapper(agregar_producto)