Los PNGs tienen que estar con el tamaño específico en función de la categoría de socia benefactora. Es en función del área... o sea que ancho por alto, tiene que dar:

- Platino: 25200
- Oro: 12600
- Plata: 6300

Si da menos que ese AREA, conseguir un original más grande.

Si da más que ese AREA, siendo `w` y `h` el tamaño de la imagen actual, el nuevo ancho será `math.sqrt(AREA * w / h)` (y el nuevo alto proporcional).
