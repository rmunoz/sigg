import logging

from decimal import Decimal

from gi.repository import Gtk

from constants import RESOURCES_DIR
from util import ITEM_TYPES
from models import Vehicle, DeliveryNote, DeliveryNoteItem


class DeliveryNotesManagerWindow:

    CODE_COLUMN = 0
    DATE_COLUMN = 1
    VEHICLE_NUMBER_COLUMN = 2
    INVOICED_COLUMN = 3
    REMOVE_COLUMN = 4

    ITEM_TYPE_COLUMN = 0
    UNITS_COLUMN = 1
    PRICE_COLUMN = 2
    SUBTOTAL_COLUMN = 3
    REMOVE_ITEM_COLUMN = 4

    def __init__(self, company, parent=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)

        self.company = company
        self.selected_delivery_note = None

        self.load_data_from_database()
        self.build_ui()

        self.window.set_modal(True)
        self.window.set_transient_for(parent)

        self.window.show_all()

    def load_data_from_database(self):
        self.logger.debug("Loading data from db...")

    def build_ui(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(
                RESOURCES_DIR + "/delivery_notes_window.glade"
                )

        self.builder.connect_signals(self)

        self.window = self.builder.get_object("delivery_notes_window")

        self.company_code_label = self.builder.get_object("company_code_label")
        self.company_name_label = self.builder.get_object("company_name_label")

        self.code_entry = self.builder.get_object("code_entry")
        self.date_entry = self.builder.get_object("date_entry")
        self.vehicle_number_combo = self.builder.get_object(
                "vehicle_number_combo"
                )

        self.delivery_notes_view = self.builder.get_object(
                "delivery_notes_view"
                )
        self.delivery_notes_model = self.builder.get_object(
                "delivery_notes_model"
                )

        self.item_type_combo = self.builder.get_object("item_type_combo")
        self.units_entry = self.builder.get_object("units_entry")
        self.price_entry = self.builder.get_object("price_entry")
        self.description_entry = self.builder.get_object("description_entry")

        self.delivery_note_items_view = self.builder.get_object(
                "delivery_note_items_view"
                )
        self.delivery_note_items_model = self.builder.get_object(
                "delivery_note_items_model"
                )
        self.total_value_label = self.builder.get_object("total_value_label")

        self.populate_widgets()

        self.company_code_label.set_text(self.company.code)
        self.company_name_label.set_text(self.company.name)

    def populate_widgets(self):
        self.populate_delivery_notes_model()
        self.populate_vehicle_names_combo()
        self.populate_item_type_combo()

    def populate_item_type_combo(self):
        for payment_type in ITEM_TYPES.values():
            self.item_type_combo.append(payment_type, payment_type)

    def populate_vehicle_names_combo(self):
        for vehicle in Vehicle.select():
            self.vehicle_number_combo.append(
                    str(vehicle.number), str(vehicle.number)
                    )

    def populate_delivery_notes_model(self):
        for delivery_note in self.company.delivery_notes:
            self.logger.debug("dnote: %s", delivery_note)
            self.delivery_notes_model.append(
                [delivery_note.code, str(delivery_note.date),
                    delivery_note.vehicle.number, delivery_note.invoiced,
                    "gtk-delete"]
                )

    def populate_delivery_note_items_model(self, delivery_note):
        self.logger.debug("populate_delivery_note_items_model")

        self.delivery_note_items_model.clear()
        for delivery_note_item in delivery_note.items:
            self.logger.debug("dnote item: %s", delivery_note_item)
            subtotal = delivery_note_item.units * delivery_note_item.price
            self.delivery_note_items_model.append(
                [ITEM_TYPES[delivery_note_item.item_type],
                    delivery_note_item.units, str(delivery_note_item.price),
                    str(subtotal), "gtk-delete"]
                )

    def populate_delivery_note_form(self, delivery_note):
        self.logger.debug("populate_delivery_note_form")

        self.code_entry.set_text(delivery_note.code)
        self.date_entry.set_text(str(delivery_note.date))
        self.vehicle_number_combo.set_active_id(
                str(delivery_note.vehicle.number)
                )

        self.code_entry.editable = False

        self.populate_delivery_note_items_model(delivery_note)

    def populate_delivery_note_items_form(self, delivery_note_item):
        self.logger.debug("populate_items_form")

        self.item_type_combo.set_active_id(
                ITEM_TYPES[delivery_note_item.item_type]
                )
        self.units_entry.set_text(str(delivery_note_item.units))
        self.price_entry.set_text(str(delivery_note_item.price))
        self.description_entry.set_text(delivery_note_item.description)

    def clean_delivery_note_form(self):
        self.logger.debug("clean_delivery_note_form")

        self.code_entry.set_text("")
        self.date_entry.set_text("")
        self.vehicle_number_combo.set_active_id(None)

        self.delivery_notes_view.get_selection().unselect_all()
        self.code_entry.editable = True

        self.clean_items_form()

        self.total_value_label.set_text("0.00")

    def clean_items_form(self):
        self.logger.debug("clean_items_form")

        self.item_type_combo.set_active_id(None)
        self.units_entry.set_text("")
        self.price_entry.set_text("")
        self.description_entry.set_text("")

        self.delivery_note_items_view.get_selection().unselect_all()
        self.delivery_note_items_model.clear()

    def update_total(self):
        self.logger.debug("update_total")

        value = Decimal(0.00)
        for item in self.selected_delivery_note.items:
            value = value + (item.units * item.price)
            self.logger.debug("Value: %s", str(value))

        self.total_value_label.set_text(str(value))

    def on_delete_window(self, *args):
        self.window.hide()

    def on_quit_button_clicked(self, button):
        self.window.hide()

    def on_clean_button_clicked(self, button):
        self.logger.debug("on_clean_button_clicked")
        self.clean_delivery_note_form()

    def on_save_button_clicked(self, button):
        self.logger.debug("on_save_button_clicked")

        delivery_note = self.validate_delivery_note()

        if delivery_note is None:
            dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "Invalid values"
                    )

            dialog.run()
            dialog.destroy()
        else:
            self.logger.debug(
                    "Trying to find delivery_note: %s", delivery_note.code
                    )

            query = DeliveryNote.select().where(
                    DeliveryNote.code == delivery_note.code
                    )

            if query.exists():
                dialog = Gtk.MessageDialog(
                        self.window, 0, Gtk.MessageType.QUESTION,
                        Gtk.ButtonsType.YES_NO,
                        "The delivery note already exists,"
                        " do you want to update it?"
                        )

                if dialog.run() == Gtk.ResponseType.YES:
                    self.update_delivery_note(delivery_note)

                dialog.destroy()
            else:
                self.create_delivery_note(delivery_note)

            self.selected_delivery_note = delivery_note

    def on_add_item_button_clicked(self, button):
        self.logger.debug("on_add_item_button_clicked")

        delivery_note_item = DeliveryNoteItem()
        if self.validate_delivery_note_item(delivery_note_item):
            self.create_delivery_note_item(delivery_note_item)
        else:
            dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "Invalid values"
                    )

            dialog.run()
            dialog.destroy()

        self.update_total()

    def on_delivery_notes_view_row_activated(self, treeview, path, column):
        self.logger.debug("on_delivery_notes_view_row_activated")

        tree_iter = self.delivery_notes_model.get_iter(path)

        code = self.delivery_notes_model.get_value(tree_iter, self.CODE_COLUMN)
        delivery_note = DeliveryNote.select().where(
                DeliveryNote.code == code
                ).get()

        column_id = column.get_sort_column_id()
        if column_id == self.REMOVE_COLUMN:
            dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.YES_NO,
                    "Are you sure to remove the delivery note?"
                    )

            if dialog.run() == Gtk.ResponseType.YES:
                self.delete_delivery_note(delivery_note)
                self.clean_delivery_note_form()

            dialog.destroy()
        else:
            self.populate_delivery_note_form(delivery_note)
            self.selected_delivery_note = delivery_note
            self.update_total()

    def on_items_view_row_activated(self, treeview, path, column):
        self.logger.debug("on_items_view_row_activated")

        tree_iter = self.delivery_note_items_model.get_iter(path)
        item_type = self.delivery_note_items_model.get_value(
                tree_iter, self.ITEM_TYPE_COLUMN
                )

        dnote = self.selected_delivery_note
        self.logger.debug("item_type: %s", item_type)
        self.logger.debug("item_type: %s", ITEM_TYPES.inv[item_type])
        delivery_note_item = DeliveryNoteItem.select().where(
                (DeliveryNoteItem.delivery_note == dnote) and
                (DeliveryNoteItem.item_type == ITEM_TYPES.inv[item_type])
                ).get()

        column_id = column.get_sort_column_id()
        if column_id == self.REMOVE_ITEM_COLUMN:
            dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.YES_NO,
                    "Are you sure to remove the delivery note item?"
                    )

            if dialog.run() == Gtk.ResponseType.YES:
                self.delete_delivery_note_item(delivery_note_item)
                self.update_total()

            dialog.destroy()
        else:
            self.populate_delivery_note_items_form(delivery_note_item)

    def on_item_type_combo_changed(self, combo):
        self.logger.debug("on_item_type_combo_changed")

        price = "0.00"
        itype = combo.get_active_text()
        if itype:
            if ITEM_TYPES.inv[itype] == "HOURS":
                price = str(self.selected_delivery_note.vehicle.hour_price)
            elif ITEM_TYPES.inv[itype] == "KMS":
                price = str(self.selected_delivery_note.vehicle.km_price)

        self.price_entry.set_text(price)

    def get_iter_from_delivery_notes_model(self, code):
        self.logger.debug("get_iter_from_delivery_notes_model")

        for row in self.delivery_notes_model:
            row_code = row.model.get_value(row.iter, self.CODE_COLUMN)
            self.logger.debug("Row id: %s", row_code)
            if row_code == code:
                return row.iter

        self.logger.error("Cannot find element")
        raise RuntimeError("Cannot find element: % in model", id)

    def get_iter_from_delivery_note_items_model(self, item_type):
        self.logger.debug("get_iter_from_delivery_note_items_model")

        for row in self.delivery_note_items_model:
            row_itype = row.model.get_value(row.iter, self.ITEM_TYPE_COLUMN)
            self.logger.debug("Row itype: %s", row_itype)
            if row_itype == item_type:
                return row.iter

        self.logger.error("Cannot find element")
        raise RuntimeError("Cannot find element: % in model", id)

    def validate_delivery_note(self):
        self.logger.debug("validate_delivery_note")

        delivery_note = None
        try:
            code = self.code_entry.get_text()
            date = self.date_entry.get_text()
            vehicle_number = self.vehicle_number_combo.get_active_text()

            vehicle = Vehicle.select().where(
                    Vehicle.number == vehicle_number
                    ).get()

            delivery_note = DeliveryNote(
                code=code, date=date, company=self.company, vehicle=vehicle,
                invoiced=False
                )

        except Exception as ex:
            self.logger.error("Exception: %: %", ex.errno, ex.strerror)
            self.logger.error("Invalid data")

        return delivery_note

    def create_delivery_note(self, delivery_note):
        self.logger.debug("create_delivery_note")

        self.logger.info("saving delivery_note to database")
        delivery_note.save()

        self.logger.info("adding delivery_note to model")
        treeiter = self.delivery_notes_model.append(
                [delivery_note.code, str(delivery_note.date),
                    delivery_note.vehicle.number, delivery_note.invoiced,
                    "gtk-delete"]
                )
        self.delivery_notes_view.get_selection().select_iter(treeiter)

    def update_delivery_note(self, delivery_note):
        self.logger.debug("update_delivery_note")

        self.logger.info("saving delivery note to database")
        self.logger.debug("delivery_note: %s", delivery_note)

        # FIXME Updating throws an IntegrityError due to UNIQUE constraint
        # on delivery_note.code at updating vehicle foreign key.
        DeliveryNote.update(
                code=delivery_note.code, date=delivery_note.date,
                company=delivery_note.company, vehicle=delivery_note.vehicle,
                invoiced=delivery_note.invoiced
                ).execute()

        self.logger.info("updating delivery_note to model")
        tree_iter = self.get_iter_from_delivery_notes_model(delivery_note.code)
        self.delivery_notes_model.set(
                tree_iter,
                [self.CODE_COLUMN, self.DATE_COLUMN,
                    self.VEHICLE_NUMBER_COLUMN, self.INVOICED_COLUMN],
                [delivery_note.code, delivery_note.date,
                    delivery_note.vehicle.number, delivery_note.invoiced]
                )

    def delete_delivery_note(self, delivery_note):
        self.logger.debug("delete_delivery_note")

        self.logger.info("deleting delivery_note from database")
        DeliveryNote.delete().where(
                DeliveryNote.code == delivery_note.code
                ).execute()

        self.logger.info("removing delivery_note from model")
        tree_iter = self.get_iter_from_delivery_notes_model(delivery_note.code)
        self.delivery_notes_model.remove(tree_iter)

    def validate_delivery_note_item(self, delivery_note_item):
        self.logger.debug("validate_delivery_note_item")

        retvalue = False

        try:
            delivery_note_item.delivery_note = self.selected_delivery_note
            delivery_note_item.item_type = ITEM_TYPES.inv[
                    self.item_type_combo.get_active_text()
                    ]

            delivery_note_item.units = int(self.units_entry.get_text())
            delivery_note_item.price = Decimal(self.price_entry.get_text())
            delivery_note_item.description = self.description_entry.get_text()

            retvalue = True

        except Exception as ex:
            self.logger.error("Exception: %: %", ex.errno, ex.strerror)
            self.logger.error("Invalid data")

        return retvalue

    def create_delivery_note_item(self, delivery_note_item):
        self.logger.debug("create_delivery_note_item")

        self.logger.info("saving delivery note item to database")
        delivery_note_item.save()

        self.logger.info("adding delivery_note_item to model")
        subtotal = delivery_note_item.units * delivery_note_item.price
        treeiter = self.delivery_note_items_model.append(
                [ITEM_TYPES[delivery_note_item.item_type],
                    delivery_note_item.units, str(delivery_note_item.price),
                    str(subtotal), "gtk-delete"]
                )
        self.delivery_note_items_view.get_selection().select_iter(treeiter)

    def update_delivery_note_item(self, delivery_note_item):
        self.logger.debug("update_delivery_note_item")

        self.logger.info("saving delivery note item to database")
        delivery_note_item.save()

        self.logger.info("updating delivery note item to model")
        tree_iter = self.get_iter_from_delivery_note_items_model(
                delivery_note_item.item_type
                )

        subtotal = delivery_note_item.units * delivery_note_item.price
        self.delivery_notes_model.set(
                tree_iter,
                [self.ITEM_TYPE_COLUMN, self.UNITS_COLUMN, self.PRICE_COLUMN,
                    self.SUBTOTAL_COLUMN],
                [ITEM_TYPES[delivery_note_item.item_type],
                    delivery_note_item.units, delivery_note_item.price,
                    subtotal]
                )

    def delete_delivery_note_item(self, delivery_note_item):
        self.logger.debug("delete_delivery_note_item")

        self.logger.info("removing delivery note item from model")
        tree_iter = self.get_iter_from_delivery_note_items_model(
                delivery_note_item.item_type
                )
        self.delivery_notes_model.remove(tree_iter)

        self.logger.info("deleting delivery note item from database")
        delivery_note_item.delete_instance()
