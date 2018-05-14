#!/usr/bin/env fades

"""Get data from Socios spreadsheet and send a continuation mail."""

import os
import smtplib
import sys
from email.message import EmailMessage
from contextlib import contextmanager

import infoauth  # fades
import gspread  # fades
from oauth2client.service_account import ServiceAccountCredentials  # fades


SCOPE = ['https://spreadsheets.google.com/feeds']

SUBJECT = "Continuación del trámite de inscripción a la Asociación Civil Python Argentina"

# these are the titles from the "Altas" tab in the Socios spreadsheet, mapped to a name
# will use to handle fields
FIELDS = [
    ('Nombre', 'nombre'),
    ('Apellido', 'apellido'),
    ('Tipo socio', 'tiposocio'),
    ('DNI', 'dni'),
    ('EMail', 'email'),
    ('Nacionalidad', 'nacionalidad'),
    ('Estado Civil', 'ecivil'),
    ('Profesión', 'profesion'),
    ('Fecha Nacimiento', 'fnac'),
    ('Domicilio', 'domicilio'),
    ('Forma de pago', 'formadepago'),
    ('Datos que faltan', 'datosquefaltan'),
]

# the row where the titles are
TITLE_ROW = 8

# mail data
MAIL_HOST = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_TOKENS = infoauth.load(os.path.expanduser("~/.pyarac-presidencia-mail.tokens"))
FROM = "Facundo Batista <{}>".format(MAIL_TOKENS['user'])

MISSING = """\
Para completar los datos legales, necesito por favor que me pases/ajustes también
lo siguiente: {missing_items}
"""

MAIN_TEXT = """\
Hola!

¡Gracias por completar el formulario!

Te pido por favor que valides los datos:

    Nombre(s):         {nombre}
    Apellido(s):       {apellido}
    Tipo socio:        {tiposocio}
    DNI:               {dni}
    Nacionalidad:      {nacionalidad}
    Estado civil:      {ecivil}
    Profesión:         {profesion}
    Fecha nacimiento:  {fnac}
    Domicilio:         {domicilio}

{missing}
Por otro lado, para lo que es el carnet de socia/o que vamos a hacer, necesito que si querés
me pases una foto cuadrada o imagen cuadrada, y un nick o sobrenombre.
{pago}
Gracias, saludos,

--
.   Facundo Batista
.
Presidente Asociación Civil Python Argentina
http://ac.python.org.ar/
"""

PMENT_ACTIVO_AUTO = """
Te dejo el link para que pagues (Socia/o Activa/o débito automático mensual de $200), así
podemos continuar con el trámite:

    http://mpago.la/c0H8
"""

PMENT_ACTIVO_BANK_12m = """
Te dejo los datos para que deposites o transfieras (Socia/o Activa/o por un año, total $2400),
así podemos continuar con el trámite:

    Asociación Civil Python Argentina
    Banco Credicoop
    Cuenta Corriente en pesos
    Nro. 191-153-009748/3
    CBU 19101530-55015300974832
"""

PMENT_ACTIVO_BANK_6m = """
Te dejo los datos para que deposites o transfieras (Socia/o Activa/o por seis meses, total $1200),
así podemos continuar con el trámite:

    Asociación Civil Python Argentina
    Banco Credicoop
    Cuenta Corriente en pesos
    Nro. 191-153-009748/3
    CBU 19101530-55015300974832
"""

PMENT_ACTIVO_CRED_12m = """
Te dejo el link para que pagues (Socia/o Activa/o por un año, total $2400), así
podemos continuar con el trámite:

    https://forms.todopago.com.ar/formulario/commands?command=formulario&fr=1&m=56ff9e1c1ba2317c797eb29b4d7d0a02
"""

PMENT_ACTIVO_CRED_6m = """
Te dejo el link para que pagues (Socia/o Activa/o por seis meses, total $1200), así
podemos continuar con el trámite:

    https://forms.todopago.com.ar/formulario/commands?command=formulario&fr=1&m=7acbfc555b7673c3b753a60d1ee4dfb0
"""

PMENT_ADHERENTE_AUTO = """
Te dejo el link para que pagues (Socia/o Adherente débito automático mensual de $75), así
podemos continuar con el trámite:

    http://mpago.la/4rHr
"""

PMENT_ADHERENTE_BANK_12m = """
Te dejo los datos para que deposites o transfieras (Socia/o Adherente por un año, total $900),
así podemos continuar con el trámite:

    Asociación Civil Python Argentina
    Banco Credicoop
    Cuenta Corriente en pesos
    Nro. 191-153-009748/3
    CBU 19101530-55015300974832
"""

PMENT_ADHERENTE_BANK_6m = """
Te dejo los datos para que deposites o transfieras (Socia/o Adherente por un seis meses,
total $450), así podemos continuar con el trámite:

    Asociación Civil Python Argentina
    Banco Credicoop
    Cuenta Corriente en pesos
    Nro. 191-153-009748/3
    CBU 19101530-55015300974832
"""

PMENT_ADHERENTE_CARD_12m = """
Te dejo el link para que pagues (Socia/o Adherente por un año, total $900), así
podemos continuar con el trámite:

    https://forms.todopago.com.ar/formulario/commands?command=formulario&fr=1&m=d6613446d3790ccfb01fb509bcaf3211
"""

PMENT_ADHERENTE_CARD_6m = """
Te dejo el link para que pagues (Socia/o Adherente por seis meses, total $450), así
podemos continuar con el trámite:

    https://forms.todopago.com.ar/formulario/commands?command=formulario&fr=1&m=cb0003dd9a62b25bed9a82545dda9bd5
"""

