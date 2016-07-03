import logging

# from decimal import Decimal
from datetime import datetime
import subprocess
import os
from gi.repository import Gtk

from util import invoice
from models import Settings
from constants import RESOURCES_DIR


class InvoicesWindow:

    def __init__(self, company, logger=None, parent=None):
        self.logger = logger or logging.getLogger(__name__)

        self.company = company

        self.load_data_from_database()
        self.build_ui()
        self.populate_form()

        self.window.set_modal(True)
        self.window.set_transient_for(parent)

        self.window.show_all()

    def load_data_from_database(self):
        self.logger.debug("Loading data from db...")
        self.settings = Settings.select().get()
        self.logger.debug(
                "Next invoice number: %s", self.settings.invoice_number
                )

    def build_ui(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(RESOURCES_DIR + "/invoices_window.glade")

        self.builder.connect_signals(self)

        self.window = self.builder.get_object("invoices_window")
        self.company_code_label = self.builder.get_object("company_code_label")
        self.company_name_label = self.builder.get_object("company_name_label")
        self.delivery_notes_number = self.builder.get_object(
                "delivery_notes_number"
                )
        self.invoice_number_entry = self.builder.get_object(
                "invoice_number_entry"
                )
        self.invoice_date_entry = self.builder.get_object(
                "invoice_date_entry"
                )
        self.invoice_number_entry.editable = False

    def populate_form(self):
        self.logger.debug("populate_form")

        self.company_code_label.set_text(self.company.code)
        self.company_name_label.set_text(self.company.name)
        self.invoice_number_entry.set_text(self.settings.invoice_number)
        self.delivery_notes_number.set_text(
                str(len(self.company.delivery_notes))
                )
        self.invoice_date_entry.set_text(datetime.now().strftime("%Y-%m-%d"))

    def on_delete_window(self, *args):
        self.window.hide()

    def on_quit_button_clicked(self, button):
        self.window.hide()

    def on_invoice_button_clicked(self, button):
        self.logger.debug("on_invoice_button_clicked")
        pdf_file = "/tmp/test.pdf"
        invoice(
                company=self.company,
                invoice_number=self.invoice_number_entry.get_text(),
                invoice_date=self.invoice_date_entry.get_text(),
                vat=self.settings.vat,
                pdf_filename=pdf_file
                )

        if os.name == 'nt':
            os.startfile(pdf_file)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', pdf_file))

    def on_invoice_number_checkbutton_toggled(self, button):
        self.logger.debug("on_invoice_number_checkbutton_toggled")
        self.invoice_number_entry.editable = button.get_active()
