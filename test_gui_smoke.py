# -*- coding: utf-8 -*-
"""Functional verification of the graphical interface.

This script exercises the main GUI flows without a human operator.  It needs
a graphical environment; when Tk cannot create a window (for example, on a
server without DISPLAY), the tests are skipped with a clear message.

Run with:
    python -m unittest -v test_gui_smoke.py
On Linux without a desktop:
    xvfb-run -a python -m unittest -v test_gui_smoke.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
import unittest

import main
from affiliate_data_structure import (
    EMPLOYEE,
    INDEPENDENT,
    LIST,
    PARK_ADMISSION,
    PREVENTIVE_MEDICINE,
    QUEUE,
    STACK,
    UNEMPLOYMENT_SUBSIDY,
)


class GuiSmokeTests(unittest.TestCase):
    """Twelve end-to-end checks over the real Tkinter widgets."""

    app = None
    errors: list[str] = []

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.app = main.CompensandoteApp()
        except tk.TclError as exc:
            raise unittest.SkipTest(f"No hay entorno gráfico disponible: {exc}")
        cls.app.root.withdraw()
        cls.original_show_error = messagebox.showerror
        cls.original_ask_yes_no = messagebox.askyesno
        cls.original_ask_string = simpledialog.askstring
        messagebox.showerror = lambda _title, message, **_kwargs: cls.errors.append(message)
        messagebox.askyesno = lambda *_args, **_kwargs: True
        simpledialog.askstring = lambda *_args, **_kwargs: cls.next_identification

    @classmethod
    def tearDownClass(cls) -> None:
        messagebox.showerror = cls.original_show_error
        messagebox.askyesno = cls.original_ask_yes_no
        simpledialog.askstring = cls.original_ask_string
        if cls.app is not None:
            cls.app.root.destroy()

    def setUp(self) -> None:
        self.errors.clear()
        type(self).next_identification = ""
        self.app.data.clear_all()
        if self.app.main_view is None:
            self.app.show_main()
        view = self.app.main_view
        view.structure_var.set("Pila")
        view.clear_inputs()
        view.refresh_view()

    def _fill(self, number: str, name: str, income: str, service: str,
              mode: str = EMPLOYEE, structure: str = "Pila") -> None:
        view = self.app.main_view
        view.structure_var.set(structure)
        view.refresh_view()
        view.id_type_var.set("CC")
        view.id_number_var.set(number)
        view.full_name_var.set(name)
        view.income_var.set(income)
        view.service_var.set(service)
        view.mode_var.set(mode)
        view.update_fee()

    def test_01_login_flow(self) -> None:
        self.app.show_login()
        login = self.app.login_frame
        login.password_entry.insert(0, "incorrecta")
        login.attempt_login()
        self.assertIn("incorrecta", login.error_var.get())
        self.assertIsNotNone(self.app.login_frame)
        login.password_entry.delete(0, "end")
        login.password_entry.insert(0, "Caja")
        login.attempt_login()
        self.assertIsNone(self.app.login_frame)
        self.assertIsNotNone(self.app.main_view)
        self.assertEqual(self.app.root.title(), main.MAIN_TITLE)

    def test_02_about_dialog_opens(self) -> None:
        self.app.show_about()
        self.assertIsNotNone(self.app.about_dialog)
        self.assertTrue(self.app.about_dialog.winfo_exists())
        self.app.about_dialog.destroy()

    def test_03_fee_is_calculated(self) -> None:
        self._fill("5000", "Ana Maria Perez", "1500000", "Medicina preventiva")
        self.assertEqual(self.app.main_view.fee_var.get(), "$ 195.000")
        self._fill("5001", "Ana Maria Perez", "4200000", "Paquete de viaje", INDEPENDENT)
        self.assertEqual(self.app.main_view.fee_var.get(), "$ 50.000")

    def test_04_register_in_stack(self) -> None:
        self._fill("5100", "Ana Maria Perez", "1500000", "Ingreso a parque")
        self.app.main_view.register_affiliate()
        self.assertEqual(len(self.app.data.stack), 1)
        self.assertEqual(len(self.app.main_view.tree.get_children()), 1)

    def test_05_register_in_queue(self) -> None:
        self._fill("5200", "Luis Carlos Gomez", "2500000", "Curso de formación", structure="Cola")
        self.app.main_view.register_affiliate()
        self.assertEqual(len(self.app.data.queue), 1)
        self.assertIn("1 registro(s) en espera", self.app.data.report_text(QUEUE))

    def test_06_register_in_list(self) -> None:
        self._fill("5300", "Pedro Jose Ruiz", "3500000", "Paquete de viaje", structure="Lista")
        self.app.main_view.register_affiliate()
        self.assertEqual(len(self.app.data.affiliate_list), 1)
        self.assertIn("$ 3.500.000", self.app.data.report_text(LIST))

    def test_07_duplicate_identification_is_rejected(self) -> None:
        self._fill("5400", "Ana Maria Perez", "1500000", "Ingreso a parque")
        self.app.main_view.register_affiliate()
        self._fill("5400", "Otra Persona", "2000000", "Curso de formación")
        self.app.main_view.register_affiliate()
        self.assertTrue(self.errors)
        self.assertIn("Ya existe", self.errors[0])
        self.assertEqual(len(self.app.data.stack), 1)

    def test_08_clear_keeps_records(self) -> None:
        self._fill("5500", "Ana Maria Perez", "1500000", "Ingreso a parque")
        self.app.main_view.register_affiliate()
        self.app.main_view.clear_form()
        self.assertEqual(self.app.main_view.id_number_var.get(), "")
        self.assertEqual(self.app.main_view.full_name_var.get(), "")
        self.assertEqual(len(self.app.data.stack), 1)

    def test_09_reports_use_the_selected_structure(self) -> None:
        self._fill("5600", "Ana Maria Perez", "1500000", "Ingreso a parque")
        self.app.main_view.register_affiliate()
        self._fill("5601", "Luis Carlos Gomez", "2500000", "Curso de formación")
        self.app.main_view.register_affiliate()
        report = self.app.data.report_text(STACK)
        self.assertIn("$ 115.000", report)
        self.assertEqual(self.app.data.build_report(STACK).count, 2)

    def test_10_delete_stack_and_queue(self) -> None:
        self._fill("5700", "Ana Maria Perez", "1500000", "Ingreso a parque")
        self.app.main_view.register_affiliate()
        self._fill("5701", "Luis Carlos Gomez", "2500000", "Curso de formación")
        self.app.main_view.register_affiliate()
        self.app.main_view.structure_var.set("Pila")
        self.app.main_view.refresh_view()
        self.app.main_view.delete_affiliate()
        self.assertEqual([a.identification_number for a in self.app.data.stack], ["5700"])

        self.app.main_view.structure_var.set("Cola")
        self._fill("5800", "Pedro Jose Ruiz", "3500000", "Paquete de viaje", structure="Cola")
        self.app.main_view.register_affiliate()
        self.app.main_view.delete_affiliate()
        self.assertEqual(len(self.app.data.queue), 0)

    def test_11_structure_switch_refreshes_tree(self) -> None:
        self._fill("5950", "Ana Maria Perez", "1500000", "Ingreso a parque")
        self.app.main_view.register_affiliate()
        view = self.app.main_view
        view.structure_var.set("Cola")
        view.refresh_view()
        self.assertEqual(len(view.tree.get_children()), 0)
        self.assertIn("Cola", view.report_widget.get("1.0", "end"))
        view.structure_var.set("Pila")
        view.refresh_view()
        self.assertEqual(len(view.tree.get_children()), 1)

    def test_12_delete_from_list_by_identification(self) -> None:
        self._fill("5900", "Ana Maria Perez", "1500000", "Ingreso a parque", structure="Lista")
        self.app.main_view.register_affiliate()
        self._fill("5901", "Luis Carlos Gomez", "2500000", "Curso de formación", structure="Lista")
        self.app.main_view.register_affiliate()
        type(self).next_identification = "5900"
        self.app.main_view.delete_affiliate()
        self.assertEqual([a.identification_number for a in self.app.data.affiliate_list], ["5901"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
