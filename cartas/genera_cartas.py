#!/usr/bin/env fades

"""Get data from Socios spreadsheet and build the proper letter."""

import os
import sys
import certg
import gspread  # fades
from oauth2client.service_account import ServiceAccountCredentials  # fades

CREDENTIALS_FILE = os.path.expanduser("~/.asociados-pyar.json")
SCOPE = ['https://spreadsheets.google.com/feeds']


def main(args):
    titles = ['Nro', 'Nombre', 'Apellido', 'Tipo socio', 'DNI', 'EMail', 'Nick', 'Foto',
              'Nacionalidad', 'Estado Civil', 'Profesión', 'Fecha Nacimiento', 'Domicilio']
    asocio_titles ={'Nro':False, 'Nombre':'nombre', 'Apellido':'apellido', 'Tipo socio':'tiposocio', 'DNI':'dni', 'EMail':'email', 'Nick':False, 'Foto':False,
              'Nacionalidad':'nacionalidad', 'Estado Civil':'ecivil', 'Profesión':'profesion', 'Fecha Nacimiento':'fnac', 'Domicilio':'domicilio'}

    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    gc = gspread.authorize(credentials)
    data_dic = {}
    datos =[]
    wks = gc.open("Socios").sheet1
    row_data = wks.row_values(args[1])
    for title, value in zip(titles, row_data):
        if  asocio_titles[title]:
            data_dic[asocio_titles[title]] = value
            print("{}: {}".format(title, value))

    # FIXME: build the letter in PDF
    datos.append(data_dic)

    certg.process('carta.svg','carta','apellido',datos)
if __name__ == '__main__':
    sys.exit(main(sys.argv))

