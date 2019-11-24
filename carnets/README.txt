Pasos:
- ir a una instancia de asoc_members y correr `./manage.py dump_carnets_info`
- traerse el `dump-carnets.csv` que deja eso
- ejecutar `download_pictures.py`
- ejecutar `check_pictures.py` tantas veces como sea necesario para que todo esté "verde"
- ejecutar `gen_pdfs.py`

Si se quiere revisar las salidas, lo más sencillo es juntar todos los resultados en uno::
    pdftk socio-*.pdf cat output newfile.pdf
