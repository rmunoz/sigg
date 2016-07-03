from peewee import Model
from peewee import DecimalField, CharField
from constants import DB


class Settings(Model):
    vat = DecimalField(null=False, max_digits=5, decimal_places=2)
    invoice_number = CharField(null=False, max_length=10)

    def __repr__(self):
        s = "[ vat: {}, invoice_number: {}} ]"

        return s.format(self.vat, self.invoice_number)

    class Meta:
        database = DB