PMENT_ESTUDIANTE_CARD_6m = """
Te dejo el link para que pagues (Socia/o Estudiante por seis meses, total $150), así
podemos continuar con el trámite:

    https://forms.todopago.com.ar/formulario/commands?command=formulario&fr=1&m=f64f0d3b5f324abdd3f87a4b2c87952c
"""

COLABORADOR = """
Además, te cuento que para ser socia/o colaborador/a hay que participar en algún proyecto de la
Asociación Civil.

Para poder continuar con el trámite, tenés que darte de alta como colaborador siguiendo los
pasos descriptos acá:

    https://github.com/PyAr/asoc/wiki/Socios-colaboradores

Con esa confirmación ya le metemos para adelante, y luego de un año se hace la evaluación
correspondiente para poder seguir.

Avisame entonces cuando hayas realizado ese procedimiento.
"""

ALL_PAYMENTS = {
    ('Activo', 'Débito automático'):
        PMENT_ACTIVO_AUTO,
    ('Activo', 'Pago Anual (Transferencia Bancaria o depósito)'):
        PMENT_ACTIVO_BANK_12m,
    ('Activo', 'Pago Semestral (Transferencia Bancaria o depósito)'):
        PMENT_ACTIVO_BANK_6m,
    ('Activo', 'Pago Anual (Tarjeta de Crédito, Débito, Pago Fácil, Rapipago, etc)'):
        PMENT_ACTIVO_CRED_12m,
    ('Activo', 'Pago Semestral (Tarjeta de Crédito, Débito, Pago Fácil, Rapipago, etc)'):
        PMENT_ACTIVO_CRED_6m,

    ('Adherente', 'Débito automático'):
        PMENT_ADHERENTE_AUTO,
    ('Adherente', 'Pago Anual (Transferencia Bancaria o depósito)'):
        PMENT_ADHERENTE_BANK_12m,
    ('Adherente', 'Pago Semestral (Transferencia Bancaria o depósito)'):
        PMENT_ADHERENTE_BANK_6m,
    ('Adherente', 'Pago Anual (Tarjeta de Crédito, Débito, Pago Fácil, Rapipago, etc)'):
        PMENT_ADHERENTE_CARD_12m,
    ('Adherente', 'Pago Semestral (Tarjeta de Crédito, Débito, Pago Fácil, Rapipago, etc)'):
        PMENT_ADHERENTE_CARD_6m,

    ('Estudiante', 'Pago Semestral (Tarjeta de Crédito, Débito, Pago Fácil, Rapipago, etc)'):
        PMENT_ESTUDIANTE_CARD_6m,

    ('Colaborador', 'COL'):
        COLABORADOR,
    ('Cadete', 'CAD'):
        "",
}


@contextmanager
def mailer():
    s = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
    s.ehlo()
    s.starttls()
    s.login(MAIL_TOKENS['user'], MAIL_TOKENS['password'])
    yield s
    s.quit()


def send_mails(mails_data):
    """Send the mails."""
    print("Sending mails")
    with mailer() as mlr:
        for recipient, text in mails_data:
            print("    ", recipient)

            # send the mail
            msg = EmailMessage()
            msg.set_content(text)
            msg['From'] = FROM
            msg['To'] = recipient
            msg['Subject'] = SUBJECT
            mlr.send_message(msg)


def get_data_from_spreadsheet(credentials_file, rows):
    """Get user data from Socios spreadsheet."""
    # open the spreadsheet
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, SCOPE)
    gc = gspread.authorize(credentials)
    wks = gc.open("Socios").worksheet('Alta')

    # get the map from spreadsheet titles to colums
    title_values = wks.row_values(TITLE_ROW)
    row_titles = {val: i for i, val in enumerate(title_values)}
    field2col = {}
    for title, field in FIELDS:
        field2col[field] = row_titles[title]

    # build each replace data for each row
    user_data = []
    for row in rows:
        row_values = wks.row_values(row)

        user_data.append(
            {field: row_values[col] for field, col in field2col.items()})

    return user_data


def build_mails(user_data):
    """Build the mails content for the given user data."""
    mails = []
    print("Building texts")
    for data in user_data:
        missingdata = data['datosquefaltan'].strip()
        if missingdata and missingdata != "-":
            missing = MISSING.format(missing_items=missingdata)
        else:
            missing = ""

        payment_key = (data['tiposocio'], data['formadepago'])
        print("    ", payment_key, repr(missingdata))
        pago = ALL_PAYMENTS[payment_key]

        data.update(missing=missing, pago=pago)
        text = MAIN_TEXT.format(**data)

        recipient = "{} {} <{}>".format(data['nombre'], data['apellido'], data['email'])
        mails.append((recipient, text))

    return mails


def main(credentials_file, rows):
    """Main entry point."""
    user_data = get_data_from_spreadsheet(credentials_file, rows)
    print("Retrieved {} record(s) from the spreadsheet".format(len(user_data)))
    mails = build_mails(user_data)
    send_mails(mails)


USAGE = "Usage: send_mails_primeralta.py google_credentials.json row_from [row_to]"

if __name__ == '__main__':
    if len(sys.argv) == 3:
        rows = [int(sys.argv[2])]
    elif len(sys.argv) == 4:
        rows = list(range(int(sys.argv[2]), int(sys.argv[3]) + 1))
    else:
        print(USAGE)
        sys.exit()

    credentials_file = sys.argv[1]
    if not os.path.exists(credentials_file):
        print(USAGE)
        sys.exit()

    sys.exit(main(credentials_file, rows))
