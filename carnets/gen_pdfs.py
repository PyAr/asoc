#!/usr/bin/env fades

"""Generate the carnets.

pyqrcode also needs:

fades:
    pypng
"""

import csv
import os
import tempfile

import certg  # fades file:///home/facundo/devel/reps/certg
import pyqrcode  # fades


DEFAULT_FACE = "logo-python-cuadradito.png"


def generate_qr(last_name, first_name, mail):
    qr = pyqrcode.create("{} {} <{}>".format(first_name, last_name, mail))
    _, tmpfile = tempfile.mkstemp(suffix='.png')
    qr.png(tmpfile, scale=3, background=(0xf7, 0xe6, 0xdc, 0xff), quiet_zone=3)
    return tmpfile


replace_info = []
image_info = [{
    'placement_rectangle_id': 'rect1016',
    'path_variable': 'face_path',
}, {
    'placement_rectangle_id': 'rect1023',
    'path_variable': 'qr_path',
}]

with open("dump-carnets.csv", "rt", encoding="utf8") as fh:
    reader = csv.DictReader(fh)
    for item in reader:
        qr_path = generate_qr(item['last_name'], item['first_name'], item['email'])
        face_path = item['picture']
        if face_path in ("", "False"):  # missing picture, or specifically asked to not have one
            face_path = DEFAULT_FACE
        replace_info.append({
            'nsoc': "{:04d}".format(int(item['legal_id'])),
            'apellido': item['last_name'],
            'nombre': item['first_name'],
            'nick': item['nick'],
            'face_path': os.path.abspath(face_path),
            'qr_path': os.path.abspath(qr_path),
        })


def cback(data):
    print("Avance:", data['nsoc'])


certg.process("carnet-adelante.svg", "socio", "nsoc", replace_info, image_info, progress_cb=cback)
