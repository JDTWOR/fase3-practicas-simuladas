# Fase 3 — Prácticas simuladas

Estudiante: Jhon Deivid Rojas Rodriguez. Grupo: 301305_298.

Aplicación de escritorio en Python para registrar afiliados de la Caja Compensándote y practicar tres estructuras lineales: pila, cola y lista. La interfaz permite elegir la estructura activa, registrar afiliados, consultar su reporte y retirar registros según las reglas de cada estructura.

## Ejecutar

Requiere Python 3 y Tkinter. La aplicación usa `tkcalendar` de forma opcional para mostrar un selector de fecha; sin esa biblioteca, presenta controles alternativos.

```bash
python -m pip install -r requirements.txt
python main.py
```

Los datos se mantienen en memoria mientras la aplicación está abierta.

## Estructuras

- **Pila:** usa una lista de Python y retira el último registro agregado (LIFO).
- **Cola:** usa `collections.deque` y retira el primer registro agregado (FIFO).
- **Lista:** permite buscar y retirar un afiliado por número de identificación.

La aplicación calcula la cuota a partir del rango de ingresos, la modalidad laboral y el servicio elegido.

## Archivos principales

- `main.py`: interfaz y manejo de eventos.
- `affiliate_data_structure.py`: afiliados, validaciones, estructuras y reportes.
- `test_affiliate_data_structure.py` y `test_gui_smoke.py`: comprobaciones incluidas con el proyecto.

La clave del formulario es un valor fijo de demostración definido en el código; no es autenticación real ni debe reutilizarse en otros servicios.
