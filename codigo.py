import queue
import time
import random
from datetime import datetime, timedelta
import threading

class Paquete:
    def __init__(self, id_paquete, nombre, tipo, fecha_ingreso, fecha_vencimiento=None):
        self.id = id_paquete
        self.nombre = nombre
        self.tipo = tipo  # 'normal', 'perecedero', 'devolucion'
        self.fecha_ingreso = fecha_ingreso
        self.fecha_vencimiento = fecha_vencimiento

    def __str__(self):
        if self.fecha_vencimiento:
            return f"Paquete {self.id}: {self.nombre} (Vence: {self.fecha_vencimiento.strftime('%Y-%m-%d')})"
        return f"Paquete {self.id}: {self.nombre}"

class SimuladorAlmacen:
    def __init__(self, nombre_almacen):
        self.nombre = nombre_almacen
        self.cola_fifo = queue.Queue()
        self.cola_lifo = queue.LifoQueue()
        self.paquetes_procesados_fifo = []
        self.paquetes_procesados_lifo = []

    def agregar_paquete(self, paquete, usar_fifo=True):
        """Agrega un paquete al almacén"""
        if usar_fifo:
            self.cola_fifo.put(paquete)
            print(f"[{self.nombre}] Paquete {paquete.id} agregado a COLA FIFO")
        else:
            self.cola_lifo.put(paquete)
            print(f"[{self.nombre}] Paquete {paquete.id} agregado a COLA LIFO")

    def despachar_paquete(self, usar_fifo=True):
        """Despacha un paquete del almacén"""
        try:
            if usar_fifo:
                if not self.cola_fifo.empty():
                    paquete = self.cola_fifo.get(timeout=1)
                    self.paquetes_procesados_fifo.append(paquete)
                    print(f"[{self.nombre}] Despachado (FIFO): {paquete}")
                    return paquete
            else:
                if not self.cola_lifo.empty():
                    paquete = self.cola_lifo.get(timeout=1)
                    self.paquetes_procesados_lifo.append(paquete)
                    print(f"[{self.nombre}] Despachado (LIFO): {paquete}")
                    return paquete
        except queue.Empty:
            print(f"[{self.nombre}] No hay paquetes para despachar")
            return None

    def mostrar_estado(self):
        """Muestra el estado actual del almacén"""
        print(f"\n=== Estado del Almacén {self.nombre} ===")
        print(f"Paquetes en FIFO: {self.cola_fifo.qsize()}")
        print(f"Paquetes en LIFO: {self.cola_lifo.qsize()}")
        print(f"Procesados FIFO: {len(self.paquetes_procesados_fifo)}")
        print(f"Procesados LIFO: {len(self.paquetes_procesados_lifo)}")

    def verificar_vencidos(self):
        """Verifica si hay paquetes vencidos en el almacén"""
        vencidos_fifo = 0
        vencidos_lifo = []

        # Revisar FIFO (no podemos ver el interior sin sacarlos)
        print("\n[ADVERTENCIA] Revisando paquetes vencidos...")

        # Simular revisión de LIFO (podemos ver el último)
        try:
            paquetes_temp = []
            while not self.cola_lifo.empty():
                paquete = self.cola_lifo.get()
                if paquete.fecha_vencimiento and paquete.fecha_vencimiento < datetime.now():
                    vencidos_lifo.append(paquete)
                    print(f"¡ALERTA! Paquete vencido encontrado en LIFO: {paquete}")
                else:
                    paquetes_temp.append(paquete)

            # Devolver paquetes no vencidos
            for p in reversed(paquetes_temp):
                self.cola_lifo.put(p)

        except queue.Empty:
            pass

        return len(vencidos_lifo)

def generar_paquetes(cantidad, tipo_paquete='normal'):
    """Genera una lista de paquetes para pruebas"""
    paquetes = []
    tipos_producto = {
        'normal': ['Libro', 'Ropa', 'Electrónica', 'Juguete', 'Herramienta'],
        'perecedero': ['Leche', 'Yogurt', 'Fruta', 'Verdura', 'Carne'],
        'devolucion': ['Teléfono', 'Tablet', 'Zapatos', 'Lámpara', 'Silla']
    }

    fecha_base = datetime.now()

    for i in range(cantidad):
        nombre = random.choice(tipos_producto[tipo_paquete])
        fecha_ingreso = fecha_base + timedelta(hours=i)

        # Para perecederos, agregar fecha de vencimiento
        fecha_vencimiento = None
        if tipo_paquete == 'perecedero':
            fecha_vencimiento = fecha_ingreso + timedelta(days=random.randint(1, 7))

        paquete = Paquete(
            id_paquete=f"{tipo_paquete[0].upper()}{i+1:03d}",
            nombre=nombre,
            tipo=tipo_paquete,
            fecha_ingreso=fecha_ingreso,
            fecha_vencimiento=fecha_vencimiento
        )
        paquetes.append(paquete)

    return paquetes

