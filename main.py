"""Interfaz para el registro de afiliados de Caja Compensándote."""

from __future__ import annotations

from datetime import date, datetime
import os
import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, simpledialog, ttk

from affiliate_data_structure import (
    ACCESS_PASSWORD,
    DATE_PATTERN,
    EMPLOYEE,
    EMPLOYMENT_LABELS,
    EMPLOYMENT_MODES,
    IDENTIFICATION_TYPES,
    LIST,
    QUEUE,
    SERVICE_LABELS,
    SERVICES,
    STACK,
    STRUCTURE_LABELS,
    STRUCTURES,
    Affiliate,
    AffiliateDataStructure,
    DataStructureError,
    DuplicateAffiliateError,
    ValidationError,
    calculate_affiliation_fee,
    format_currency,
    parse_income,
    validate_full_name,
    validate_identification_number,
)
# Datos y colores de la aplicación
AUTHOR = "Jhon Deivid Rojas Rodriguez"
GROUP_NUMBER = "301305_298"
COURSE = "Estructura de Datos (301305-16-04)"
PROGRAM = "Ingeniería de Sistemas"
UNIVERSITY = "Universidad Nacional Abierta y a Distancia - UNAD"
PHASE = "Fase 3 - Componente práctico - Prácticas Simuladas"

LOGIN_TITLE = "Login - Compensándote"
MAIN_TITLE = "Caja Compensándote – Control de Afiliados"

NAVY = "#0B2239"
NAVY_SOFT = "#123E5A"
TEAL = "#0F7C7B"
TEAL_DARK = "#0A5E5D"
GOLD = "#E8A33D"
BG = "#F2F6F9"
CARD = "#FFFFFF"
TEXT = "#1F2D3D"
MUTED = "#6B7C8F"
BORDER = "#D8E2EA"
SOFT = "#F7FAFC"
DANGER = "#B23A48"
DANGER_DARK = "#8E2C38"
SUCCESS = "#1E7A4F"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo_compensandote.png")

FONT = "Segoe UI"

try:  # tkcalendar is optional; the application falls back to three Spinboxes.
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except Exception:  # pragma: no cover - depends on the machine
    DateEntry = None
    HAS_TKCALENDAR = False

STRUCTURE_LABEL_TO_VALUE = {label: value for value, label in STRUCTURE_LABELS.items()}
SERVICE_LABEL_TO_VALUE = {label: value for value, label in SERVICE_LABELS.items()}


def pick_font(root: tk.Misc) -> str:
    """Choose a clean sans-serif family available on the current system."""
    available = set(tkfont.families(root))
    for candidate in ("Segoe UI", "Inter", "Carlito", "DejaVu Sans", "Liberation Sans"):
        if candidate in available:
            return candidate
    return "TkDefaultFont"


