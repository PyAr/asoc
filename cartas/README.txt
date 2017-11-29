La idea es generar el PDF para que los socios impriman y manden por correo postal.

Para ello ejecutar:

    genera_cartas.py credenciales.json N1 [N2 [...]]

El credenciales.json hay que generarlo desde Google (ver [0]).

Los N1, etc, son los números de la planilla de Socios, en la pestaña de Altas, desde donde se va a tomar la info del usuario.

Dependencias:

    - fades

    - inkscape

Enjoy.


[0] Pasos:
    - seguir las instrucciones de http://gspread.readthedocs.io/en/latest/oauth2.html
    - bajarse el json para usarlo con este programa
    - compartir la planila Socios en forma "sólo lectura" al mail que figure en ese json
