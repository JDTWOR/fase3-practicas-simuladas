# Tabla de abstracción — Fase 3

**Estudiante:** Jhon Deivid Rojas Rodriguez<br>
**Curso:** Estructura de Datos (301305)<br>
**Grupo colaborativo:** 298

**Planteamiento:** La Caja Compensándote registra afiliados, calcula su cuota según sus ingresos, modalidad laboral y servicio, y organiza los registros en pila, cola o lista.

| Clase y visibilidad | Atributos y tipos | Estructura de datos | Métodos y responsabilidad |
|---|---|---|---|
| `AffiliateDataStructure` — pública. Administra las estructuras lineales. | `access_password: str`<br>`stack: list[Affiliate]`<br>`queue: deque[Affiliate]`<br>`affiliate_list: list[Affiliate]` | Pila: `list`<br>Cola: `deque`<br>Lista: `list` | `validate_password()`<br>`register()`<br>`remove()`<br>`records()`<br>`find_by_identification()`<br>`build_report()`<br>`report_text()`<br>`count()`<br>`summary()` |
| `Affiliate` — pública. Representa los datos de un afiliado. | `identification_type: str`<br>`identification_number: str`<br>`full_name: str`<br>`current_income: int`<br>`desired_service: str`<br>`employment_mode: str`<br>`affiliation_fee: int`<br>`affiliation_date: date` | El registro se almacena en la pila, cola o lista seleccionada. | `__post_init__()`<br>`formatted_date()`<br>`formatted_income()`<br>`formatted_fee()`<br>`service_label()`<br>`employment_label()`<br>`to_row()` |

*Nota.* Elaboración propia a partir de los requisitos de la práctica.
