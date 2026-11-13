# -*- coding: utf-8 -*-
"""Del PDF de The Corbeau Way a un texto estructurado y editable.

Trabaja sobre la geometría de cada línea (pdftotext -bbox-layout), no sobre el
texto plano: en este libro la jerarquía está en la posición. El cuerpo empieza
siempre en x=62,5 (y en 74,5 cuando es la primera línea de un párrafo, por la
sangría); los títulos, las leyes, las preguntas y las citas van centrados; las
marcas («C A P Í T U L O», «C I E R R E») van en versalitas espaciadas.

Salida: libro.es.txt, una marca por bloque. El índice y la portada no se
extraen: se rehacen al armar el libro, con los números de página nuevos.
"""
import re
import collections

IZQ = 62.5          # margen izquierdo del cuerpo
SANGRIA = 74.5      # primera línea de párrafo
DER = 397.3         # margen derecho
TOL = 2.0

SALTAR = {1, 2, 4, 5, 6, 8, 11}     # portada, índice y páginas en blanco
MANIFIESTO = {126, 127, 128}
LEYES = {123, 124, 125}      # el listado final: numeral al margen y texto sangrado
SECCIONES = ('Nota de esta edición', 'Prefacio', 'Quiénes somos',
             'Cómo leer este libro', 'Epílogo', 'Las treinta leyes Corbeau',
             'Manifiesto')

s = open('caja.xhtml', encoding='utf-8').read()
paginas = re.findall(r'<page width="[\d.]+" height="[\d.]+">(.*?)</page>', s, re.S)


def lineas_de(html):
    out = []
    for m in re.finditer(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" '
                         r'yMax="([\d.]+)">(.*?)</line>', html, re.S):
        palabras = re.findall(r'>([^<]*)</word>', m.group(5))
        txt = ' '.join(palabras).strip()
        if txt:
            out.append({'x0': float(m.group(1)), 'x1': float(m.group(3)),
                        'y': float(m.group(2)), 't': txt,
                        'alto': float(m.group(4)) - float(m.group(2))})
    return out


def filas(lineas):
    """Una línea del PDF puede venir partida en varias: cuando las letras van
    muy separadas (las marcas en versalitas) o cuando el numeral de una sección
    y su título están al lado. Se juntan por altura, que es lo que no cambia."""
    grupos = []
    for x in sorted(lineas, key=lambda z: z['y']):
        if grupos and x['y'] - grupos[-1][-1]['y'] <= 4.5:
            grupos[-1].append(x)
        else:
            grupos.append([x])
    salida = []
    for g in grupos:
        g = sorted(g, key=lambda z: z['x0'])
        salida.append({'t': '  '.join(z['t'] for z in g),
                       'x0': min(z['x0'] for z in g),
                       'x1': max(z['x1'] for z in g),
                       'y': g[0]['y'], 'piezas': g})
    return salida


def versalita(t):
    """«C A P Í T U L O 1» -> «CAPÍTULO 1»."""
    letras = [c for c in t if c.isalpha() and c not in 'ºª']
    if not letras or not all(c.isupper() for c in letras):
        return None
    if t.count(' ') < len(t) / 3:
        return None
    return re.sub(r'\s+', ' ', re.sub(r'(?<=\S) (?=\S)', '', t)).strip()


bloques = []


def agregar(marca, *partes):
    bloques.append((marca, [x.strip() for x in partes]))


class Juntador:
    """Acumula líneas sueltas y las entrega como un bloque."""
    def __init__(self):
        self.marca = None
        self.partes = []

    def abrir(self, marca):
        self.cerrar()
        self.marca = marca

    def linea(self, t):
        self.partes.append(t)

    def cerrar(self):
        if self.marca and self.partes:
            agregar(self.marca, ' '.join(self.partes))
        self.marca, self.partes = None, []


j = Juntador()
esperando = None
seccion_num = None

