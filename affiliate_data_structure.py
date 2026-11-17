# -*- coding: utf-8 -*-
"""
Caja Compensandote - Affiliate data structures (business logic).

Phase 3 - Practical component - Simulated practices
Course: Data Structures (301305-16-04) - UNAD
Collaborative group: 298
Author: Jhon Deivid Rojas Rodriguez

This module is intentionally independent from Tkinter.  It contains the
domain model (Affiliate), the three linear data structures required by the
assignment (stack, queue and list) and every calculation or validation rule.
Keeping the logic isolated makes it testable and reusable by the GUI.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import date, datetime
import hmac
import re
from typing import Iterable

# ---------------------------------------------------------------------------
# Domain constants (internal values are in English, as requested by the guide)
# ---------------------------------------------------------------------------
ACCESS_PASSWORD = "Caja"

STACK = "Stack"
QUEUE = "Queue"
LIST = "List"
STRUCTURES = (STACK, QUEUE, LIST)

IDENTIFICATION_TYPES = ("CC", "CE", "NUIP", "PAS")

UNEMPLOYMENT_SUBSIDY = "Unemployment subsidy"
PARK_ADMISSION = "Park admission"
TRAINING_COURSE = "Training course"
TRAVEL_PACKAGE = "Travel package"
PREVENTIVE_MEDICINE = "Preventive medicine"
SERVICES = (
    UNEMPLOYMENT_SUBSIDY,
    PARK_ADMISSION,
    TRAINING_COURSE,
    TRAVEL_PACKAGE,
    PREVENTIVE_MEDICINE,
)

EMPLOYEE = "Employee"
INDEPENDENT = "Independent"
EMPLOYMENT_MODES = (EMPLOYEE, INDEPENDENT)

# Spanish labels shown by the graphical interface.
STRUCTURE_LABELS = {STACK: "Pila", QUEUE: "Cola", LIST: "Lista"}
SERVICE_LABELS = {
    UNEMPLOYMENT_SUBSIDY: "Subsidio de desempleo",
    PARK_ADMISSION: "Ingreso a parque",
    TRAINING_COURSE: "Curso de formación",
    TRAVEL_PACKAGE: "Paquete de viaje",
    PREVENTIVE_MEDICINE: "Medicina preventiva",
}
EMPLOYMENT_LABELS = {EMPLOYEE: "Empleado", INDEPENDENT: "Independiente"}

# Base fee brackets: (upper bound of the bracket, fee).  The first bracket
# starts at $ 0 so that the table is always defined; the assignment publishes
# it from $ 1.000.000 and the application honours the published amounts.
EMPLOYEE_BRACKETS = (
    (2_000_000, 45_000),
    (3_000_000, 60_000),
    (4_000_000, 75_000),
    (5_000_000, 90_000),
    (None, 150_000),
)
INDEPENDENT_BRACKETS = (
    (2_000_000, 10_000),
    (3_000_000, 20_000),
    (4_000_000, 30_000),
    (5_000_000, 40_000),
    (None, 80_000),
)

# Fixed surcharge added to the base fee, except for preventive medicine,
# whose surcharge is 10 % of the current income.
SERVICE_SURCHARGES = {
    UNEMPLOYMENT_SUBSIDY: 0,
    PARK_ADMISSION: 2_500,
    TRAINING_COURSE: 7_500,
    TRAVEL_PACKAGE: 10_000,
}

DATE_FORMAT = "%d/%m/%Y"
DATE_PATTERN = "dd/mm/yyyy"
NAME_PATTERN = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$")


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------
class DataStructureError(Exception):
    """Base class for the errors raised by the domain model."""


class ValidationError(DataStructureError):
    """Raised when a value does not satisfy a business rule."""


class DuplicateAffiliateError(DataStructureError):
    """Raised when an identification already exists in a structure."""


class EmptyStructureError(DataStructureError):
    """Raised when a removal is attempted on an empty structure."""


class AffiliateNotFoundError(DataStructureError):
    """Raised when the requested affiliate is not present in the list."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def format_currency(value: int | float) -> str:
    """Return a Colombian peso representation, e.g. 45000 -> '$ 45.000'."""
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        number = 0
    return "$ " + f"{number:,}".replace(",", ".")


