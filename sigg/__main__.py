import logging
import logging.config

from gi.repository import Gtk
from datetime import date

from constants import DB, RESOURCES_DIR
from models import Vehicle, Company, DeliveryNote, DeliveryNoteItem
from models import Settings
from ui import CompaniesManagerWindow

def init_db():
    DB.connect()
    DB.drop_tables(
            [Company, DeliveryNoteItem, DeliveryNote, Vehicle, Settings],
            safe=True)
    DB.create_tables(
            [Company, DeliveryNoteItem, DeliveryNote, Vehicle, Settings],
            safe=True)

def populate_db():
    v12 = Vehicle(number=12, plate="1234ABC", brand="My brand",
            model="My model", hour_price=27.32, km_price=8.99)
    v15 = Vehicle(number=15, plate="9876ZYX", brand="My brand",
            model="My model", hour_price=34.02, km_price=4.00)
    v12.save()
    v15.save()

    c1 = Company(code="0001", name="Company name", nif="B12345678",
            address="Rue st.", city="Zaragoza", state="Zaragoza",
            zip_code="50000", phone="123456789", contact_person="Foolano",
            alternative_phone="987654321", fax="246813579",
            email="foolano@bar.com", iban="ES12345678901234567890123456789012",
            bank_name="THE Bank", payment_type="CASH", expiration_days=30,
            first_payment_day=5, second_payment_day=15, third_payment_day=25)

    c2 = Company(code="0002", name="Foo Inc.", nif="B45678123",
            address="Major st", city="Zaragoza", state="Zaragoza",
            zip_code="50002", email="foolano@bar.com",
            iban="ES12345678901234567890123456789012", bank_name="Minor Bank",
            payment_type="BANK_TRANSFER", expiration_days=45,
            first_payment_day=8)

    c1.save()
    c2.save()

    dn1 = DeliveryNote(code="11111111", date=date(2016, 1, 3), company=c1,
            vehicle=v12, invoiced=False)
    dn2 = DeliveryNote(code="22222222", date=date(2016, 1, 5), company=c1,
            vehicle=v15, invoiced=False)
    dn1.save()
    dn2.save()

    dni1 = DeliveryNoteItem(delivery_note=dn1, item_type="HOURS", units=12,
            price=v12.hour_price, description="Working hard")
    dni2 = DeliveryNoteItem(delivery_note=dn2, item_type="HOURS", units=7,
            price=21.00, description="We are working hard here")
    dni3 = DeliveryNoteItem(delivery_note=dn2, item_type="OTHERS", units=1,
            price=327.86, description="Are you working hard?")
    dni1.save()
    dni2.save()
    dni3.save()

    Settings(vat=21.00, invoice_number="0000000001").save()

def main():
    logging.config.fileConfig(RESOURCES_DIR + "/logging.ini")
    logging.info("SIGG Started")

    main_window = CompaniesManagerWindow()

    Gtk.main()

if __name__ == '__main__':
    main()
