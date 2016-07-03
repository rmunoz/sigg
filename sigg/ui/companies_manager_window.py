import logging

from gi.repository import Gtk

from constants import RESOURCES_DIR
from util import EXPIRATION_DAYS, PAYMENT_TYPES
from models import Company

from .vehicles_manager_window import VehiclesManagerWindow
from .delivery_notes_manager_window import DeliveryNotesManagerWindow
from .preferences_window import PreferencesWindow
from .invoices_window import InvoicesWindow


class CompaniesManagerWindow:

    CODE_COLUMN = 0
    NAME_COLUMN = 1
    NIF_COLUMN = 2
    REMOVE_COLUMN = 3
    DELIVERY_NOTES_COLUMN = 4
    INVOICE_COLUMN = 5

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        self.load_data_from_database()
        self.build_ui()

        self.window.show_all()

    def load_data_from_database(self):
        self.logger.debug("Loading data from db...")
        self.companies = Company.select()
        self.logger.debug("%s companies loaded", len(self.companies))

    def build_ui(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(RESOURCES_DIR + "/companies_window.glade")

        self.builder.connect_signals(self)

        self.window = self.builder.get_object("companies_window")
        # basic data widgets
        self.code_entry = self.builder.get_object("code_entry")
        self.name_entry = self.builder.get_object("name_entry")
        self.nif_entry = self.builder.get_object("nif_entry")

        # contact data widgets
        self.address_entry = self.builder.get_object("address_entry")
        self.city_entry = self.builder.get_object("city_entry")
        self.state_entry = self.builder.get_object("state_entry")
        self.zip_code_entry = self.builder.get_object("zip_code_entry")
        self.phone_entry = self.builder.get_object("phone_entry")
        self.contact_person_entry = self.builder.get_object(
                "contact_person_entry")
        self.alternative_phone_entry = self.builder.get_object(
                "alternative_phone_entry")
        self.fax_entry = self.builder.get_object("fax_entry")
        self.email_entry = self.builder.get_object("email_entry")

        # invoicing data entries
        self.iban_entry = self.builder.get_object("iban_entry")
        self.bank_name_entry = self.builder.get_object("bank_name_entry")
        self.payment_type_combo = self.builder.get_object("payment_type_combo")
        self.expiration_days_combo = self.builder.get_object(
                "expiration_days_combo")
        self.first_payment_day_entry = self.builder.get_object(
                "first_payment_day_entry")
        self.second_payment_day_entry = self.builder.get_object(
                "second_payment_day_entry")
        self.third_payment_day_entry = self.builder.get_object(
                "third_payment_day_entry")

        self.companies_view = self.builder.get_object("companies_view")
        self.companies_model = self.builder.get_object("companies_model")
        self.populate_widgets()

    def populate_widgets(self):
        self.populate_treeview_model()
        self.populate_payment_type_combo()
        self.populate_expiration_days_combo()

    def populate_payment_type_combo(self):
        for payment_type in PAYMENT_TYPES.values():
            self.payment_type_combo.append(payment_type, payment_type)

    def populate_expiration_days_combo(self):
        for expiration_day in EXPIRATION_DAYS:
            eday = str(expiration_day)
            self.expiration_days_combo.append(eday, eday)

    def populate_treeview_model(self):
        for company in self.companies:
            self.companies_model.append(
                    [company.code, company.name, company.nif,
                     "gtk-delete", "gtk-file", "gtk-print"]
                    )

    def populate_form(self, company):
        self.logger.debug("populate_form")

        self.code_entry.set_text(company.code)
        self.name_entry.set_text(company.name)
        self.nif_entry.set_text(company.nif)

        self.address_entry.set_text(company.address)
        self.city_entry.set_text(company.city)
        self.state_entry.set_text(company.state)
        self.zip_code_entry.set_text(company.zip_code)
        self.phone_entry.set_text(company.phone)
        self.contact_person_entry.set_text(company.contact_person)
        self.alternative_phone_entry.set_text(company.alternative_phone)
        self.fax_entry.set_text(company.fax)
        self.email_entry.set_text(company.email)

        self.iban_entry.set_text(company.iban)
        self.bank_name_entry.set_text(company.bank_name)
        self.payment_type_combo.set_active_id(
                PAYMENT_TYPES[company.payment_type]
                )
        self.expiration_days_combo.set_active_id(
                str(EXPIRATION_DAYS[company.expiration_days])
                )
        self.first_payment_day_entry.set_text(str(company.first_payment_day))
        self.second_payment_day_entry.set_text(str(company.second_payment_day))
        self.third_payment_day_entry.set_text(str(company.third_payment_day))

        self.code_entry.editable = False

    def clean_form(self):
        self.code_entry.set_text("")
        self.name_entry.set_text("")
        self.nif_entry.set_text("")

        self.address_entry.set_text("")
        self.city_entry.set_text("")
        self.state_entry.set_text("")
        self.zip_code_entry.set_text("")
        self.phone_entry.set_text("")
        self.contact_person_entry.set_text("")
        self.alternative_phone_entry.set_text("")
        self.fax_entry.set_text("")
        self.email_entry.set_text("")

        self.iban_entry.set_text("")
        self.bank_name_entry.set_text("")
        self.payment_type_combo.set_active_id(None)
        self.expiration_days_combo.set_active_id(None)
        self.first_payment_day_entry.set_text("")
        self.second_payment_day_entry.set_text("")
        self.third_payment_day_entry.set_text("")

        self.code_entry.editable = True
        self.companies_view.get_selection().unselect_all()

    def on_vehicles_button_clicked(self, button):
        self.logger.debug("on_vehicles_button_clicked")
        VehiclesManagerWindow(parent=self.window)

    def on_settings_button_clicked(self, button):
        self.logger.debug("on_setting_button_clicked")
        PreferencesWindow(parent=self.window)

    def on_delete_window(self, *args):
        Gtk.main_quit(*args)

    def on_quit_button_clicked(self, button):
        Gtk.main_quit()

    def on_clean_button_clicked(self, button):
        self.logger.debug("on_clean_button_clicked")
        self.clean_form()

    def on_save_button_clicked(self, button):
        self.logger.debug("on_save_button_clicked")

        company = self.validate_company()

        if company is None:
            dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "Invalid values"
                    )

            dialog.run()
            dialog.destroy()
        else:
            self.logger.debug("Trying to find company: %s", company.code)

            query = company.select().where(Company.code == company.code)
            if query.exists():
                dialog = Gtk.MessageDialog(
                        self.window, 0, Gtk.MessageType.QUESTION,
                        Gtk.ButtonsType.YES_NO,
                        "The company already exists, do you want to update it?"
                        )

                if dialog.run() == Gtk.ResponseType.YES:
                    self.update_company(company)

                dialog.destroy()
            else:
                self.create_company(company)

            self.clean_form()

    def on_row_activated(self, treeview, path, column):
        self.logger.debug("on_row_activated")

        tree_iter = self.companies_model.get_iter(path)
        code = self.companies_model.get_value(tree_iter, self.CODE_COLUMN)
        company = Company.select().where(Company.code == code).get()

        column_id = column.get_sort_column_id()
        if column_id == self.REMOVE_COLUMN:
            dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.YES_NO,
                    "Are you sure to remove the company?"
                    )

            if dialog.run() == Gtk.ResponseType.YES:
                self.delete_company(company)

            dialog.destroy()
        elif column_id == self.DELIVERY_NOTES_COLUMN:
            DeliveryNotesManagerWindow(company=company, parent=self.window)
        elif column_id == self.INVOICE_COLUMN:
            InvoicesWindow(company=company, parent=self.window)
        else:
            self.populate_form(company)

    def get_iter_from_selected_row(self, code):
        self.logger.debug("get_iter_from_selected_row")

        for row in self.companies_model:
            row_code = row.model.get_value(row.iter, self.CODE_COLUMN)
            self.logger.debug("Row code: %s", row_code)
            if row_code == code:
                return row.iter

        self.logger.error("Cannot find element")
        raise RuntimeError("Cannot find element: % in model", code)

    def validate_company(self):
        # TODO better checking
        self.logger.debug("validate_company")

        company = None
        try:
            code = self.code_entry.get_text()
            name = self.name_entry.get_text()
            nif = self.nif_entry.get_text()

            address = self.address_entry.get_text()
            city = self.city_entry.get_text()
            state = self.state_entry.get_text()
            zip_code = self.zip_code_entry.get_text()
            phone = self.phone_entry.get_text()
            contact_person = self.contact_person_entry.get_text()
            alternative_phone = self.alternative_phone_entry.get_text()
            fax = self.fax_entry.get_text()
            email = self.email_entry.get_text()

            iban = self.iban_entry.get_text()
            bank_name = self.bank_name_entry.get_text()

            pt_str = self.payment_type_combo.get_active_text()
            payment_type = PAYMENT_TYPES.inv[pt_str]

            expiration_days = self.expiration_days_combo.get_active()

            fpday = self.first_payment_day_entry.get_text()
            spday = self.second_payment_day_entry.get_text()
            tpday = self.third_payment_day_entry.get_text()

            first_payment_day = int(fpday) if fpday else None
            second_payment_day = int(spday) if spday else None
            third_payment_day = int(tpday) if tpday else None

            company = Company(
                code=code, name=name, nif=nif, address=address, city=city,
                state=state, zip_code=zip_code, phone=phone,
                contact_person=contact_person,
                alternative_phone=alternative_phone, fax=fax, email=email,
                iban=iban, bank_name=bank_name, payment_type=payment_type,
                expiration_days=expiration_days,
                first_payment_day=first_payment_day,
                second_payment_day=second_payment_day,
                third_payment_day=third_payment_day
                )

        except Exception as ex:
            self.logger.error("Exception: %: %", ex.errno, ex.strerror)
            self.logger.error("Invalid data")

        return company

    def create_company(self, company):
        self.logger.debug("create_company")

        self.logger.info("saving company to database")
        company.save()

        self.logger.info("adding company to model")
        self.companies_model.append([company.code, company.name, company.nif,
                                    "gtk-delete", "gtk-file", "gtk-print"]
                                    )

    def update_company(self, company):
        self.logger.debug("update_company")

        self.logger.info("saving company to database")
        self.logger.debug("company: %s", company)
        Company.update(
                code=company.code, name=company.name, nif=company.nif,
                address=company.address, city=company.city,
                state=company.state, zip_code=company.zip_code,
                phone=company.phone, contact_person=company.contact_person,
                alternative_phone=company.alternative_phone,
                fax=company.fax, email=company.email, iban=company.iban,
                bank_name=company.bank_name, payment_type=company.payment_type,
                expiration_days=company.expiration_days,
                first_payment_day=company.first_payment_day,
                second_payment_day=company.second_payment_day,
                third_payment_day=company.third_payment_day
                ).execute()

        self.logger.info("updating company to model")
        tree_iter = self.get_iter_from_selected_row(company.code)
        self.companies_model.set(
                tree_iter,
                [self.CODE_COLUMN, self.NAME_COLUMN, self.NIF_COLUMN],
                [company.code, company.name, company.nif]
                )

    def delete_company(self, company):
        self.logger.debug("delete_company")

        self.logger.info("deleting company from database")
        Company.delete().where(Company.code == company.code).execute()

        self.logger.info("removing company from model")
        tree_iter = self.get_iter_from_selected_row(company.code)
        self.companies_model.remove(tree_iter)