def parse_income(value: str | int | float) -> int:
    """Convert user input such as '2.500.000' or '$ 2500000' to an integer.

    Only the digits are kept; this accepts the thousands separators usually
    typed by Colombian users without allowing negative or decimal amounts.
    """
    if isinstance(value, bool):
        raise ValidationError("Los ingresos actuales deben ser un valor numérico.")
    if isinstance(value, int):
        number = value
    elif isinstance(value, float):
        number = int(round(value))
    else:
        digits = re.sub(r"[^0-9]", "", str(value))
        if not digits:
            raise ValidationError("Los ingresos actuales deben ser un valor numérico.")
        number = int(digits)
    if number <= 0:
        raise ValidationError("Los ingresos actuales deben ser mayores que cero.")
    return number


def validate_identification_number(value: str) -> str:
    """Validate that the identification contains digits only."""
    text = str(value).strip()
    if not text:
        raise ValidationError("El número de identificación es obligatorio.")
    if not text.isdigit():
        raise ValidationError("El número de identificación solo debe contener números.")
    return text


def validate_full_name(value: str) -> str:
    """Validate that the full name contains letters and spaces only."""
    text = re.sub(r"\s+", " ", str(value)).strip()
    if not text:
        raise ValidationError("El nombre completo es obligatorio.")
    if len(text) < 3 or not NAME_PATTERN.fullmatch(text):
        raise ValidationError(
            "El nombre completo solo debe contener letras y espacios."
        )
    return text


def format_date(value: date) -> str:
    """Format a date as dd/mm/yyyy."""
    return value.strftime(DATE_FORMAT)


def parse_date(value: str) -> date:
    """Parse a dd/mm/yyyy string into a date object."""
    try:
        return datetime.strptime(str(value).strip(), DATE_FORMAT).date()
    except (TypeError, ValueError) as exc:
        raise ValidationError("La fecha debe tener el formato dd/mm/aaaa.") from exc


def calculate_base_fee(current_income: int, employment_mode: str) -> int:
    """Return the base affiliation fee according to the published tables."""
    if current_income < 1_000_000:
        raise ValidationError("Los ingresos deben ser de al menos $ 1.000.000 según la tabla de tarifas.")
    if employment_mode == EMPLOYEE:
        brackets = EMPLOYEE_BRACKETS
    elif employment_mode == INDEPENDENT:
        brackets = INDEPENDENT_BRACKETS
    else:
        raise ValidationError("Debe seleccionar una modalidad de empleo válida.")
    for upper_bound, fee in brackets:
        if upper_bound is None or current_income <= upper_bound:
            return fee
    return brackets[-1][1]


def calculate_affiliation_fee(
    current_income: int,
    desired_service: str,
    employment_mode: str,
) -> int:
    """Calculate the final fee: base bracket plus the service adjustment."""
    if desired_service not in SERVICES:
        raise ValidationError("Debe seleccionar un servicio deseado válido.")
    income = parse_income(current_income)
    base_fee = calculate_base_fee(income, employment_mode)
    if desired_service == PREVENTIVE_MEDICINE:
        surcharge = int(round(income * 0.10))
    else:
        surcharge = SERVICE_SURCHARGES.get(desired_service, 0)
    return int(base_fee + surcharge)