def escenario_pedidos_normales():
    """Escenario 1: Almacén de pedidos normales"""
    print("\n" + "="*60)
    print("ESCENARIO 1: ALMACÉN DE PEDIDOS NORMALES")
    print("="*60)

    almacen = SimuladorAlmacen("Pedidos Normales")
    paquetes = generar_paquetes(10, 'normal')

    print("\n--- Recibiendo pedidos en orden de llegada ---")
    for paquete in paquetes:
        almacen.agregar_paquete(paquete, usar_fifo=True)
        almacen.agregar_paquete(paquete, usar_fifo=False)

    print("\n--- Despachando pedidos ---")
    print("\nDespachando con FIFO (orden justo):")
    for _ in range(5):
        almacen.despachar_paquete(usar_fifo=True)
        time.sleep(0.5)

    print("\nDespachando con LIFO (último en llegar):")
    for _ in range(5):
        almacen.despachar_paquete(usar_fifo=False)
        time.sleep(0.5)

    print("\n--- ANÁLISIS ---")
    print("✓ FIFO es más justo: Los primeros clientes reciben sus pedidos primero")
    print("✓ FIFO garantiza tiempos de espera predecibles")
    print("✗ LIFO puede causar que clientes antiguos esperen indefinidamente")
    print("\nRecomendación: Usar FIFO para pedidos normales")

def escenario_perecederos():
    global datetime
    """Escenario 2: Almacén de productos perecederos"""
    print("\n" + "="*60)
    print("ESCENARIO 2: ALMACÉN DE PRODUCTOS PERECEDEROS")
    print("="*60)

    almacen = SimuladorAlmacen("Productos Perecederos")

    # Simular recepción de productos perecederos en diferentes días
    print("\n--- Semana 1: Recibiendo productos ---")
    for dia in range(1, 6):
        print(f"\nDía {dia}:")
        paquete = Paquete(
            id_paquete=f"P{dia:03d}",
            nombre="Leche",
            tipo="perecedero",
            fecha_ingreso=datetime.now() + timedelta(days=dia-1),
            fecha_vencimiento=datetime.now() + timedelta(days=dia+5)  # Vence en 5 días
        )
        almacen.agregar_paquete(paquete, usar_fifo=True)
        almacen.agregar_paquete(paquete, usar_fifo=False)

    print("\n--- Día 6: Despachando productos (simulando 5 días después) ---")
    print("\nCon FIFO (primero en entrar):")
    for _ in range(3):
        almacen.despachar_paquete(usar_fifo=True)

    print("\nCon LIFO (último en entrar):")
    for _ in range(3):
        almacen.despachar_paquete(usar_fifo=False)

    print("\n--- Verificando productos vencidos ---")
    # Avanzar el tiempo 3 días
    class DateLater(datetime):
        @classmethod
        def now(cls):
            return super().now() + timedelta(days=3)

    old_datetime = datetime
    datetime = DateLater

    vencidos = almacen.verificar_vencidos()

    # Restaurar datetime
    datetime = old_datetime

    print("\n--- ANÁLISIS ---")
    print(f"Productos vencidos encontrados en LIFO: {vencidos}")
    print("\n✓ FIFO es mejor para perecederos: los productos más antiguos salen primero")
    print("✗ LIFO puede dejar productos antiguos en el fondo hasta que se venzan")
    print("\nRecomendación: Usar FIFO para productos perecederos")

def escenario_devoluciones():
    """Escenario 3: Almacén de devoluciones"""
    print("\n" + "="*60)
    print("ESCENARIO 3: ALMACÉN DE DEVOLUCIONES")
    print("="*60)

    almacen = SimuladorAlmacen("Devoluciones")

    print("\n--- Simulando devoluciones de clientes ---")
    devoluciones = generar_paquetes(8, 'devolucion')

    for i, paquete in enumerate(devoluciones):
        almacen.agregar_paquete(paquete, usar_fifo=True)
        almacen.agregar_paquete(paquete, usar_fifo=False)

        # Simular que un repartidor recoge cada 3 devoluciones
        if (i + 1) % 3 == 0:
            print(f"\n--- Repartidor recoge devoluciones (después de {i+1} devoluciones) ---")
            print("Recogiendo con FIFO:")
            almacen.despachar_paquete(usar_fifo=True)
            print("Recogiendo con LIFO:")
            almacen.despachar_paquete(usar_fifo=False)

    print("\n--- Estado final del almacén ---")
    almacen.mostrar_estado()

    print("\n--- ANÁLISIS ---")
    print("Para optimizar espacio:")
    print("✓ LIFO es más eficiente: el repartidor recoge las devoluciones más recientes")
    print("  que están en la parte superior de la pila")
    print("✓ LIFO requiere menos movimiento de paquetes")
    print("✗ FIFO requeriría mover todos los paquetes para acceder a los primeros")
    print("\nPara optimizar tiempo:")
    print("✓ LIFO es más rápido: acceso inmediato al último paquete")
    print("✓ FIFO puede ser más lento si la cola es larga")
    print("\nRecomendación: Usar LIFO para devoluciones, a menos que haya")
    print("fechas de procesamiento prioritarias")

def main():
    print("="*60)
    print("SIMULADOR DE ALMACÉN AMAZON - FIFO vs LIFO")
    print("="*60)

    # Ejecutar los tres escenarios
    escenario_pedidos_normales()
    time.sleep(2)

    escenario_perecederos()
    time.sleep(2)

    escenario_devoluciones()

    print("\n" + "="*60)
    print("CONCLUSIONES FINALES")
    print("="*60)
    print("""
    RESUMEN DE RECOMENDACIONES:

    1. PEDIDOS NORMALES:
       → Usar FIFO para garantizar equidad con los clientes

    2. PRODUCTOS PERECEDEROS:
       → Usar FIFO para evitar pérdidas por vencimiento

    3. DEVOLUCIONES:
       → Usar LIFO para optimizar espacio y tiempo de acceso

    El sistema híbrido (FIFO + LIFO) permite optimizar
    diferentes tipos de productos según sus necesidades específicas.
    """)

if __name__ == "__main__":
    main()
