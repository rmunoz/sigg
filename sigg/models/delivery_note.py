from peewee import *
from constants import DB
from models import Company, Vehicle

class DeliveryNote(Model):
    code = CharField(index=True, null=False, unique=True, max_length=8)
    date = DateField(null=False)
    company = ForeignKeyField(Company, related_name="delivery_notes")
    vehicle = ForeignKeyField(Vehicle)
    invoiced = BooleanField(null=False, default=False)

    def __repr__(self):
        s = """[ code: {}, date: {}, company: {}, vehicle: {}, invoiced: {}
        ]""".format(self.code, self.date, self.company, self.vehicle,
        self.invoiced)

        return s

    class Meta:
        database = DB