def center_window(window: tk.Misc, width: int, height: int) -> None:
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = max(0, (screen_width - width) // 2)
    y = max(0, (screen_height - height) // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


def create_badge(parent: tk.Misc, size: int = 44, background: str = NAVY, oval: str = GOLD,
                 letter: str = "C", letter_color: str = NAVY) -> tk.Canvas:
    """Draw the small circular brand mark used in the headers."""
    canvas = tk.Canvas(parent, width=size, height=size, bg=background,
                       highlightthickness=0, bd=0)
    canvas.create_oval(2, 2, size - 2, size - 2, fill=oval, outline="")
    canvas.create_text(size / 2, size / 2 + 1, text=letter,
                       fill=letter_color, font=(FONT, int(size * 0.42), "bold"))
    return canvas
# Campo de fecha


class AffiliationDateField(tk.Frame):
    """Date control showing dd/mm/yyyy.

    The assignment asks for a DateEntry + Spinbox control.  When tkcalendar is
    installed the native DateEntry is used; otherwise the widget falls back to
    three Spinboxes so the project still runs without external packages.
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, bg=CARD)
        self._calendar = HAS_TKCALENDAR
        if self._calendar:
            self._widget = DateEntry(
                self,
                date_pattern=DATE_PATTERN,
                width=11,
                justify="center",
                font=(FONT, 10),
                background=TEAL,
                foreground="white",
                headersbackground=NAVY,
                headersforeground="white",
                selectbackground=TEAL,
                selectforeground="white",
                normalbackground=CARD,
                weekendbackground=CARD,
                othermonthbackground=SOFT,
                bordercolor=BORDER,
            )
            self._widget.pack(side="left")
            self._widget.set_date(date.today())
        else:
            self.day_var = tk.StringVar(value=f"{date.today().day:02d}")
            self.month_var = tk.StringVar(value=f"{date.today().month:02d}")
            self.year_var = tk.StringVar(value=str(date.today().year))
            common = dict(width=3, justify="center", font=(FONT, 10),
                          bg="white", fg=TEXT, relief="flat",
                          highlightthickness=1, highlightbackground=BORDER,
                          buttonbackground=SOFT)
            self.day_spin = tk.Spinbox(self, from_=1, to=31, width=3,
                                       textvariable=self.day_var, **{k: v for k, v in common.items() if k != "width"})
            self.day_spin.pack(side="left", ipady=5)
            tk.Label(self, text="/", bg=CARD, fg=MUTED, font=(FONT, 10)).pack(side="left", padx=3)
            self.month_spin = tk.Spinbox(self, from_=1, to=12, width=3,
                                         textvariable=self.month_var, **{k: v for k, v in common.items() if k != "width"})
            self.month_spin.pack(side="left", ipady=5)
            tk.Label(self, text="/", bg=CARD, fg=MUTED, font=(FONT, 10)).pack(side="left", padx=3)
            self.year_spin = tk.Spinbox(self, from_=1900, to=2100, width=5,
                                        textvariable=self.year_var, **{k: v for k, v in common.items() if k != "width"})
            self.year_spin.pack(side="left", ipady=5)

    def get_date(self) -> date:
        if self._calendar:
            try:
                value = self._widget.get_date()
            except Exception as exc:  # invalid manual input
                raise ValidationError("La fecha debe tener el formato dd/mm/aaaa.") from exc
            if not isinstance(value, date):
                raise ValidationError("La fecha debe tener el formato dd/mm/aaaa.")
            return value
        try:
            return date(int(self.year_var.get()), int(self.month_var.get()), int(self.day_var.get()))
        except (TypeError, ValueError) as exc:
            raise ValidationError("La fecha debe tener el formato dd/mm/aaaa.") from exc

    def set_date(self, value: date) -> None:
        if self._calendar:
            self._widget.set_date(value)
        else:
            self.day_var.set(f"{value.day:02d}")
            self.month_var.set(f"{value.month:02d}")
            self.year_var.set(str(value.year))
# Información del estudiante


class AboutDialog(tk.Toplevel):
    """Small dialog with the course, author and group information."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.title("Acerca de")
        self.configure(bg=CARD)
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda _event: self.destroy())

        header = tk.Frame(self, bg=NAVY, height=118)
        header.pack(fill="x")
        header.pack_propagate(False)
        badge = create_badge(header, 58, NAVY, GOLD, "C", NAVY)
        badge.pack(side="left", padx=(28, 14), pady=30)
        titles = tk.Frame(header, bg=NAVY)
        titles.pack(side="left", pady=28)
        tk.Label(titles, text="Acerca de la aplicación", bg=NAVY, fg="white",
                 font=(FONT, 16, "bold")).pack(anchor="w")
        tk.Label(titles, text="Caja Compensándote · Control de Afiliados", bg=NAVY,
                 fg="#BFD3E2", font=(FONT, 9)).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(self, bg=CARD)
        body.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(body, text="Información del estudiante y del curso", bg=CARD,
                 fg=TEAL, font=(FONT, 11, "bold")).pack(anchor="w")
        line = tk.Frame(body, bg=BORDER, height=1)
        line.pack(fill="x", pady=(8, 14))

        information = (
            ("Curso", COURSE),
            ("Estudiante", AUTHOR),
            ("Grupo colaborativo", GROUP_NUMBER),
            ("Programa", PROGRAM),
            ("Universidad", UNIVERSITY),
            ("Fase", PHASE),
        )
        grid = tk.Frame(body, bg=CARD)
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, minsize=128)
        grid.grid_columnconfigure(1, weight=1)
        for row, (label, value) in enumerate(information):
            tk.Label(grid, text=label, bg=CARD, fg=MUTED, font=(FONT, 9, "bold"),
                     anchor="w").grid(row=row, column=0, sticky="nw", pady=5)
            tk.Label(grid, text=value, bg=CARD, fg=TEXT, font=(FONT, 9),
                     anchor="w", justify="left", wraplength=285).grid(
                row=row, column=1, sticky="nw", pady=5)

        close = ttk.Button(body, text="Cerrar", style="Primary.TButton",
                           command=self.destroy)
        close.pack(side="bottom", anchor="e", pady=(16, 0))

        center_window(self, 500, 500)
        self.grab_set()
        self.after(80, self.focus_force)
# Ventana de acceso


