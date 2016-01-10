import logging

from decimal import *

from gi.repository import Gtk

from constants import RESOURCES_DIR
from models import Vehicle

class VehiclesManagerWindow:

    NUMBER_COLUMN = 0
    PLATE_COLUMN = 1
    BRAND_COLUMN = 2
    MODEL_COLUMN = 3
    REMOVE_COLUMN = 4

    def __init__(self, logger=None, parent=None):
        self.logger = logger or logging.getLogger(__name__)

        self.load_data_from_database()
        self.build_ui()

        self.window.set_modal(True)
        self.window.set_transient_for(parent)

        self.window.show_all()

    def load_data_from_database(self):
        self.logger.debug("Loading data from db...")
        self.vehicles = Vehicle.select()
        self.logger.debug("%s vehicles loaded", len(self.vehicles))

    def build_ui(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(RESOURCES_DIR + "/vehicles_window.glade")

        self.builder.connect_signals(self)

        self.window = self.builder.get_object("vehicles_window")
        self.number_entry = self.builder.get_object("number_entry")
        self.plate_entry = self.builder.get_object("plate_entry")
        self.brand_entry = self.builder.get_object("brand_entry")
        self.model_entry = self.builder.get_object("model_entry")
        self.hour_price_entry = self.builder.get_object("hour_price_entry")
        self.km_price_entry = self.builder.get_object("km_price_entry")

        self.vehicles_view = self.builder.get_object("vehicles_view")
        self.vehicles_model = self.builder.get_object("vehicles_model")
        self.populate_treeview_model()

    def populate_treeview_model(self):
        for vehicle in self.vehicles:
            self.vehicles_model.append([str(vehicle.number), vehicle.plate,
                vehicle.brand, vehicle.model, "gtk-delete"])

    def populate_form(self, vehicle):
        self.logger.debug("populate_form")
        self.number_entry.set_text(str(vehicle.number))
        self.plate_entry.set_text(vehicle.plate)
        self.brand_entry.set_text(vehicle.brand)
        self.model_entry.set_text(vehicle.model)
        self.hour_price_entry.set_text(str(vehicle.hour_price))
        self.km_price_entry.set_text(str(vehicle.km_price))
        self.number_entry.editable = False

    def clean_form(self):
        self.logger.debug("clean_form")
        self.number_entry.set_text("")
        self.plate_entry.set_text("")
        self.brand_entry.set_text("")
        self.model_entry.set_text("")
        self.hour_price_entry.set_text("")
        self.km_price_entry.set_text("")
        self.number_entry.editable = True
        self.vehicles_view.get_selection().unselect_all()

    def on_delete_window(self, *args):
        self.window.hide()

    def on_quit_button_clicked(self, button):
        self.window.hide()

    def on_clean_button_clicked(self, button):
        self.logger.debug("on_clean_button_clicked")
        self.clean_form()

    def on_save_button_clicked(self, button):
        self.logger.debug("on_save_button_clicked")

        vehicle = self.validate_vehicle()

        if vehicle == None:
            dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CANCEL, "Invalid values")

            dialog.run()
            dialog.destroy()
        else:
            self.logger.debug("Trying to find vehicle: %s", vehicle.number)

            query = Vehicle.select().where(Vehicle.number == vehicle.number)
            if query.exists():
                dialog = Gtk.MessageDialog(
                        self.window, 0, Gtk.MessageType.QUESTION,
                        Gtk.ButtonsType.YES_NO,
                        "The vehicle already exists, do you want to update it?")

                if dialog.run() == Gtk.ResponseType.YES:
                    self.update_vehicle(vehicle)

                dialog.destroy()
            else:
                self.create_vehicle(vehicle)

            self.clean_form()

    def on_row_activated(self, treeview, path, column):
        self.logger.debug("on_row_activated")

        tree_iter = self.vehicles_model.get_iter(path)
        number = self.vehicles_model.get_value(tree_iter, self.NUMBER_COLUMN)
        vehicle = Vehicle.select().where(Vehicle.number == number).get()

        if column.get_sort_column_id() == self.REMOVE_COLUMN:
            dialog = Gtk.MessageDialog(
                    self.window, 0, Gtk.MessageType.QUESTION,
                    Gtk.ButtonsType.YES_NO,
                    "Are you sure to remove the vehicle?")

            if dialog.run() == Gtk.ResponseType.YES:
                self.delete_vehicle(vehicle)

            dialog.destroy()
        else:
            self.populate_form(vehicle)

    def get_iter_from_selected_row(self, number):
        self.logger.debug("get_iter_from_selected_row")

        for row in self.vehicles_model:
            row_number = row.model.get_value(row.iter, self.NUMBER_COLUMN)
            self.logger.debug("Row number: %s", row_number)
            if row_number == str(number):
                return row.iter

        self.logger.error("Cannot find element")
        raise RuntimeError("Cannot find element: % in model", number)

    def validate_vehicle(self):
        self.logger.debug("validate_vehicle")

        vehicle = None
        try:
            number = int(self.number_entry.get_text())
            plate = self.plate_entry.get_text()
            brand = self.brand_entry.get_text()
            model = self.model_entry.get_text()
            hour_price = Decimal(self.hour_price_entry.get_text())
            km_price = Decimal(self.km_price_entry.get_text())

            if(len(plate) != 7):
                raise ValueError

            vehicle = Vehicle(number = number, plate = plate, brand = brand,
                    model = model, hour_price = hour_price, km_price = km_price)
        except:
            self.logger.error("Invalid data")

        return vehicle

    def create_vehicle(self, vehicle):
        self.logger.debug("create_vehicle")

        self.logger.info("saving vehicle to database")
        vehicle.save()

        self.logger.info("adding vehicle to model")
        self.vehicles_model.append([str(vehicle.number), vehicle.plate,
            vehicle.brand, vehicle.model, "gtk-delete"])

    def update_vehicle(self, vehicle):
        self.logger.debug("update_vehicle")

        self.logger.info("saving vehicle to database")
        self.logger.debug("vehicle: %s", vehicle)
        Vehicle.update(plate = vehicle.plate, brand = vehicle.brand,
                model = vehicle.model, hour_price = vehicle.hour_price,
                km_price = vehicle.km_price).where(Vehicle.number ==
                        vehicle.number).execute()

        self.logger.info("updating vehicle to model")
        tree_iter = self.get_iter_from_selected_row(vehicle.number)
        self.vehicles_model.set(tree_iter,
                [self.PLATE_COLUMN, self.BRAND_COLUMN, self.MODEL_COLUMN],
                [vehicle.plate, vehicle.brand, vehicle.model])

    def delete_vehicle(self, vehicle):
        self.logger.debug("delete_vehicle")

        self.logger.info("deleting vehicle from database")
        Vehicle.delete().where(Vehicle.number == vehicle.number).execute()

        self.logger.info("removing vehicle from model")
        tree_iter = self.get_iter_from_selected_row(vehicle.number)
        self.vehicles_model.remove(tree_iter)