# ---------------------------------------------------------------------------
# Domain entities
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Affiliate:
    """An affiliate registered in the compensation fund.

    The class stores one complete record; it does not know which data
    structure contains it.  ``AffiliateDataStructure`` below owns the three
    linear structures.
    """

    identification_type: str
    identification_number: str
    full_name: str
    current_income: int
    desired_service: str
    employment_mode: str
    affiliation_fee: int
    affiliation_date: date

    def __post_init__(self) -> None:
        object.__setattr__(self, "identification_type", str(self.identification_type).strip().upper())
        object.__setattr__(self, "identification_number", validate_identification_number(self.identification_number))
        object.__setattr__(self, "full_name", validate_full_name(self.full_name))
        object.__setattr__(self, "current_income", parse_income(self.current_income))
        object.__setattr__(self, "affiliation_fee", int(self.affiliation_fee))

        if self.identification_type not in IDENTIFICATION_TYPES:
            raise ValidationError("Seleccione un tipo de identificación válido.")
        if self.desired_service not in SERVICES:
            raise ValidationError("Seleccione un servicio deseado válido.")
        if self.employment_mode not in EMPLOYMENT_MODES:
            raise ValidationError("Seleccione una modalidad de empleo válida.")
        if self.affiliation_fee < 0:
            raise ValidationError("La tarifa de afiliación no puede ser negativa.")
        if not isinstance(self.affiliation_date, date):
            raise ValidationError("La fecha de afiliación no es válida.")

    # -- Presentation helpers -------------------------------------------------
    @property
    def formatted_date(self) -> str:
        return format_date(self.affiliation_date)

    @property
    def formatted_income(self) -> str:
        return format_currency(self.current_income)

    @property
    def formatted_fee(self) -> str:
        return format_currency(self.affiliation_fee)

    @property
    def service_label(self) -> str:
        return SERVICE_LABELS[self.desired_service]

    @property
    def employment_label(self) -> str:
        return EMPLOYMENT_LABELS[self.employment_mode]

    def to_row(self) -> tuple[str, ...]:
        """Return the values displayed by one Treeview row."""
        return (
            self.identification_type,
            self.identification_number,
            self.full_name,
            self.formatted_income,
            self.service_label,
            self.employment_label,
            self.formatted_fee,
            self.formatted_date,
        )


@dataclass(frozen=True)
class StructureReport:
    """Result of the report requested for one data structure."""

    structure: str
    count: int
    total_fees: int
    average_income: float

    @property
    def formatted_total_fees(self) -> str:
        return format_currency(self.total_fees)

    @property
    def formatted_average_income(self) -> str:
        return format_currency(self.average_income)


