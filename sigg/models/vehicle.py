from peewee import *
from constants import DB

class Vehicle(Model):
    number = IntegerField(index=True, null=False, unique=True)
    plate = CharField(null=False)
    brand = CharField(null=True)
    model = CharField(null=True)
    hour_price = DecimalField(null=False, max_digits=10, decimal_places=2)
    km_price = DecimalField(null=False, max_digits=10, decimal_places=2)

    def __repr__(self):
        s = ("[ number: {}, plate: {}, brand: {}, model: {}, hour_price: {}, "
            "km_price: {} ]")

        return s.format(self.number, self.plate, self.brand, self.model,
                self.hour_price, self.km_price)

    class Meta:
        database = DB