class LoginView(tk.Frame):
    """Access screen with masked password and the Acerca de / Salir buttons."""

    def __init__(self, master: tk.Misc, app: "CompensandoteApp") -> None:
        super().__init__(master, bg=BG)
        self.app = app
        self.error_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        left = tk.Frame(self, bg=NAVY, width=510)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # Decorative concentric circles on the dark panel.
        decoration = tk.Canvas(left, width=220, height=220, bg=NAVY,
                               highlightthickness=0, bd=0)
        decoration.place(relx=1.0, rely=1.0, x=78, y=70, anchor="se")
        for radius, color in ((190, "#163F5B"), (145, "#1B4B69"), (100, "#225776")):
            decoration.create_oval(110 - radius, 110 - radius, 110 + radius,
                                   110 + radius, outline=color, width=2)

        content = tk.Frame(left, bg=NAVY)
        content.pack(fill="both", expand=True, padx=48, pady=44)

        brand = tk.Frame(content, bg=NAVY)
        brand.pack(anchor="w")
        create_badge(brand, 42, NAVY, GOLD, "C", NAVY).pack(side="left")
        brand_text = tk.Frame(brand, bg=NAVY)
        brand_text.pack(side="left", padx=(12, 0))
        tk.Label(brand_text, text="COMPENSÁNDOTE", bg=NAVY, fg="white",
                 font=(FONT, 13, "bold")).pack(anchor="w")
        tk.Label(brand_text, text="CAJA DE COMPENSACIÓN FAMILIAR", bg=NAVY,
                 fg="#93AFC4", font=(FONT, 7, "bold")).pack(anchor="w")

        tk.Frame(content, bg=NAVY, height=44).pack()
        tk.Label(content, text="Bienestar que se\nsiente. Afiliación\nque se vive.",
                 bg=NAVY, fg="white", justify="left",
                 font=(FONT, 27, "bold"), wraplength=390).pack(anchor="w")
        accent = tk.Frame(content, bg=GOLD, height=4, width=64)
        accent.pack(anchor="w", pady=(16, 14))
        tk.Label(content, text="Acceda al sistema de registro de afiliados y\n"
                               "gestione la información de los usuarios del centro\n"
                               "de servicios.",
                 bg=NAVY, fg="#C4D6E3", justify="left",
                 font=(FONT, 10), wraplength=370).pack(anchor="w")

        tk.Frame(content, bg=NAVY, height=22).pack()
        benefits = (
            "Subsidio de desempleo",
            "Ingreso a parques",
            "Cursos de formación",
            "Paquetes de viaje",
            "Medicina preventiva",
        )
        for benefit in benefits:
            row = tk.Frame(content, bg=NAVY)
            row.pack(anchor="w", pady=3)
            tk.Label(row, text="✓", bg=NAVY, fg=GOLD,
                     font=(FONT, 10, "bold")).pack(side="left")
            tk.Label(row, text=benefit, bg=NAVY, fg="#DCE8F1",
                     font=(FONT, 9)).pack(side="left", padx=(8, 0))

        tk.Frame(content, bg=NAVY).pack(fill="both", expand=True)
        tk.Label(content, text="Universidad Nacional Abierta y a Distancia - UNAD\n"
                               "Estructura de Datos (301305) · Fase 3",
                 bg=NAVY, fg="#7F9CB2", justify="left",
                 font=(FONT, 8)).pack(anchor="w")

        right = tk.Frame(self, bg=CARD)
        right.pack(side="right", fill="both", expand=True)
        panel = tk.Frame(right, bg=CARD)
        panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.76)

        tk.Label(panel, text="CAJA DE COMPENSACIÓN FAMILIAR", bg=CARD, fg=TEAL,
                 font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(panel, text="Iniciar sesión", bg=CARD, fg=NAVY,
                 font=(FONT, 25, "bold")).pack(anchor="w", pady=(6, 4))
        tk.Label(panel, text="Ingrese la contraseña para acceder al control de afiliados.",
                 bg=CARD, fg=MUTED, font=(FONT, 10), wraplength=380,
                 justify="left").pack(anchor="w")

        tk.Frame(panel, bg=CARD, height=28).pack()
        tk.Label(panel, text="Contraseña", bg=CARD, fg=TEXT,
                 font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 5))
        self.password_entry = tk.Entry(
            panel, show="*", font=(FONT, 15), bg=SOFT, fg=TEXT,
            insertbackground=TEXT, relief="flat", highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=TEAL,
        )
        self.password_entry.pack(fill="x", ipady=9)
        self.password_entry.bind("<Return>", lambda _event: self.attempt_login())

        tk.Label(panel, textvariable=self.error_var, bg=CARD, fg=DANGER,
                 font=(FONT, 9), wraplength=380, justify="left").pack(
            anchor="w", pady=(6, 0))

        tk.Frame(panel, bg=CARD, height=8).pack()
        login_button = ttk.Button(panel, text="Ingresar", style="Primary.TButton",
                                  command=self.attempt_login)
        login_button.pack(fill="x", pady=(6, 0))

        tk.Frame(panel, bg=CARD, height=20).pack()
        self._separator(panel)
        tk.Frame(panel, bg=CARD, height=18).pack()

        secondary = tk.Frame(panel, bg=CARD)
        secondary.pack(fill="x")
        secondary.grid_columnconfigure(0, weight=1, uniform="secondary")
        secondary.grid_columnconfigure(1, weight=1, uniform="secondary")
        ttk.Button(secondary, text="Acerca de", style="Secondary.TButton",
                   command=self.app.show_about).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(secondary, text="Salir", style="Ghost.TButton",
                   command=self.app.exit_app).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        tk.Frame(panel, bg=CARD, height=28).pack()
        footer = tk.Frame(panel, bg=CARD)
        footer.pack(fill="x")
        tk.Label(footer, text="Fase 3 · Componente práctico", bg=CARD, fg=MUTED,
                 font=(FONT, 8)).pack(anchor="w")
        tk.Label(footer, text=AUTHOR, bg=CARD, fg=TEXT,
                 font=(FONT, 8, "bold")).pack(anchor="w", pady=(2, 0))

        self.password_entry.focus_set()

    @staticmethod
    def _separator(parent: tk.Misc) -> None:
        line = tk.Frame(parent, bg=BORDER, height=1)
        line.pack(fill="x")

    def attempt_login(self) -> None:
        password = self.password_entry.get()
        if self.app.data.validate_password(password):
            self.error_var.set("")
            self.app.show_main()
            return
        self.error_var.set("Contraseña incorrecta. Verifique e intente nuevamente.")
        self.password_entry.selection_range(0, "end")
        self.password_entry.focus_set()
        self.bell()
# Ventana de registro


