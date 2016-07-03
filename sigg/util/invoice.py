from decimal import Decimal
from datetime import datetime, timedelta

from constants import RESOURCES_DIR
from util import ITEM_TYPES, PAYMENT_TYPES

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


def print_header(c):
    c.drawImage(
            RESOURCES_DIR + "/logo-gruas.png",
            5*mm, 247*mm, width=90*mm, height=45*mm
            )
    c.setFont("Helvetica", 8)
    c.drawString(100*mm, 287*mm, "Base y oficinas:")
    c.drawString(100*mm, 283*mm,
                 "Parque industrial 'El Polígono', C\ Río Arba, 39")
    c.drawString(100*mm, 279*mm,
                 "Teléfono 976 50 55 44 - Fax 976 50 41 87")
    c.drawString(100*mm, 275*mm,
                 "Teléfono móvil 686 96 22 33")
    c.drawString(100*mm, 271*mm,
                 "50410 CUARTE DE HUERVA (Zaragoza)")
    c.drawString(100*mm, 267*mm,
                 "www.gruasyplataformas.com")
    c.setFont("Courier", 9)


def invoice_header(c):
    c.setFont("Courier", 7)
    c.rect(5*mm, 230*mm, 25*mm, 10*mm)
    c.drawString(7*mm, 238*mm, "FACTURA")
    c.rect(30*mm, 230*mm, 25*mm, 10*mm)
    c.drawString(32*mm, 238*mm, "FECHA")
    c.rect(5*mm, 220*mm, 30*mm, 10*mm)
    c.drawString(7*mm, 228*mm, "COD.CLIENTE")
    c.rect(35*mm, 220*mm, 50*mm, 10*mm)
    c.drawString(37*mm, 228*mm, "N.I.F.")
    c.rect(100*mm, 220*mm, 105*mm, 40*mm)
    c.rotate(90)
    c.setFont("Courier", 6)
    legal = "Reg. Merc. de Zaragoza. tomo 1.538, folio 1, hoja nº Z-11.892,"
    legal += " ins. 1.ª, fecha 2-11-93"
    c.drawString(80*mm, -3*mm, legal)
    c.rotate(270)
    c.setFont("Courier", 9)


def delivery_notes(c):
    c.setFillGray(0.85)
    c.rect(5*mm, 210*mm, 22*mm, 6*mm, fill=1)
    c.rect(5*mm, 40*mm, 22*mm, 170*mm)
    c.rect(27*mm, 210*mm, 20*mm, 6*mm, fill=1)
    c.rect(27*mm, 40*mm, 20*mm, 170*mm)
    c.rect(47*mm, 210*mm, 12*mm, 6*mm, fill=1)
    c.rect(47*mm, 40*mm, 12*mm, 170*mm)
    c.rect(59*mm, 210*mm, 80*mm, 6*mm, fill=1)
    c.rect(59*mm, 40*mm, 80*mm, 170*mm)
    c.rect(139*mm, 210*mm, 20*mm, 6*mm, fill=1)
    c.rect(139*mm, 40*mm, 20*mm, 170*mm)
    c.rect(159*mm, 210*mm, 20*mm, 6*mm, fill=1)
    c.rect(159*mm, 40*mm, 20*mm, 170*mm)
    c.rect(179*mm, 210*mm, 28*mm, 6*mm, fill=1)
    c.rect(179*mm, 40*mm, 28*mm, 170*mm)
    c.setFillGray(0)
    c.setFont("Courier-Bold", 9)
    c.drawString(7*mm, 212*mm, "{:^9}".format("FECHA"))
    c.drawString(29*mm, 212*mm, "{:^9}".format("ALBARAN"))
    c.drawString(49*mm, 212*mm, "{:^5}".format("GRUA"))
    c.drawString(61*mm, 212*mm, "{:^40}".format("CONCEPTO"))
    c.drawString(141*mm, 212*mm, "{:^9}".format("UNIDADES"))
    c.drawString(161*mm, 212*mm, "{:^9}".format("PRECIO"))
    c.drawString(181*mm, 212*mm, "{:^13}".format("IMPORTE"))
    c.setFont("Courier", 9)


