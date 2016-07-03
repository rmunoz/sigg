import logging

from decimal import Decimal

from gi.repository import Gtk

from constants import RESOURCES_DIR
from models import Settings
from util import init_db


class PreferencesWindow:

    def __init__(self, logger=None, parent=None):
        self.logger = logger or logging.getLogger(__name__)

        self.load_data_from_database()
        self.build_ui()
        self.populate_form()

        self.window.set_modal(True)
        self.window.set_transient_for(parent)

        self.window.show_all()

    def load_data_from_database(self):
        self.logger.debug("Loading data from db...")
        if Settings.select().count() == 0:
            Settings(vat=21.00, invoice_number="0000000001").save()
        self.settings = Settings.select().get()
        self.logger.debug("Settings loaded")

    def build_ui(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(RESOURCES_DIR + "/preferences_window.glade")

        self.builder.connect_signals(self)

        self.window = self.builder.get_object("preferences_window")
        self.vat_entry = self.builder.get_object("vat_entry")
        self.invoice_number_entry = self.builder.get_object(
                "invoice_number_entry"
                )

    def populate_form(self):
        self.logger.debug("populate_form")

        self.vat_entry.set_text(str(self.settings.vat))
        self.invoice_number_entry.set_text(self.settings.invoice_number)

    def on_reset_db_clicked(self, button):
        self.logger.debug("reset_db")
        init_db()

    def on_delete_window(self, *args):
        self.window.hide()

    def on_quit_button_clicked(self, button):
        self.window.hide()

    def on_save_button_clicked(self, button):
        self.logger.debug("on_save_button_clicked")

        if self.validate_settings():
            self.logger.debug("Saving settings...")
            self.settings.save()
        else:
            dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "Invalid values")

            dialog.run()
            dialog.destroy()

    def validate_settings(self):
        self.logger.debug("validate_settings")

        retvalue = False

        try:
            self.settings.vat = Decimal(self.vat_entry.get_text())
            int(self.invoice_number_entry.get_text())
            self.settings.invoice_number = self.invoice_number_entry.get_text()

            retvalue = True

        except BaseException as ex:
            self.logger.error("Exception: " + str(ex))

        return retvalue