class MainView(tk.Frame):
    """Registration form, Treeview and the three linear data structures."""

    COLUMNS = ("id_type", "id_number", "name", "income", "service",
               "mode", "fee", "date")
    HEADINGS = {
        "id_type": "Tipo ID",
        "id_number": "Identificación",
        "name": "Nombre completo",
        "income": "Ingresos",
        "service": "Servicio deseado",
        "mode": "Modalidad",
        "fee": "Tarifa",
        "date": "Fecha",
    }
    WIDTHS = {
        "id_type": 50,
        "id_number": 92,
        "name": 150,
        "income": 88,
        "service": 128,
        "mode": 82,
        "fee": 80,
        "date": 76,
    }

    def __init__(self, master: tk.Misc, app: "CompensandoteApp") -> None:
        super().__init__(master, bg=BG)
        self.app = app
        self.data = app.data
        self.root = app.root

        self.id_type_var = tk.StringVar(value=IDENTIFICATION_TYPES[0])
        self.id_number_var = tk.StringVar()
        self.full_name_var = tk.StringVar()
        self.income_var = tk.StringVar()
        self.service_var = tk.StringVar()
        self.mode_var = tk.StringVar(value=EMPLOYEE)
        self.fee_var = tk.StringVar()
        self.structure_var = tk.StringVar(value=STRUCTURE_LABELS[STACK])
        self.count_var = tk.StringVar(value="0 registros")
        self.status_var = tk.StringVar(value="Listo. Seleccione una estructura y registre el primer afiliado.")
        self.hint_var = tk.StringVar()

        self._build()
        self._attach_traces()
        self.refresh_view(initial=True)

    def _build(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()

        body = tk.Frame(self, bg=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=14)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=0, minsize=430)
        body.grid_columnconfigure(1, weight=1)

        self._build_form_card(body)
        self._build_records_card(body)
        self._build_footer()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=NAVY, height=78)
        header.grid(row=0, column=0, sticky="ew")
        header.pack_propagate(False)

        left = tk.Frame(header, bg=NAVY)
        left.pack(side="left", padx=20, pady=13)
        create_badge(left, 44, NAVY, GOLD, "C", NAVY).pack(side="left")
        titles = tk.Frame(left, bg=NAVY)
        titles.pack(side="left", padx=(12, 0))
        tk.Label(titles, text="Control de Afiliados", bg=NAVY, fg="white",
                 font=(FONT, 16, "bold")).pack(anchor="w")
        tk.Label(titles, text="Caja Compensándote · Afiliación y beneficios",
                 bg=NAVY, fg="#AFC8DA", font=(FONT, 8)).pack(anchor="w")

        right = tk.Frame(header, bg=NAVY)
        right.pack(side="right", padx=20, pady=14)
        tk.Label(right, text=f"Grupo {GROUP_NUMBER}", bg=NAVY, fg="white",
                 font=(FONT, 9, "bold")).pack(anchor="e")
        tk.Label(right, text=f"{PHASE} · {datetime.now():%d/%m/%Y}", bg=NAVY,
                 fg="#AFC8DA", font=(FONT, 8)).pack(anchor="e", pady=(3, 0))

    def _card(self, parent: tk.Misc) -> tk.Frame:
        return tk.Frame(parent, bg=CARD, highlightbackground=BORDER,
                        highlightthickness=1)

    def _build_form_card(self, body: tk.Misc) -> None:
        card = self._card(body)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="both", expand=True, padx=18, pady=15)

        ttk.Label(inner, text="Datos del afiliado", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(inner, text="Complete la información para calcular la tarifa de afiliación.",
                  style="CardSub.TLabel").pack(anchor="w", pady=(2, 8))
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=(0, 4))

        form = tk.Frame(inner, bg=CARD)
        form.pack(fill="both", expand=True)
        form.grid_columnconfigure(0, weight=1, uniform="form")
        form.grid_columnconfigure(1, weight=1, uniform="form")

        # Identification type and number.
        self._field_label(form, "Tipo de identificación", 0, 0)
        self._field_label(form, "Número de identificación", 0, 1)
        self.id_type_combo = ttk.Combobox(
            form, textvariable=self.id_type_var, values=IDENTIFICATION_TYPES,
            state="readonly", width=8, style="Card.TCombobox",
        )
        self.id_type_combo.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(0, 6))
        digits_command = (self.register(self._validate_digits), "%P")
        self.id_number_entry = ttk.Entry(
            form, textvariable=self.id_number_var, style="Card.TEntry",
            validate="key", validatecommand=digits_command,
        )
        self.id_number_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(0, 6))

        # Full name.
        self._field_label(form, "Nombre completo", 2, 0, columnspan=2)
        self.name_entry = ttk.Entry(
            form, textvariable=self.full_name_var, style="Card.TEntry",
            validate="key",
            validatecommand=(self.register(self._validate_name), "%P"),
        )
        self.name_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        # Income and requested service.
        self._field_label(form, "Ingresos actuales (COP)", 4, 0)
        self._field_label(form, "Servicio deseado", 4, 1)
        self.income_entry = ttk.Entry(
            form, textvariable=self.income_var, style="Card.TEntry",
            validate="key", validatecommand=digits_command,
        )
        self.income_entry.grid(row=5, column=0, sticky="ew", padx=(0, 5), pady=(0, 6))
        self.service_combo = ttk.Combobox(
            form, textvariable=self.service_var,
            values=[SERVICE_LABELS[service] for service in SERVICES],
            state="readonly", width=18, style="Card.TCombobox",
        )
        self.service_combo.grid(row=5, column=1, sticky="ew", padx=(5, 0), pady=(0, 6))

        # Employment mode.
        self._field_label(form, "Modalidad de empleo", 6, 0, columnspan=2)
        modes = tk.Frame(form, bg=CARD)
        modes.grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 6))
        for mode in EMPLOYMENT_MODES:
            ttk.Radiobutton(
                modes, text=EMPLOYMENT_LABELS[mode], value=mode,
                variable=self.mode_var, style="Card.TRadiobutton",
            ).pack(side="left", padx=(0, 22))

        # Fee and date.
        self._field_label(form, "Tarifa de afiliación", 8, 0)
        self._field_label(form, "Fecha de afiliación", 8, 1)
        self.fee_entry = tk.Entry(
            form, textvariable=self.fee_var, state="readonly", readonlybackground="#E9F6F4",
            fg=TEAL, font=(FONT, 11, "bold"), relief="flat", highlightthickness=1,
            highlightbackground=BORDER, justify="left",
        )
        self.fee_entry.grid(row=9, column=0, sticky="ew", padx=(0, 5), pady=(0, 6), ipady=5)
        self.date_field = AffiliationDateField(form)
        self.date_field.grid(row=9, column=1, sticky="w", padx=(5, 0), pady=(0, 6))

        # Read-only report.
        self._field_label(form, "Reporte", 10, 0, columnspan=2)
        self.report_widget = tk.Text(
            form, height=3, width=1, wrap="word", bg=SOFT, fg=TEXT, relief="flat",
            highlightthickness=1, highlightbackground=BORDER, font=(FONT, 9),
            padx=8, pady=6, state="disabled", cursor="arrow",
        )
        self.report_widget.grid(row=11, column=0, columnspan=2, sticky="nsew")
        tk.Label(
            form,
            text="La tarifa se calcula automáticamente con los ingresos, la modalidad "
                 "y el servicio. Medicina preventiva adiciona el 10 % de los ingresos.",
            bg=CARD, fg=MUTED, font=(FONT, 8), justify="left", wraplength=380,
        ).grid(row=12, column=0, columnspan=2, sticky="w", pady=(9, 0))

    def _build_records_card(self, body: tk.Misc) -> None:
        card = self._card(body)
        card.grid(row=0, column=1, sticky="nsew")
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="both", expand=True, padx=16, pady=15)

        title_row = tk.Frame(inner, bg=CARD)
        title_row.pack(fill="x")
        ttk.Label(title_row, text="Registros por estructura",
                  style="CardTitle.TLabel").pack(side="left")
        tk.Label(title_row, textvariable=self.count_var, bg="#E9F6F4", fg=TEAL,
                 font=(FONT, 8, "bold"), padx=8, pady=2).pack(side="right")

        controls = tk.Frame(inner, bg=CARD)
        controls.pack(fill="x", pady=(8, 7))
        ttk.Label(controls, text="Ver estructura:", style="Field.TLabel").pack(side="left")
        self.structure_combo = ttk.Combobox(
            controls, textvariable=self.structure_var,
            values=[STRUCTURE_LABELS[value] for value in STRUCTURES],
            state="readonly", width=10, style="Card.TCombobox",
        )
        self.structure_combo.pack(side="left", padx=(8, 0))
        self.structure_combo.bind("<<ComboboxSelected>>", self._on_structure_change)
        ttk.Label(controls, text="La estructura seleccionada recibe el registro y los reportes.",
                  style="Hint.TLabel").pack(side="left", padx=(12, 0))

        tree_frame = tk.Frame(inner, bg=CARD, highlightbackground=BORDER,
                              highlightthickness=1)
        tree_frame.pack(fill="both", expand=True)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=self.COLUMNS,
                                 show="headings", selectmode="browse")
        for column in self.COLUMNS:
            self.tree.heading(column, text=self.HEADINGS[column])
            anchor = "center" if column in ("id_type", "income", "mode", "fee", "date") else "w"
            self.tree.column(column, width=self.WIDTHS[column],
                             minwidth=self.WIDTHS[column], anchor=anchor,
                             stretch=(column == "name"))
        self.tree.tag_configure("odd", background="#F8FAFC")
        self.tree.tag_configure("even", background=CARD)
        self.tree.grid(row=0, column=0, sticky="nsew")

        vertical = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        self.horizontal_scrollbar = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview)
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set,
                            xscrollcommand=self.horizontal_scrollbar.set)
        self.tree.bind("<Configure>", self._update_horizontal_scrollbar)

        self.empty_label = tk.Label(
            tree_frame, text="Aún no hay registros en esta estructura.\n"
                             "Diligencie el formulario y presione Registrar.",
            bg=CARD, fg=MUTED, font=(FONT, 9), justify="center",
        )
        self.empty_label.place(relx=0.5, rely=0.55, anchor="center")
        self.empty_label.lift()

        self.hint_label = ttk.Label(inner, textvariable=self.hint_var,
                                    style="Hint.TLabel")
        self.hint_label.pack(fill="x", pady=(7, 0))

    def _update_horizontal_scrollbar(self, _event: tk.Event | None = None) -> None:
        """Hide the horizontal bar when every column fits in the Treeview."""
        needed = sum(self.WIDTHS.values()) + 4
        if self.tree.winfo_width() >= needed:
            self.horizontal_scrollbar.grid_remove()
        else:
            self.horizontal_scrollbar.grid()

    def _build_footer(self) -> None:
        footer = tk.Frame(self, bg=CARD, height=70,
                          highlightbackground=BORDER, highlightthickness=1)
        footer.grid(row=2, column=0, sticky="ew")
        footer.pack_propagate(False)

        status_box = tk.Frame(footer, bg=CARD)
        status_box.pack(side="left", padx=20)
        self.status_dot = tk.Label(status_box, text="●", bg=CARD, fg=TEAL,
                                   font=(FONT, 10))
        self.status_dot.pack(side="left")
        self.status_label = tk.Label(status_box, textvariable=self.status_var,
                                     bg=CARD, fg=TEXT, font=(FONT, 9),
                                     anchor="w", justify="left", wraplength=520)
        self.status_label.pack(side="left", padx=(7, 0))

        buttons = tk.Frame(footer, bg=CARD)
        buttons.pack(side="right", padx=16)
        self.register_button = ttk.Button(buttons, text="Registrar",
                                          style="Primary.TButton",
                                          command=self.register_affiliate)
        self.register_button.pack(side="left", padx=4)
        ttk.Button(buttons, text="Limpiar", style="Secondary.TButton",
                   command=self.clear_form).pack(side="left", padx=4)
        ttk.Button(buttons, text="Reporte", style="Info.TButton",
                   command=self.show_report).pack(side="left", padx=4)
        ttk.Button(buttons, text="Eliminar", style="Danger.TButton",
                   command=self.delete_affiliate).pack(side="left", padx=4)
        ttk.Button(buttons, text="Salir", style="Ghost.TButton",
                   command=self.app.exit_app).pack(side="left", padx=4)

    @staticmethod
    def _validate_digits(value: str) -> bool:
        return value == "" or value.isdigit()

    @staticmethod
    def _validate_name(value: str) -> bool:
        if value == "":
            return True
        return all(character.isalpha() or character == " " for character in value)

    def _field_label(self, parent: tk.Misc, text: str, row: int, column: int,
                     columnspan: int = 1) -> None:
        ttk.Label(parent, text=text, style="Field.TLabel").grid(
            row=row, column=column, columnspan=columnspan, sticky="w",
            pady=(5, 2))

    def _attach_traces(self) -> None:
        self.income_var.trace_add("write", lambda *_: self.update_fee())
        self.service_var.trace_add("write", lambda *_: self.update_fee())
        self.mode_var.trace_add("write", lambda *_: self.update_fee())

    def _on_structure_change(self, _event: tk.Event | None = None) -> None:
        structure = self.selected_structure()
        self.refresh_view()
        self.set_status(
            f"Mostrando la {STRUCTURE_LABELS[structure]}. "
            f"Los nuevos registros y los reportes usarán esta estructura.",
            "info",
        )

    def selected_service(self) -> str | None:
        return SERVICE_LABEL_TO_VALUE.get(self.service_var.get())

    def selected_structure(self) -> str:
        return STRUCTURE_LABEL_TO_VALUE.get(self.structure_var.get(), STACK)

    def update_fee(self) -> None:
        if not hasattr(self, "fee_var"):
            return
        try:
            service = self.selected_service()
            if service is None:
                raise ValidationError("Seleccione un servicio.")
            income = parse_income(self.income_var.get())
            fee = calculate_affiliation_fee(income, service, self.mode_var.get())
        except (ValidationError, DataStructureError):
            self.fee_var.set("")
        else:
            self.fee_var.set(format_currency(fee))

    def refresh_view(self, initial: bool = False) -> None:
        structure = self.selected_structure()
        records = self.data.records(structure)

        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, affiliate in enumerate(records):
            self.tree.insert("", "end", values=affiliate.to_row(),
                             tags=("even" if index % 2 == 0 else "odd",))

        self.count_var.set(f"{len(records)} registro(s)")
        if records:
            self.empty_label.place_forget()
            target = self.tree.get_children()[0] if structure == STACK else self.tree.get_children()[-1]
            self.tree.selection_set(target)
            self.tree.see(target)
        else:
            self.empty_label.place(relx=0.5, rely=0.55, anchor="center")
            self.empty_label.lift()

        if structure == STACK:
            self.hint_var.set("Vista LIFO: el último afiliado registrado aparece primero. "
                              "Eliminar desapila el registro superior.")
        elif structure == QUEUE:
            self.hint_var.set("Vista FIFO: el primer afiliado registrado aparece primero. "
                              "Eliminar desencola el registro del frente.")
        else:
            self.hint_var.set("Vista secuencial: los afiliados conservan el orden de llegada. "
                              "Eliminar solicita la identificación del afiliado.")
        self.update_report()
        if initial:
            self.set_status("Listo. Seleccione una estructura y registre el primer afiliado.", "info")

    def update_report(self) -> None:
        text = self.data.report_text(self.selected_structure())
        self.report_widget.configure(state="normal")
        self.report_widget.delete("1.0", "end")
        self.report_widget.insert("1.0", text)
        self.report_widget.configure(state="disabled")

    def register_affiliate(self) -> None:
        structure = self.selected_structure()
        try:
            identification_type = self.id_type_var.get().strip().upper()
            identification_number = validate_identification_number(self.id_number_var.get())
            full_name = validate_full_name(self.full_name_var.get())
            income = parse_income(self.income_var.get())
            service = self.selected_service()
            if service is None:
                raise ValidationError("Debe seleccionar un servicio deseado.")
            mode = self.mode_var.get()
            fee = calculate_affiliation_fee(income, service, mode)
            affiliate_date = self.date_field.get_date()
            affiliate = Affiliate(
                identification_type=identification_type,
                identification_number=identification_number,
                full_name=full_name,
                current_income=income,
                desired_service=service,
                employment_mode=mode,
                affiliation_fee=fee,
                affiliation_date=affiliate_date,
            )
            self.data.register(structure, affiliate)
        except DuplicateAffiliateError as exc:
            self.show_error(str(exc))
            return
        except (ValidationError, DataStructureError) as exc:
            self.show_error(str(exc))
            return

        self.refresh_view()
        self.clear_inputs()
        self.id_number_entry.focus_set()
        label = STRUCTURE_LABELS[structure]
        self.set_status(
            f"Afiliado {affiliate.full_name} registrado en la {label} "
            f"con una tarifa de {format_currency(affiliate.affiliation_fee)}.",
            "success",
        )

    def clear_inputs(self) -> None:
        self.id_type_var.set(IDENTIFICATION_TYPES[0])
        self.id_number_var.set("")
        self.full_name_var.set("")
        self.income_var.set("")
        self.service_var.set("")
        self.mode_var.set(EMPLOYEE)
        self.fee_var.set("")
        self.date_field.set_date(date.today())

    def clear_form(self) -> None:
        self.clear_inputs()
        self.id_number_entry.focus_set()
        self.set_status("Formulario limpio. Los registros de la estructura se conservan.", "info")

    def show_report(self) -> None:
        structure = self.selected_structure()
        self.update_report()
        report = self.data.build_report(structure)
        label = STRUCTURE_LABELS[structure]
        if structure == STACK:
            detail = f"suma de tarifas {report.formatted_total_fees}"
        elif structure == QUEUE:
            detail = f"{report.count} registro(s) en espera"
        else:
            detail = f"promedio de ingresos {report.formatted_average_income}"
        self.set_status(f"Reporte de la {label}: {detail}.", "info")

    def delete_affiliate(self) -> None:
        structure = self.selected_structure()
        label = STRUCTURE_LABELS[structure]
        records = self.data.records(structure)
        if not records:
            messagebox.showinfo("Eliminar registro",
                                f"La {label.lower()} está vacía; no hay registros para eliminar.",
                                parent=self.root)
            return

        number: str | None = None
        if structure == LIST:
            initial = self.id_number_var.get().strip()
            answer = simpledialog.askstring(
                "Eliminar de la lista",
                "Digite el número de identificación del afiliado que desea eliminar:",
                initialvalue=initial, parent=self.root,
            )
            if answer is None:
                self.set_status("Eliminación cancelada.", "info")
                return
            try:
                number = validate_identification_number(answer)
            except ValidationError as exc:
                self.show_error(str(exc))
                return
            target = self.data.find_by_identification(LIST, number)
            if target is None:
                self.show_error(
                    f"No existe un afiliado con la identificación {number} en la lista."
                )
                return
        else:
            target = records[0]

        action = {"Stack": "desapilar (tope de la pila)",
                  "Queue": "desencolar (frente de la cola)",
                  "List": "eliminar de la lista"}[structure]
        confirmed = messagebox.askyesno(
            "Confirmar eliminación",
            f"Se va a {action} el siguiente registro:\n\n"
            f"• {target.full_name}\n"
            f"• Identificación: {target.identification_number}\n"
            f"• Tarifa: {target.formatted_fee}\n\n"
            "¿Desea continuar?",
            parent=self.root, icon="warning",
        )
        if not confirmed:
            self.set_status("Eliminación cancelada por el usuario.", "info")
            return

        try:
            removed = self.data.remove(structure, number)
        except (EmptyStructureError, AffiliateNotFoundError, ValidationError) as exc:
            self.show_error(str(exc))
            return
        self.refresh_view()
        self.set_status(
            f"Registro de {removed.full_name} eliminado de la {label.lower()}.", "success"
        )

    def set_status(self, message: str, kind: str = "info") -> None:
        colors = {"info": TEAL, "success": SUCCESS, "error": DANGER}
        self.status_var.set(message)
        self.status_label.configure(fg=TEXT if kind != "error" else DANGER)
        self.status_dot.configure(fg=colors.get(kind, TEAL))

    def show_error(self, message: str) -> None:
        self.set_status(message, "error")
        messagebox.showerror("Validación de datos", message, parent=self.root)
