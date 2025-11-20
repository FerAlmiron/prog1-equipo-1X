# test_digital_stock.py
import unittest
import os
import json
import tempfile
from digital_stock import (
    cargar_inventario,
    guardar_inventario,
    agregar_producto,
    buscar_producto,
    vender_producto_logico,
    eliminar_producto_logico,
    calcular_balance,
    registrar_transaccion,
)

class TestDigitalStockCore(unittest.TestCase):

    def setUp(self):
        # crear archivos temporales
        self.inv_fd, self.inv_path = tempfile.mkstemp(suffix=".json")
        os.close(self.inv_fd)
        self.bal_fd, self.bal_path = tempfile.mkstemp(suffix=".json")
        os.close(self.bal_fd)

        # iniciar inventario simple
        self.inventario = [
            {"codigo":"A1", "nombre":"Producto A", "cantidad": 5, "precio": 10.0},
            {"codigo":"B2", "nombre":"Producto B", "cantidad": 20, "precio": 5.0}
        ]
        guardar_inventario(self.inventario, filename=self.inv_path)

    def tearDown(self):
        try:
            os.remove(self.inv_path)
        except OSError:
            pass
        try:
            os.remove(self.bal_path)
        except OSError:
            pass

    def test_cargar_guardar(self):
        inv = cargar_inventario(filename=self.inv_path)
        self.assertIsInstance(inv, list)
        self.assertEqual(len(inv), 2)
        self.assertEqual(inv[0]["codigo"], "A1")

    def test_agregar_producto(self):
        inv = cargar_inventario(filename=self.inv_path)
        nuevo = {"codigo":"C3","nombre":"Producto C","cantidad":10,"precio":2.5}
        agregar_producto(inv, nuevo, inventario_file=self.inv_path, balance_file=self.bal_path)
        inv2 = cargar_inventario(filename=self.inv_path)
        self.assertEqual(len(inv2), 3)
        p = buscar_producto("C3", inv2)
        self.assertIsNotNone(p)
        # balance debe tener registro de compra
        compras, ventas = calcular_balance(filename=self.bal_path)
        self.assertGreater(compras, 0)

    def test_vender_producto_logico(self):
        inv = cargar_inventario(filename=self.inv_path)
        # vender 2 de A1 a precio 12
        vender_producto_logico("A1", 2, 12.0, inv, inventario_file=self.inv_path, balance_file=self.bal_path)
        inv2 = cargar_inventario(filename=self.inv_path)
        p = buscar_producto("A1", inv2)
        self.assertEqual(p["cantidad"], 3)
        compras, ventas = calcular_balance(filename=self.bal_path)
        self.assertGreater(ventas, 0)

    def test_eliminar_producto_logico(self):
        inv = cargar_inventario(filename=self.inv_path)
        eliminar_producto_logico("A1", inv, inventario_file=self.inv_path)
        inv2 = cargar_inventario(filename=self.inv_path)
        self.assertIsNone(buscar_producto("A1", inv2))

    def test_registrar_transaccion_manual(self):
        registrar_transaccion("COMPRA", "X1", "Test", 1, 100.0, filename=self.bal_path)
        compras, ventas = calcular_balance(filename=self.bal_path)
        self.assertEqual(compras, 100.0)

if __name__ == "__main__":
    unittest.main()
