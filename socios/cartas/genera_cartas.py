#!/usr/bin/env fades

"""Get data from Socios spreadsheet and build the proper letter."""

import os
import sys

import certg  # fades

import gspread  # fades
from oauth2client.service_account import ServiceAccountCredentials  # fades

SCOPE = ['https://spreadsheets.google.com/feeds']

# these are the titles from the "Altas" tab in the Socios spreadsheet, mapped to the
# corresponding field in the SVG
SVG_FIELDS = [
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
]

# the row where the titles are
TITLE_ROW = 8

# the title for "all data is ok"
DATA_OK_TITLE = "Datos OK"


def main(credentials_file, rows):
    """Main entry point."""
    # open the spreadsheet
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, SCOPE)
    gc = gspread.authorize(credentials)
    wks = gc.open("Socios").worksheet('Alta')

    # get the map from spreadsheet titles to colums
    title_values = wks.row_values(TITLE_ROW)
    row_titles = {val: i for i, val in enumerate(title_values)}
    svgfield2col = {}
    for title, svgfield in SVG_FIELDS:
        svgfield2col[svgfield] = row_titles[title]
    data_ok_column = row_titles[DATA_OK_TITLE]

    # build each replace data for each row
    replace_data = []
    for row in rows:
        row_values = wks.row_values(row)

        # check all data is complete
        if row_values[data_ok_column] != "✓":
            raise ValueError(
                "Data is not OK for row {} ({!r})".format(row, row_values[data_ok_column]))

        d = {field: row_values[col] for field, col in svgfield2col.items()}
        replace_data.append(d)

    # generate the certificates
    certg.process('carta.svg', 'carta', 'apellido', replace_data)


USAGE = "Usage: genera_cartas.py credentials.json row1 [row2 [...]]"

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(USAGE)
        sys.exit()

    credentials_file = sys.argv[1]
    if not os.path.exists(credentials_file):
        print(USAGE)
        sys.exit()

    try:
        rows = map(int, sys.argv[2:])
    except ValueError:
        print(USAGE)
        sys.exit()

    sys.exit(main(credentials_file, rows))
