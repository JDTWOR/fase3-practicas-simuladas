# -*- coding: utf-8 -*-
"""Automated tests for the Caja Compensandote business logic.

Run with:
    python -m unittest -v test_affiliate_data_structure.py
or simply:
    python test_affiliate_data_structure.py
"""

from datetime import date
import unittest

from affiliate_data_structure import (
    ACCESS_PASSWORD,
    EMPLOYEE,
    INDEPENDENT,
    LIST,
    PARK_ADMISSION,
    PREVENTIVE_MEDICINE,
    QUEUE,
    STACK,
    TRAINING_COURSE,
    TRAVEL_PACKAGE,
    UNEMPLOYMENT_SUBSIDY,
    Affiliate,
    AffiliateDataStructure,
    AffiliateNotFoundError,
    DuplicateAffiliateError,
    EmptyStructureError,
    EstructuraDatosAfiliado,
    ValidationError,
    calculate_affiliation_fee,
    calculate_base_fee,
    format_currency,
    parse_date,
    parse_income,
    validate_full_name,
    validate_identification_number,
)


def make_affiliate(
    number: str = "1023456789",
    name: str = "Ana Maria Perez",
    income: int = 1_500_000,
    service: str = UNEMPLOYMENT_SUBSIDY,
    mode: str = EMPLOYEE,
    fee: int | None = None,
    day: date | None = None,
) -> Affiliate:
    if fee is None:
        fee = calculate_affiliation_fee(income, service, mode)
    return Affiliate(
        identification_type="CC",
        identification_number=number,
        full_name=name,
        current_income=income,
        desired_service=service,
        employment_mode=mode,
        affiliation_fee=fee,
        affiliation_date=day or date(2026, 9, 15),
    )


class FeeCalculationTests(unittest.TestCase):
    def test_employee_brackets(self):
        cases = {
            1_000_000: 45_000,
            1_500_000: 45_000,
            2_000_000: 45_000,
            2_500_000: 60_000,
            3_500_000: 75_000,
            4_500_000: 90_000,
            5_500_000: 150_000,
        }
        for income, expected in cases.items():
            with self.subTest(income=income):
                self.assertEqual(calculate_base_fee(income, EMPLOYEE), expected)

    def test_independent_brackets(self):
        cases = {
            1_000_000: 10_000,
            1_500_000: 10_000,
            2_000_000: 10_000,
            2_500_000: 20_000,
            3_500_000: 30_000,
            4_500_000: 40_000,
            5_500_000: 80_000,
        }
        for income, expected in cases.items():
            with self.subTest(income=income):
                self.assertEqual(calculate_base_fee(income, INDEPENDENT), expected)

    def test_service_surcharges_for_employee(self):
        cases = {
            UNEMPLOYMENT_SUBSIDY: 45_000,
            PARK_ADMISSION: 47_500,
            TRAINING_COURSE: 52_500,
            TRAVEL_PACKAGE: 55_000,
            PREVENTIVE_MEDICINE: 195_000,  # 45.000 + 10 % of 1.500.000
        }
        for service, expected in cases.items():
            with self.subTest(service=service):
                self.assertEqual(
                    calculate_affiliation_fee(1_500_000, service, EMPLOYEE),
                    expected,
                )

    def test_preventive_medicine_uses_ten_percent_of_income(self):
        self.assertEqual(
            calculate_affiliation_fee(2_350_000, PREVENTIVE_MEDICINE, INDEPENDENT),
            20_000 + 235_000,
        )

    def test_fee_with_thousands_separator(self):
        self.assertEqual(
            calculate_affiliation_fee("2.500.000", PARK_ADMISSION, EMPLOYEE),
            62_500,
        )

    def test_invalid_service_is_rejected(self):
        with self.assertRaises(ValidationError):
            calculate_affiliation_fee(1_500_000, "Servicio inventado", EMPLOYEE)

    def test_invalid_employment_mode_is_rejected(self):
        with self.assertRaises(ValidationError):
            calculate_base_fee(1_500_000, "Desconocido")

    def test_income_must_be_positive(self):
        with self.assertRaises(ValidationError):
            parse_income("0")
        with self.assertRaises(ValidationError):
            parse_income("")