# Ventana principal


class CompensandoteApp:
    """Own the Tk root, the domain model and the two screens."""

    def __init__(self) -> None:
        global FONT
        self.root = tk.Tk()
        FONT = pick_font(self.root)
        self.root.title(LOGIN_TITLE)
        self.root.configure(bg=BG)
        self.root.minsize(980, 620)
        center_window(self.root, 1080, 660)

        self.data = AffiliateDataStructure()
        self.login_frame: LoginView | None = None
        self.main_view: MainView | None = None
        self.about_dialog: AboutDialog | None = None
        self._icon: tk.PhotoImage | None = None

        self._load_icon()
        self._configure_styles()
        self._build_menu()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.show_login()

    def _load_icon(self) -> None:
        if not os.path.exists(LOGO_PATH):
            return
        try:
            self._icon = tk.PhotoImage(file=LOGO_PATH)
            self.root.iconphoto(True, self._icon)
        except tk.TclError:
            self._icon = None

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(".", font=(FONT, 10))
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=(FONT, 10))
        style.configure("Card.TLabel", background=CARD, foreground=TEXT, font=(FONT, 10))
        style.configure("CardTitle.TLabel", background=CARD, foreground=NAVY,
                        font=(FONT, 15, "bold"))
        style.configure("CardSub.TLabel", background=CARD, foreground=MUTED,
                        font=(FONT, 9))
        style.configure("Field.TLabel", background=CARD, foreground=MUTED,
                        font=(FONT, 8, "bold"))
        style.configure("Hint.TLabel", background=CARD, foreground=MUTED,
                        font=(FONT, 8))
        style.configure("Card.TRadiobutton", background=CARD, foreground=TEXT,
                        font=(FONT, 10))
        style.map("Card.TRadiobutton", background=[("active", CARD)])

        style.configure("Card.TEntry", fieldbackground="white", foreground=TEXT,
                        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                        padding=6)
        style.map("Card.TEntry",
                  bordercolor=[("focus", TEAL)],
                  lightcolor=[("focus", TEAL)],
                  darkcolor=[("focus", TEAL)])
        style.configure("Card.TCombobox", fieldbackground="white", background="white",
                        foreground=TEXT, bordercolor=BORDER, arrowcolor=NAVY,
                        padding=4)
        style.map("Card.TCombobox",
                  fieldbackground=[("readonly", "white")],
                  foreground=[("readonly", TEXT)],
                  bordercolor=[("focus", TEAL)])

        button_common = dict(font=(FONT, 10, "bold"), padding=(16, 9), borderwidth=0)
        style.configure("Primary.TButton", background=TEAL, foreground="white",
                        **button_common)
        style.map("Primary.TButton",
                  background=[("active", TEAL_DARK), ("pressed", TEAL_DARK)],
                  foreground=[("disabled", "#DDE7EA")])
        style.configure("Secondary.TButton", background="#E8EEF3", foreground=NAVY,
                        **button_common)
        style.map("Secondary.TButton", background=[("active", "#D7E1E8")])
        style.configure("Info.TButton", background=NAVY, foreground="white",
                        **button_common)
        style.map("Info.TButton", background=[("active", NAVY_SOFT)])
        style.configure("Danger.TButton", background=DANGER, foreground="white",
                        **button_common)
        style.map("Danger.TButton", background=[("active", DANGER_DARK)])
        ghost_common = {**button_common, "borderwidth": 1}
        style.configure("Ghost.TButton", background="#F7FAFC", foreground=NAVY,
                        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                        **ghost_common)
        style.map("Ghost.TButton",
                  background=[("active", "#E8EEF3")],
                  bordercolor=[("active", "#B9C9D4")],
                  foreground=[("active", NAVY)])

        style.configure("Treeview", background=CARD, fieldbackground=CARD,
                        foreground=TEXT, rowheight=28, font=(FONT, 9),
                        borderwidth=0)
        style.configure("Treeview.Heading", background="#E8EEF3", foreground=NAVY,
                        font=(FONT, 8, "bold"), relief="flat", padding=(4, 7))
        style.map("Treeview.Heading", background=[("active", "#DCE7EE")])
        style.map("Treeview", background=[("selected", TEAL)],
                  foreground=[("selected", "white")])
        style.configure("Vertical.TScrollbar", background="#C9D6DF", troughcolor=CARD,
                        bordercolor=CARD, arrowcolor=NAVY)
        style.configure("Horizontal.TScrollbar", background="#C9D6DF", troughcolor=CARD,
                        bordercolor=CARD, arrowcolor=NAVY)

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)
        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="Información del estudiante", command=self.show_about)
        about_menu.add_separator()
        about_menu.add_command(label="Salir", command=self.exit_app)
        menubar.add_cascade(label="Acerca de", menu=about_menu)
        self.root.config(menu=menubar)

    def show_login(self) -> None:
        if self.main_view is not None:
            self.main_view.destroy()
            self.main_view = None
        self.root.title(LOGIN_TITLE)
        self.root.minsize(980, 620)
        center_window(self.root, 1080, 660)
        self.login_frame = LoginView(self.root, self)
        self.login_frame.pack(fill="both", expand=True)

    def show_main(self) -> None:
        if self.login_frame is not None:
            self.login_frame.destroy()
            self.login_frame = None
        self.root.title(MAIN_TITLE)
        self.root.minsize(1100, 720)
        center_window(self.root, 1280, 800)
        self.main_view = MainView(self.root, self)
        self.main_view.pack(fill="both", expand=True)

    def show_about(self) -> None:
        if self.about_dialog is not None and self.about_dialog.winfo_exists():
            self.about_dialog.lift()
            self.about_dialog.focus_force()
            return
        self.about_dialog = AboutDialog(self.root)

    def exit_app(self) -> None:
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    try:
        app = CompensandoteApp()
    except tk.TclError as exc:
        print("No se pudo iniciar la interfaz gráfica:", exc, file=sys.stderr)
        print("Verifique que Tkinter esté instalado y que exista un entorno gráfico.",
              file=sys.stderr)
        raise SystemExit(1) from exc
    app.run()


if __name__ == "__main__":
    main()
