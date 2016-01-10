from peewee import *
from constants import DB

class Company(Model):
    code = CharField(index=True, null=False, unique=True, max_length=4)
    name = CharField(null=False)
    nif = CharField(null=False, unique=True, max_length=9)
    address = CharField(null=False)
    city = CharField(null=False)
    state = CharField(null=False)
    zip_code = CharField(null=False)
    phone = CharField(null=True)
    contact_person = CharField(null=True)
    alternative_phone = CharField(null=True)
    fax = CharField(null=True)
    email = CharField(null=True)
    iban = CharField(null=True, max_length=34)
    bank_name = CharField(null=True)
    payment_type = CharField(null=False)
    expiration_days = IntegerField(null=True)
    first_payment_day = IntegerField(null=True)
    second_payment_day = IntegerField(null=True)
    third_payment_day = IntegerField(null=True)

    def __repr__(self):
        s = ("[ code: {}, name: {}, nif: {}, address: {}, city: {}, state: {},"
                "zip_code: {}, phone: {}, contact_person: {}, "
                "alternative_phone: {}, fax: {}, email: {}, iban: {}, "
                "bank_name: {}, payment_type: {}, expiration_days: {}, "
                "first_payment_day: {}, second_payment_day: {}, "
                "third_payment_day: {} ]")

        return s.format(self.code, self.name, self.nif,
                self.address, self.city, self.state, self.zip_code,
                self.phone, self.contact_person, self.alternative_phone,
                self.fax, self.email, self.iban, self.bank_name,
                self.payment_type, self.expiration_days,
                self.first_payment_day, self.second_payment_day,
                self.third_payment_day)

    class Meta:
        database = DB
