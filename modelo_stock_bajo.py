import curses

limite = 5

productos = [
    {"nombre": "Monitor 24''", "stock": 12},
    {"nombre": "Mouse optico", "stock": 3},
    {"nombre": "Teclado", "stock": 5},
    {"nombre": "Notebook", "stock": 0},
    {"nombre": "Camara", "stock": 8}
]

def verBajos(lista ):
  bajos = []
  for i in lista:
     if i["stock"] <= limite:
        bajos.append(i)
  return bajos

def mostrarBajos(pantalla):
    pantalla.clear()
    pantalla.addstr("Productos con poco STOCK\n\n")

    bajos = verBajos(productos)

    if bajos == []:
        pantalla.addstr("No hay productos bajos \n")
    else:
        for i in bajos:
            pantalla.addstr( " - " + i["nombre"] + " : " + str(i["stock"]) + " uds\n")

    pantalla.addstr("\nPresione tecla para volver...")
    pantalla.refresh()
    pantalla.getch()

def menu(pantalla):
   curses.curs_set(0)
   op = 0
   opciones = ["Ver stock bajo","Salir" ]

   while True:
        pantalla.clear()
        pantalla.addstr("MENU PRINCIPAL\n\n")

        for i in range(len(opciones)):
            if i==op:
                pantalla.addstr("> " + opciones[i] + "\n", curses.A_REVERSE)
            else:
                pantalla.addstr("  " + opciones[i] + "\n")

        t = pantalla.getch()

        if t == curses.KEY_UP:
            op = (op - 1) % len(opciones)
        elif t == curses.KEY_DOWN:
            op = (op + 1) % len(opciones)
        elif t == 10:
            if op == 0:
                mostrarBajos(pantalla)
            elif op == 1:
                break

   pantalla.clear()
   pantalla.addstr("saliendo... \n")
   pantalla.refresh()
   curses.napms(1000)

def test():
   print ("probando modulo de stock bajo")
   lista1 = []
   print("caso1:", verBajos(lista1))
   lista2 = [{"nombre":"A","stock":6}]
   print ("caso2:",verBajos(lista2))
   lista3 = [{"nombre":"B","stock":5},{"nombre":"C","stock":1}]
   print("caso3:",verBajos(lista3))
   lista4 = [{"nombre":"D","stock":0}]
   print ("caso4:",verBajos(lista4))
   print ("todo bien creo jaja")

if __name__ == "__main__":
    test()
    curses.wrapper(menu)