for n, html in enumerate(paginas, start=1):
    if n in SALTAR:
        continue
    # el número de página se reconoce por dónde está, no por ser un número:
    # el número de capítulo también es un número suelto
    L = filas([x for x in lineas_de(html)
               if not (re.fullmatch(r'\d{1,3}', x['t']) and x['y'] > 600)])
    if n in MANIFIESTO:
        j.cerrar()
        anterior_y = None
        for x in L:
            if versalita(x['t']):
                j.cerrar(); continue
            if x['t'] == 'Manifiesto':
                j.cerrar(); agregar('TITULO_MANIFIESTO', x['t']); continue
            if anterior_y is not None and x['y'] - anterior_y > 22:
                j.cerrar()
            if j.marca != 'MANIFIESTO':
                j.abrir('MANIFIESTO')
            j.linea(x['t'])
            anterior_y = x['y']
        j.cerrar()
        continue

    if n in LEYES:
        for x in L:
            t, x0 = x['t'], x['x0']
            if t in SECCIONES:
                j.cerrar(); agregar('TITULO_SECCION', t); continue
            m = re.fullmatch(r'(\d\d)\s+(.+)', t)
            if m and abs(x0 - IZQ) < TOL:
                j.cerrar(); j.abrir('LEYN_' + m.group(1)); j.linea(m.group(2)); continue
            if x0 > IZQ + 10 and (j.marca or '').startswith('LEYN_'):
                j.linea(t); continue          # sigue la misma ley
            if j.marca != 'P':
                j.cerrar(); j.abrir('P')
            j.linea(t)
        continue

    for i, x in enumerate(L):
        t, x0, x1 = x['t'], x['x0'], x['x1']
        v = versalita(t)
        if v:
            j.cerrar()
            plano = re.sub(r'\s+', '', v)
            m = re.fullmatch(r'CAPÍTULO(\d+)', plano)
            if m:
                agregar('CAPITULO_N', m.group(1)); esperando = 'TITULO_SECCION'; continue
            m = re.fullmatch(r'LEYCORBEAUN\.º(\d+)', plano)
            if m:
                agregar('LEY_N', m.group(1)); esperando = 'LEY'; continue
            if plano == 'LAPREGUNTAQUERESPONDE':
                esperando = 'PREGUNTA'; continue
            if plano == 'CIERRE':
                agregar('CIERRE'); esperando = None; continue
            m = re.fullmatch(r'BLOQUE([IV]+)', plano)
            if m:
                agregar('BLOQUE_N', m.group(1)); esperando = 'TITULO_SECCION'; continue
            if plano == 'THECORBEAUWAY':
                continue
            agregar('MARCA', v); continue

        if t in SECCIONES:
            j.cerrar(); agregar('TITULO_SECCION', t); esperando = None; continue
        # volanta: una línea corta en mayúsculas, sin espaciar
        if t.isupper() and len(t) < 60 and abs(x0 - IZQ) < TOL and len(t.split()) <= 6:
            j.cerrar(); agregar('VOLANTA', t); continue
        # numeral de sección y su título, en la misma fila: «II.  El precio…»
        m = re.fullmatch(r'([IVX]+)\.\s+(.+)', t)
        if m and abs(x0 - IZQ) < TOL and len(x['piezas']) > 1:
            j.cerrar(); agregar('SECCION', m.group(1) + '.', m.group(2))
            esperando = 'SECCION_SIGUE'; continue
        # un título de sección puede ocupar dos líneas: la segunda va sangrada
        # y con el cuerpo de letra del título, no el del texto
        if esperando == 'SECCION_SIGUE':
            esperando = None
            # la segunda línea del título vuelve al margen, pero conserva el
            # cuerpo de letra del título: eso es lo que la distingue
            if x['piezas'][0].get('alto', 0) > 14.3:
                marca_ant, partes_ant = bloques[-1]
                bloques[-1] = (marca_ant, [partes_ant[0], partes_ant[1] + ' ' + t])
                continue
        # el listado final de leyes: «01  Una empresa es…»
        m = re.fullmatch(r'(\d\d)\s+(.+)', t)
        if m and abs(x0 - IZQ) < TOL and int(m.group(1)) <= 30:
            j.cerrar(); j.abrir('LEYN_' + m.group(1)); j.linea(m.group(2)); continue
        if t.startswith('—'):
            j.cerrar(); j.abrir('LISTA'); j.linea(t.lstrip('— ').strip()); continue

        centrada = x0 > IZQ + TOL and abs((x0 - IZQ) - (DER - x1)) < 14
        if esperando == 'TITULO_SECCION' and j.partes and x['piezas'][0].get('alto', 99) < 18:
            j.cerrar(); esperando = None       # lo que sigue es el subtítulo
        if esperando in ('TITULO_SECCION', 'LEY', 'PREGUNTA'):
            if x0 > IZQ + TOL:     # sigue centrado: es parte del mismo bloque
                if j.marca != esperando:
                    j.abrir(esperando)
                j.linea(t)
                continue
            j.cerrar(); esperando = None   # volvió el cuerpo
        if centrada and x0 > 90:
            if j.marca != 'CITA':
                j.abrir('CITA')
            j.linea(t); continue
        # cuerpo
        if abs(x0 - SANGRIA) < TOL or (j.marca or '').startswith(('CITA', 'LISTA', 'LEYN', 'MANIFIESTO')):
            j.abrir('P')
        elif j.marca != 'P':
            j.abrir('P')
        j.linea(t)
    # al terminar la página, lo que esperaba una línea centrada ya llegó
    if esperando in ('TITULO_SECCION', 'LEY', 'PREGUNTA') and j.partes:
        j.cerrar(); esperando = None

j.cerrar()

with open('libro.es.txt', 'w', encoding='utf-8') as f:
    for marca, partes in bloques:
        f.write(marca + ' | ' + ' | '.join(partes) + '\n')

c = collections.Counter(re.sub(r'_\d+$', '_N', m) for m, _ in bloques)
print(dict(c)); print('bloques:', len(bloques))
