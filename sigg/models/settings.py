from peewee import *
from constants import DB

class Settings(Model):
    vat = DecimalField(null=False, max_digits=5, decimal_places=2)
    invoice_number = CharField(null=False, max_length=10)

    def __repr__(self):
        return "[ vat: %s, invoice_number: %s ]" % (self.vat,
                self.invoice_number)

    class Meta:
        database = DB