# ---------------------------------------------------------------------------
# Linear data structures
# ---------------------------------------------------------------------------
class AffiliateDataStructure:
    """Manage the affiliates through a stack, a queue and a list.

    * Stack  -> Python ``list`` used with ``append`` / ``pop`` (LIFO).
    * Queue  -> ``collections.deque`` used with ``append`` / ``popleft`` (FIFO).
    * List   -> Python ``list`` used with ``append`` and removal by ID.

    ``EstructuraDatosAfiliado`` is kept as an alias because that is the name
    used by the assignment statement; the implementation follows the English
    naming convention required by the guide.
    """

    def __init__(self, access_password: str = ACCESS_PASSWORD) -> None:
        self.access_password = access_password
        self.stack: list[Affiliate] = []
        self.queue: deque[Affiliate] = deque()
        self.affiliate_list: list[Affiliate] = []

    # -- Access ---------------------------------------------------------------
    def validate_password(self, password: str) -> bool:
        """Compare the password entered in the login window."""
        return hmac.compare_digest(str(password), str(self.access_password))

    # -- Read -----------------------------------------------------------------
    def _collection(self, structure: str) -> Iterable[Affiliate]:
        if structure == STACK:
            return self.stack
        if structure == QUEUE:
            return self.queue
        if structure == LIST:
            return self.affiliate_list
        raise ValidationError("Seleccione una estructura de datos válida.")

    def records(self, structure: str) -> list[Affiliate]:
        """Return the records in the order in which the Treeview shows them.

        The stack is shown top-first (the last record appears at the top),
        the queue is shown front-first and the list keeps the arrival order.
        """
        self._collection(structure)  # validates the structure name
        if structure == STACK:
            return list(reversed(self.stack))
        if structure == QUEUE:
            return list(self.queue)
        return list(self.affiliate_list)

    def count(self, structure: str) -> int:
        return len(self.records(structure))

    def find_by_identification(self, structure: str, identification_number: str) -> Affiliate | None:
        number = validate_identification_number(identification_number)
        for affiliate in self.records(structure):
            if affiliate.identification_number == number:
                return affiliate
        return None

    # -- Write ----------------------------------------------------------------
    def register(self, structure: str, affiliate: Affiliate) -> Affiliate:
        """Insert an affiliate using the default behaviour of the structure."""
        self._collection(structure)
        if self.find_by_identification(structure, affiliate.identification_number) is not None:
            raise DuplicateAffiliateError(
                "Ya existe un afiliado con la identificación "
                f"{affiliate.identification_number} en la estructura "
                f"{STRUCTURE_LABELS[structure]}."
            )
        if structure == STACK:
            self.stack.append(affiliate)          # push
        elif structure == QUEUE:
            self.queue.append(affiliate)          # enqueue
        else:
            self.affiliate_list.append(affiliate)  # append at the end
        return affiliate

    def remove(self, structure: str, identification_number: str | None = None) -> Affiliate:
        """Remove one record following the behaviour of the structure.

        Stack: pop the top.  Queue: dequeue the front.  List: remove the
        affiliate whose identification number matches the argument.
        """
        self._collection(structure)
        if structure == STACK:
            if not self.stack:
                raise EmptyStructureError("La pila está vacía; no hay registros para desapilar.")
            return self.stack.pop()
        if structure == QUEUE:
            if not self.queue:
                raise EmptyStructureError("La cola está vacía; no hay registros para desencolar.")
            return self.queue.popleft()
        if not self.affiliate_list:
            raise EmptyStructureError("La lista está vacía; no hay registros para eliminar.")
        if identification_number is None:
            raise ValidationError("Digite el número de identificación del afiliado a eliminar.")
        affiliate = self.find_by_identification(LIST, identification_number)
        if affiliate is None:
            raise AffiliateNotFoundError(
                "No existe un afiliado con la identificación "
                f"{identification_number} en la lista."
            )
        self.affiliate_list.remove(affiliate)
        return affiliate

    # -- Reports --------------------------------------------------------------
    def build_report(self, structure: str) -> StructureReport:
        """Build the report required for the selected structure."""
        records = self.records(structure)
        count = len(records)
        total_fees = sum(record.affiliation_fee for record in records)
        average_income = (
            sum(record.current_income for record in records) / count if count else 0.0
        )
        return StructureReport(
            structure=structure,
            count=count,
            total_fees=total_fees,
            average_income=average_income,
        )

    def report_text(self, structure: str) -> str:
        """Return the Spanish text displayed in the read-only report field."""
        report = self.build_report(structure)
        label = STRUCTURE_LABELS[structure]
        if structure == STACK:
            return (
                f"{label}: {report.count} registro(s) | "
                f"Suma de tarifas de afiliación: {report.formatted_total_fees}"
            )
        if structure == QUEUE:
            return f"{label}: {report.count} registro(s) en espera"
        return (
            f"{label}: {report.count} registro(s) | "
            f"Promedio de ingresos actuales: {report.formatted_average_income}"
        )

    # -- Convenience ----------------------------------------------------------
    def summary(self) -> dict[str, int]:
        """Return how many records each structure contains."""
        return {
            STACK: len(self.stack),
            QUEUE: len(self.queue),
            LIST: len(self.affiliate_list),
        }

    def clear_all(self) -> None:
        """Remove every record (used by tests and by a full reset)."""
        self.stack.clear()
        self.queue.clear()
        self.affiliate_list.clear()


# The statement names the class in Spanish; the alias preserves that contract
# while the implementation uses the English naming convention.
EstructuraDatosAfiliado = AffiliateDataStructure
