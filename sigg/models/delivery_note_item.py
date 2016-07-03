from peewee import Model
from peewee import CharField, IntegerField, DecimalField, ForeignKeyField
from constants import DB
from models import DeliveryNote


class DeliveryNoteItem(Model):
    delivery_note = ForeignKeyField(DeliveryNote, related_name="items")
    item_type = CharField(null=False)
    units = IntegerField(null=False)
    price = DecimalField(null=False, max_digits=10, decimal_places=2)
    description = CharField(null=False)

    def __repr__(self):
        s = (
                "[ delivery_note: {}, item_type: {}, units: {}, price: {},"
                "description: {} ]"
                )

        return s.format(
                self.delivery_note, self.item_type, self.units, self.price,
                self.description
                )

    class Meta:
        database = DB