class ValidationTests(unittest.TestCase):
    def test_identification_accepts_digits_only(self):
        self.assertEqual(validate_identification_number(" 1023456789 "), "1023456789")
        for value in ("", "ABC123", "10-20", "1.5"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validate_identification_number(value)

    def test_full_name_accepts_letters_accents_and_spaces(self):
        self.assertEqual(validate_full_name("  Ana   María  Pérez "), "Ana María Pérez")
        self.assertEqual(validate_full_name("Jhon Deivid Rojas Rodriguez"), "Jhon Deivid Rojas Rodriguez")
        for value in ("", "A", "Ana 123", "Ana-Pérez", "Ana@Perez"):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validate_full_name(value)

    def test_currency_format(self):
        self.assertEqual(format_currency(45_000), "$ 45.000")
        self.assertEqual(format_currency(1_500_000), "$ 1.500.000")
        self.assertEqual(format_currency(0), "$ 0")

    def test_date_format_and_parse(self):
        value = date(2026, 9, 15)
        self.assertEqual(value.strftime("%d/%m/%Y"), "15/09/2026")
        self.assertEqual(parse_date("15/09/2026"), value)
        with self.assertRaises(ValidationError):
            parse_date("2026-09-15")

    def test_password(self):
        data = AffiliateDataStructure()
        self.assertTrue(data.validate_password(ACCESS_PASSWORD))
        self.assertTrue(data.validate_password("Caja"))
        self.assertFalse(data.validate_password("caja"))
        self.assertFalse(data.validate_password(""))

    def test_spanish_alias_points_to_the_same_class(self):
        self.assertIs(EstructuraDatosAfiliado, AffiliateDataStructure)


class StackTests(unittest.TestCase):
    def setUp(self):
        self.data = AffiliateDataStructure()
        self.first = make_affiliate("1001", "Ana Maria Perez", 1_500_000)
        self.second = make_affiliate("1002", "Luis Carlos Gomez", 2_500_000)

    def test_push_and_lifo_order(self):
        self.data.register(STACK, self.first)
        self.data.register(STACK, self.second)
        self.assertEqual([a.identification_number for a in self.data.records(STACK)], ["1002", "1001"])
        removed = self.data.remove(STACK)
        self.assertIs(removed, self.second)
        self.assertEqual([a.identification_number for a in self.data.records(STACK)], ["1001"])

    def test_empty_stack_cannot_be_popped(self):
        with self.assertRaises(EmptyStructureError):
            self.data.remove(STACK)

    def test_duplicate_identification_is_rejected_in_stack(self):
        self.data.register(STACK, self.first)
        with self.assertRaises(DuplicateAffiliateError):
            self.data.register(STACK, make_affiliate("1001", "Otra Persona", 2_000_000))

    def test_stack_report_sums_fees(self):
        self.data.register(STACK, self.first)
        self.data.register(STACK, make_affiliate("1003", "Pedro Jose Ruiz", 1_500_000, PARK_ADMISSION))
        report = self.data.build_report(STACK)
        self.assertEqual(report.count, 2)
        self.assertEqual(report.total_fees, 45_000 + 47_500)
        self.assertIn("$ 92.500", self.data.report_text(STACK))


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.data = AffiliateDataStructure()
        self.first = make_affiliate("2001", "Ana Maria Perez", 1_500_000)
        self.second = make_affiliate("2002", "Luis Carlos Gomez", 2_500_000)

    def test_enqueue_and_fifo_order(self):
        self.data.register(QUEUE, self.first)
        self.data.register(QUEUE, self.second)
        self.assertEqual([a.identification_number for a in self.data.records(QUEUE)], ["2001", "2002"])
        removed = self.data.remove(QUEUE)
        self.assertIs(removed, self.first)
        self.assertEqual([a.identification_number for a in self.data.records(QUEUE)], ["2002"])

    def test_empty_queue_cannot_be_dequeued(self):
        with self.assertRaises(EmptyStructureError):
            self.data.remove(QUEUE)

    def test_queue_report_counts_records(self):
        self.data.register(QUEUE, self.first)
        self.data.register(QUEUE, self.second)
        report = self.data.build_report(QUEUE)
        self.assertEqual(report.count, 2)
        self.assertIn("2 registro(s) en espera", self.data.report_text(QUEUE))


class ListTests(unittest.TestCase):
    def setUp(self):
        self.data = AffiliateDataStructure()
        self.first = make_affiliate("3001", "Ana Maria Perez", 1_500_000)
        self.second = make_affiliate("3002", "Luis Carlos Gomez", 2_500_000)
        self.third = make_affiliate("3003", "Pedro Jose Ruiz", 3_500_000)

    def test_append_keeps_arrival_order(self):
        for affiliate in (self.first, self.second, self.third):
            self.data.register(LIST, affiliate)
        self.assertEqual(
            [a.identification_number for a in self.data.records(LIST)],
            ["3001", "3002", "3003"],
        )

    def test_remove_by_identification(self):
        for affiliate in (self.first, self.second, self.third):
            self.data.register(LIST, affiliate)
        removed = self.data.remove(LIST, "3002")
        self.assertIs(removed, self.second)
        self.assertEqual(
            [a.identification_number for a in self.data.records(LIST)],
            ["3001", "3003"],
        )

    def test_remove_unknown_identification(self):
        self.data.register(LIST, self.first)
        with self.assertRaises(AffiliateNotFoundError):
            self.data.remove(LIST, "9999")

    def test_remove_without_identification(self):
        self.data.register(LIST, self.first)
        with self.assertRaises(ValidationError):
            self.data.remove(LIST)

    def test_empty_list_cannot_be_removed(self):
        with self.assertRaises(EmptyStructureError):
            self.data.remove(LIST, "3001")

    def test_list_report_averages_income(self):
        for affiliate in (self.first, self.second, self.third):
            self.data.register(LIST, affiliate)
        report = self.data.build_report(LIST)
        self.assertEqual(report.count, 3)
        self.assertEqual(report.average_income, 2_500_000)
        self.assertIn("$ 2.500.000", self.data.report_text(LIST))

    def test_duplicate_identification_is_rejected_in_list(self):
        self.data.register(LIST, self.first)
        with self.assertRaises(DuplicateAffiliateError):
            self.data.register(LIST, make_affiliate("3001", "Otra Persona", 2_000_000))

    def test_find_by_identification(self):
        self.data.register(LIST, self.first)
        self.assertIs(self.data.find_by_identification(LIST, "3001"), self.first)
        self.assertIsNone(self.data.find_by_identification(LIST, "9999"))


class IntegrationTests(unittest.TestCase):
    def test_each_structure_is_independent(self):
        data = AffiliateDataStructure()
        data.register(STACK, make_affiliate("4001", "Ana Maria Perez", 1_500_000))
        data.register(QUEUE, make_affiliate("4001", "Ana Maria Perez", 1_500_000))
        self.assertEqual(data.summary(), {STACK: 1, QUEUE: 1, LIST: 0})
        data.register(LIST, make_affiliate("4001", "Ana Maria Perez", 1_500_000))
        self.assertEqual(data.summary(), {STACK: 1, QUEUE: 1, LIST: 1})

    def test_full_record_row(self):
        affiliate = make_affiliate("1023456789", "Ana Maria Perez", 1_500_000, PARK_ADMISSION)
        row = affiliate.to_row()
        self.assertEqual(row[0], "CC")
        self.assertEqual(row[1], "1023456789")
        self.assertEqual(row[2], "Ana Maria Perez")
        self.assertEqual(row[3], "$ 1.500.000")
        self.assertEqual(row[4], "Ingreso a parque")
        self.assertEqual(row[5], "Empleado")
        self.assertEqual(row[6], "$ 47.500")
        self.assertEqual(row[7], "15/09/2026")

    def test_invalid_identification_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            Affiliate(
                identification_type="XX",
                identification_number="123",
                full_name="Ana Maria Perez",
                current_income=1_500_000,
                desired_service=UNEMPLOYMENT_SUBSIDY,
                employment_mode=EMPLOYEE,
                affiliation_fee=45_000,
                affiliation_date=date(2026, 9, 15),
            )

    def test_empty_reports_are_zero(self):
        data = AffiliateDataStructure()
        for structure in (STACK, QUEUE, LIST):
            report = data.build_report(structure)
            self.assertEqual(report.count, 0)
            self.assertEqual(report.total_fees, 0)
            self.assertEqual(report.average_income, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