def footer(c):
    c.setFont("Courier", 7)
    c.rect(5*mm, 28*mm, 40*mm, 10*mm)
    c.drawString(7*mm, 36*mm, "SUMA")
    c.rect(5*mm, 13*mm, 60*mm, 10*mm)
    c.drawString(7*mm, 21*mm, "FORMA DE PAGO")
    c.rect(65*mm, 13*mm, 60*mm, 10*mm)
    c.drawString(67*mm, 21*mm, "VENCIMIENTO")
    c.setFont("Courier", 9)


def total(c, vat):
    vat_str = "I.V.A. (" + str(vat) + "%)"
    c.rect(179*mm, 28*mm, 28*mm, 10*mm)
    c.drawString(150*mm, 31*mm, "BASE")
    c.rect(179*mm, 18*mm, 28*mm, 10*mm)
    c.drawString(150*mm, 21*mm, vat_str)
    c.setFont("Courier-Bold", 9)
    c.drawString(150*mm, 11*mm, "TOTAL")
    c.setFillGray(0.85)
    c.rect(179*mm, 8*mm, 28*mm, 10*mm, fill=1)
    c.setFillGray(0)
    c.setFont("Courier", 9)


def fill_invoice_header_data(c, invoice_number, invoice_date, company):
    c.drawString(7*mm, 232*mm, invoice_number)
    c.drawString(32*mm, 232*mm, invoice_date)
    c.drawString(7*mm, 222*mm, company.code)
    c.drawString(37*mm, 222*mm, company.nif)


def fill_company_data(c, company):
    c.drawString(102*mm, 256*mm, company.name)
    c.drawString(102*mm, 252*mm, company.address)
    c.drawString(102*mm, 248*mm, company.zip_code)
    c.drawString(102*mm, 244*mm, company.city)
    c.drawString(102*mm, 240*mm, company.state)


def fill_delivery_notes(c, company):
    total = Decimal(0)
    subtotal = Decimal(0)
    line = 206

    for delivery_note in company.delivery_notes:
        c.drawString(7*mm, line*mm,
                     "{:^9}".format(delivery_note.date.strftime("%Y-%m-%d")))
        c.drawString(29*mm, line*mm, delivery_note.code)
        c.drawString(49*mm, line*mm,
                     "{:^5}".format(delivery_note.vehicle.number))
        for item in delivery_note.items:
            subtotal = item.units * item.price
            total += subtotal
            units_str = str(item.units) + " " + ITEM_TYPES[item.item_type]
            c.drawString(141*mm, line*mm, "{:>9}".format(units_str))
            c.drawString(161*mm, line*mm, "{:>9.2f}".format(item.price))
            c.drawString(181*mm, line*mm, "{:>13.2f}".format(subtotal))
            desc = item.description
            while len(desc) > 0:
                c.drawString(61*mm, line*mm, desc[:40])
                desc = desc[40:]
                line -= 4
        line -= 4

    return total


def fill_footer(c, base, vat, duedate, company):
    vat_value = base * vat / 100
    total = base + vat_value
    c.drawString(181*mm, 31*mm, "{:>13.2f}".format(base))
    c.drawString(181*mm, 21*mm, "{:>13.2f}".format(vat_value))
    c.setFont("Courier-Bold", 9)
    c.drawString(181*mm, 11*mm, "{:>13.2f}".format(total))
    c.setFont("Courier", 9)
    c.drawString(7*mm, 15*mm, PAYMENT_TYPES[company.payment_type])
    c.drawString(67*mm, 15*mm, str(duedate))


def duedate_calculator(invoice_date, expiration_days, payment_days):
    duedate = invoice_date + timedelta(days=expiration_days)
    for day in payment_days:
        if duedate.day < day:
            delta = day - duedate.day
            duedate = duedate + timedelta(days=delta)
            break

    return duedate


def invoice(company, invoice_number, invoice_date, vat, pdf_filename):
    c = canvas.Canvas(pdf_filename, pagesize=A4)
    c.setFont("Courier", 9)

    print_header(c)
    invoice_header(c)
    delivery_notes(c)
    footer(c)
    total(c, vat)

    fill_invoice_header_data(c, invoice_number, invoice_date, company)
    fill_company_data(c, company)

    total_str = fill_delivery_notes(c, company)
    duedate = duedate_calculator(
            datetime.strptime(invoice_date, '%Y-%m-%d').date(),
            int(company.expiration_days),
            [5, 15, 25]  # FIXME put real payment days
            )

    fill_footer(c, total_str, vat, duedate, company)

    c.showPage()
    c.save()
