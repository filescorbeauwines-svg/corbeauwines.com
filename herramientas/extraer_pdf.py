# -*- coding: utf-8 -*-
"""Del PDF de una nota a fuente/analisis/<slug>.<idioma>.md

    python3 herramientas/extraer_pdf.py nota.pdf clave slug-es slug-en [fecha] [orden]

Las notas llegan del cliente en PDF o en .docx. Para .docx está extraer.py;
este script es para los PDF, y trabaja sobre la geometría de cada línea
(pdftotext -bbox-layout), no sobre el texto plano: en estos documentos la
jerarquía está en la posición y en el cuerpo de letra, no en marcas.

Cada PDF trae la nota en los dos idiomas, una abajo de la otra, encabezadas
por «CORBEAU JOURNAL · TEMA».

Lo que sale es un borrador: conviene leer los subtítulos, que vienen en
mayúsculas y acá pasan a minúsculas, y revisar las tablas.
"""
import collections
import html as _html
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import articulos as A
from extraer import PROPIOS, minuscula


def unir(palabras):
    """Las letras de un título en versalitas llegan como palabras sueltas, y
    cada palabra del título llega como una línea aparte. Si todo lo que hay en
    la línea son letras sueltas, se pegan: es una palabra."""
    piezas = [_html.unescape(p[2]) for p in palabras]
    letreado = (len(piezas) > 2 and
                sum(len(x) for x in piezas) / len(piezas) < 2.2)
    if len(piezas) > 1 and (letreado or all(len(x) == 1 for x in piezas)):
        # letras sueltas: el hueco entre palabras es mayor que el de entre letras
        huecos = [palabras[i + 1][0] - palabras[i][1] for i in range(len(palabras) - 1)]
        orden = sorted(huecos)
        letra, mayor = orden[len(orden) // 2], orden[-1]
        if mayor < letra * 1.6:
            return ''.join(piezas).strip()
        corte = (letra + mayor) / 2
        salida = [piezas[0]]
        for h, pieza in zip(huecos, piezas[1:]):
            salida.append(' ' if h > corte else '')
            salida.append(pieza)
        return ''.join(salida).strip()
    return ' '.join(piezas).strip()


def filas(pdf):
    xml = subprocess.check_output(['pdftotext', '-bbox-layout', pdf, '-']).decode()
    paginas = []
    for pag in re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', xml, re.S):
        alto_pag = float(pag[1])
        L = []
        for m in re.finditer(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" '
                             r'yMax="([\d.]+)">(.*?)</line>', pag[2], re.S):
            palabras = [(float(a), float(b), c) for a, b, c in re.findall(
                r'<word xMin="([\d.]+)" yMin="[\d.]+" xMax="([\d.]+)" yMax="[\d.]+">([^<]*)</word>',
                m.group(5))]
            t = unir(palabras)
            if not t:
                continue
            L.append({'x0': float(m.group(1)), 'x1': float(m.group(3)),
                      'y': float(m.group(2)), 't': t, 'palabras': palabras,
                      'alto': float(m.group(4)) - float(m.group(2))})
        # el pie de página («CORBEAU JOURNAL  4») no es contenido
        L = [x for x in L if x['y'] < alto_pag - 70]
        paginas.append(agrupar(sorted(L, key=lambda z: z['y'])))
    return paginas


def agrupar(lineas):
    """Las líneas que comparten altura son una sola: pdftotext parte una línea
    en varias cuando las letras van muy separadas o cuando hay columnas."""
    grupos = []
    for x in lineas:
        if grupos and x['y'] - grupos[-1][-1]['y'] <= 4.5:
            grupos[-1].append(x)
        else:
            grupos.append([x])
    salida = []
    for g in grupos:
        g = sorted(g, key=lambda z: z['x0'])
        salida.append({'piezas': g, 'y': g[0]['y'],
                       'x0': min(z['x0'] for z in g), 'x1': max(z['x1'] for z in g),
                       'alto': max(z['alto'] for z in g),
                       't': ' '.join(z['t'] for z in g)})
    return salida


def espaciada(t):
    letras = [c for c in t if c.isalpha() and c not in 'ºª']
    if not letras or not all(c.isupper() for c in letras):
        return None
    if t.count(' ') < len(t) / 3:
        return None
    return re.sub(r'\s+', ' ', re.sub(r'(?<=\S) (?=\S)', '', t)).strip()


def alinear(cols, modelo):
    """Cada pieza va a la columna de la cabecera que le queda más cerca."""
    salida = [''] * len(modelo)
    for texto, x in cols:
        i = min(range(len(modelo)), key=lambda k: abs(modelo[k] - x))
        salida[i] = (salida[i] + ' ' + texto).strip()
    return [(t, modelo[i]) for i, t in enumerate(salida)]


def columnas(fila, cuerpo_x):
    """Una fila de tabla: varias piezas separadas por huecos grandes."""
    if len(fila['piezas']) < 2:
        return None
    cols, actual = [], [fila['piezas'][0]]
    for p in fila['piezas'][1:]:
        if p['x0'] - actual[-1]['x1'] > 14:
            cols.append(actual); actual = [p]
        else:
            actual.append(p)
    cols.append(actual)
    if len(cols) < 2:
        return None
    return [(' '.join(z['t'] for z in c), c[0]['x0']) for c in cols]


def medidas(paginas):
    """El cuerpo del texto es lo que más se repite: su margen, su cuerpo de
    letra y su interlínea. Cada documento del cliente viene con los suyos."""
    c = collections.Counter()
    for p in paginas:
        for f in p:
            c[(round(f['x0'], 0), round(f['alto'], 1))] += 1
    (x, alto), _ = c.most_common(1)[0]
    huecos = collections.Counter()
    for p in paginas:
        for antes, ahora in zip(p, p[1:]):
            if abs(antes['alto'] - alto) < 0.3 and abs(ahora['alto'] - alto) < 0.3:
                huecos[round(ahora['y'] - antes['y'], 1)] += 1
    interlinea = huecos.most_common(1)[0][0] if huecos else alto + 2
    return x, alto, interlinea


def convertir(filas_idioma, cuerpo_x, cuerpo_alto, interlinea):
    bloques = []
    parrafo, tabla, lista, hueco_previo = [], [], None, None
    ultimo_y = None

    def cerrar():
        nonlocal parrafo, tabla, lista
        if parrafo:
            bloques.append(('P', ' '.join(parrafo))); parrafo = []
        if lista:
            bloques.append(('LISTA', lista)); lista = None
        if tabla:
            bloques.append(('TABLA', tabla)); tabla = []

    for f in filas_idioma:
        t, x0, alto = f['t'], f['x0'], f['alto']
        hueco = None if ultimo_y is None else f['y'] - ultimo_y
        ultimo_y = f['y']
        piezas = f['piezas']
        rotulo = [z for z in piezas
                  if re.fullmatch(r'(FUENTE|SOURCE)', re.sub(r'\s+', '', z['t']).upper())]
        if rotulo:
            cerrar()
            texto = ' '.join(z['t'] for z in piezas if z not in rotulo).strip()
            if texto:
                bloques.append(('FUENTE', texto))
            continue
        # la flecha de los ítems de lista viene pegada a su primera línea
        if piezas and piezas[0]['t'].strip() in ('→', '—', '·') and len(piezas) > 1:
            cerrar()
            lista = ' '.join(z['t'] for z in piezas[1:]).strip()
            continue
        if t.strip() in ('→', '—', '·'):
            continue
        v = espaciada(t)
        if v and len(piezas) > 1:
            trozos = [espaciada(z['t']) or z['t'] for z in piezas]
            v = ' '.join(x for x in trozos if x)
        es_titulin = (v or (t.isupper() and len(t) < 90)) and alto <= cuerpo_alto + 1
        if es_titulin:
            cerrar()
            texto = v or t
            if re.sub(r'[^A-ZÁÉÍÓÚÑ]', '', texto.upper()) in ('DESDEELORIGEN', 'FROMTHEORIGIN'):
                bloques.append(('ORIGEN_MARCA', texto)); continue
            if bloques and bloques[-1][0] == 'SUB' and hueco is not None and hueco < 12:
                bloques[-1] = ('SUB', bloques[-1][1] + ' ' + texto)   # título de dos líneas
            else:
                bloques.append(('SUB', texto))
            continue
        cols = columnas(f, cuerpo_x)
        # una celda que sigue en la línea de abajo deja una fila de una sola
        # columna: pertenece a la tabla abierta, no es un párrafo
        if tabla and not cols and x0 > cuerpo_x + 2 and alto <= cuerpo_alto + 1:
            cols = [(t, x0)]
        if cols and (len(cols) >= 2 or tabla) and alto <= cuerpo_alto + 1:
            if parrafo:
                bloques.append(('P', ' '.join(parrafo))); parrafo = []
            # una celda puede ocupar varias líneas: si la fila nueva no empieza
            # una columna conocida, continúa la anterior
            if tabla and hueco is not None and hueco < 14:
                for texto, x in cols:
                    for i, (prev, px) in enumerate(tabla[-1]):
                        if abs(px - x) < 6:
                            tabla[-1][i] = (prev + ' ' + texto, px)
                            break
                    else:
                        tabla[-1].append((texto, x))
            else:
                if tabla:
                    cols = alinear(cols, [x for _, x in tabla[0]])
                tabla.append(list(cols))
            continue
        if tabla:
            bloques.append(('TABLA', tabla)); tabla = []
        if alto > cuerpo_alto + 1:
            marca = 'DESTACADO' if x0 > cuerpo_x + 6 else 'BAJADA'
            if bloques and bloques[-1][0] == marca and hueco is not None and hueco < 20:
                bloques[-1] = (marca, bloques[-1][1] + ' ' + t)   # sigue el mismo
            else:
                cerrar(); bloques.append((marca, t))
            continue
        if alto < cuerpo_alto - 1.5 and x0 > cuerpo_x + 30:
            cerrar()
            bloques.append(('FUENTE', t)); continue
        if x0 > cuerpo_x + 30 and alto <= cuerpo_alto + 1:
            # línea centrada: una fórmula o un epígrafe
            cerrar(); bloques.append(('CENTRADA', t)); continue
        if x0 > cuerpo_x + 6:
            # ítem de lista: empieza sangrado y sigue en líneas más sangradas
            if lista is not None and hueco is not None and hueco < interlinea * 1.25:
                lista += ' ' + t
            else:
                cerrar(); lista = t
            continue
        if lista:
            bloques.append(('LISTA', lista)); lista = None
        if parrafo and hueco is not None and hueco > interlinea * 1.25:
            bloques.append(('P', ' '.join(parrafo))); parrafo = []
        parrafo.append(t)
    cerrar()
    return bloques


def a_markdown(bloques, idioma):
    salida, lista, origen = [], [], [False]
    def cerrar_lista():
        if lista:
            salida.append('\n'.join('- ' + x for x in lista)); lista.clear()
    for marca, dato in bloques:
        if marca != 'LISTA':
            cerrar_lista()
        if marca == 'ORIGEN_MARCA':
            origen[0] = True
        elif marca == 'SUB':
            salida.append('## ' + minuscula(dato))
        elif marca == 'DESTACADO':
            salida.append('> ' + dato)
        elif marca == 'FUENTE':
            salida.append('FUENTE ' + dato)
        elif marca == 'CENTRADA':
            salida.append('**%s**' % dato)
        elif marca == 'LISTA':
            lista.append(dato)
        elif marca == 'TABLA':
            salida.append(tabla_md(dato))
        elif origen[0]:
            salida.append('ORIGEN ' + dato); origen[0] = False
        else:
            salida.append(dato)
    cerrar_lista()
    return '\n\n'.join(salida)


def tabla_md(filas_tabla):
    n = max(len(f) for f in filas_tabla)
    def fila(f):
        celdas = [c for c, _ in f] + [''] * (n - len(f))
        return '| ' + ' | '.join(re.sub(r'\s+', ' ', c).strip() for c in celdas) + ' |'
    L = [fila(filas_tabla[0]), '| ' + ' | '.join(['---'] * n) + ' |']
    L += [fila(f) for f in filas_tabla[1:]]
    return '\n'.join(L)


def partir(paginas):
    """Las dos versiones, separadas por el rótulo «CORBEAU JOURNAL · TEMA»."""
    todas = [f for p in paginas for f in p]
    cortes = []
    for i, f in enumerate(todas):
        plano = re.sub(r'\s+', '', f['t']).upper()
        if plano.startswith('CORBEAUJOURNAL·') or re.fullmatch(r'CORBEAUJOURNAL·\w+', plano):
            cortes.append(i)
    if len(cortes) < 2:
        raise SystemExit('No encontré las dos secciones de idioma: %s' % cortes)
    def tema(i):
        return re.sub(r'\s+', ' ', re.sub(r'(?<=\S) (?=\S)', '',
                      todas[i]['t'])).split('·')[-1].strip()
    return ((todas[cortes[0] + 1:cortes[1]], tema(cortes[0])),
            (todas[cortes[1] + 1:], tema(cortes[1])))


def extraer(pdf, clave, slugs, fecha, orden):
    paginas = filas(pdf)
    cuerpo_x, cuerpo_alto, interlinea = medidas(paginas)
    secciones = partir(paginas)
    for idioma, (seccion, volanta) in zip(('es', 'en'), secciones):
        titulo = ' '.join(f['t'] for f in seccion if f['alto'] > cuerpo_alto + 8)
        resto = [f for f in seccion if f['alto'] <= cuerpo_alto + 8]
        bloques = convertir(resto, cuerpo_x, cuerpo_alto, interlinea)
        bajada = ''
        for i, (marca, dato) in enumerate(bloques):
            if marca == 'BAJADA':
                bajada = dato if not bajada else bajada + ' ' + dato
            elif bajada:
                bloques = bloques[i:]; break
        datos = {'clave': clave, 'slug': slugs[idioma], 'volanta': minuscula(volanta),
                 'titulo': re.sub(r'\s+', ' ', titulo).strip(),
                 'bajada': re.sub(r'\s+', ' ', bajada).strip(),
                 'orden': orden, 'fecha': fecha}
        md = ('---\n' + ''.join('%s: %s\n' % (k, datos[k]) for k in
              ('clave', 'slug', 'volanta', 'titulo', 'bajada', 'orden', 'fecha'))
              + '---\n\n' + a_markdown(bloques, idioma) + '\n')
        destino = os.path.join(A.ANALISIS, '%s.%s.md' % (slugs[idioma], idioma))
        open(destino, 'w', encoding='utf-8').write(md)
        print('%-52s %5.1f KB' % (os.path.relpath(destino, A.REPO), len(md.encode()) / 1024))


if __name__ == '__main__':
    pdf, clave, es, en = sys.argv[1:5]
    fecha = sys.argv[5] if len(sys.argv) > 5 else '2026-11-06'
    orden = sys.argv[6] if len(sys.argv) > 6 else '1'
    extraer(pdf, clave, {'es': es, 'en': en}, fecha, orden)
