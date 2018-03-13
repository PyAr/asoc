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
    ('Nro', 'nrosocix'),
    ('Nombre', 'nombre'),
    ('Apellido', 'apellido'),
    ('Tipo socio', 'tiposocix'),
    ('EMail', 'email'),
]

# the row where the titles are
TITLE_ROW = 1

# mail data
MAIL_HOST = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_TOKENS = infoauth.load(os.path.expanduser("~/.pyarac-presidencia-mail.tokens"))
FROM = "Facundo Batista <{}>".format(MAIL_TOKENS['user'])

MAIN_TEXT = """\
Hola {nombre}!

En este sencillo pero emotivo acto (?) te cuento que en la última reunión de Comisión Directiva
se aprobó y confirmó tu asociación.

Sos socia/o número {nrosocix}, tipo {tiposocix}.

En algún momento de las próximas semanas nos encargaremos del carnet (estamos a full con mil cosas
del arranque de la Asociación, todavía).

Cualquier duda o comentario, a tu servicio.

Gracias, saludos,

--
.   Facundo Batista
.
Presidente Asociación Civil Python Argentina
http://ac.python.org.ar/
"""


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
    wks = gc.open("Socios").worksheet('Humanos')

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


USAGE = "Usage: send_mails_yasocios.py google_credentials.json row_from [row_to]"

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
