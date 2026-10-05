# -*- coding: utf-8 -*-
"""Del .docx del cliente a fuente/analisis/<slug>.<idioma>.md

    python3 herramientas/extraer.py documento.docx es-slug en-slug [fecha]

Cada documento trae la nota en los dos idiomas, una abajo de la otra, cada
una encabezada por «CORBEAU JOURNAL · TEMA». El script las separa y escribe
un archivo por idioma.

Trabaja sobre el árbol que arma pandoc, no sobre su texto: los recuadros
viajan como tablas de una sola celda, las notas de fuente como negrita
pegada a un enlace, y los epígrafes como párrafos enteramente en cursiva.
En texto plano eso hay que adivinarlo y se rompe con el primer documento
distinto.

Lo que sale es un borrador: conviene leer los subtítulos, que en el
documento vienen en mayúsculas y acá pasan a minúsculas, y revisar las
tablas que no traen encabezado.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import articulos as A

# nombres que no se escriben en minúscula al bajar un subtítulo de mayúsculas
PROPIOS = ('INV OIV ICC NIQ HMRC IWSR AWRI UK IVA VAT ABV IRI EE.UU. P1XELS '
           'Corbeau Malbec Argentina Argentine Chardonnay Torrontés Riojano Pinot '
           'Gris Sauvignon Blanc Mendoza Italia Italy Reino Unido United Kingdom '
           'Journal Grocer WineNews NielsenIQ').split()


def texto(inlines):
    """Los inlines de pandoc a Markdown."""
    o = []
    for n in inlines:
        t = n['t']
        if t == 'Str':
            o.append(n['c'])
        elif t in ('Space', 'SoftBreak', 'LineBreak'):
            o.append(' ')
        elif t == 'Strong':
            o.append('**%s**' % texto(n['c']).strip())
        elif t == 'Emph':
            o.append('*%s*' % texto(n['c']).strip())
        elif t == 'Link':
            o.append('[%s](%s)' % (texto(n['c'][1]).strip(), n['c'][2][0]))
        elif t in ('Underline', 'Span', 'Quoted', 'SmallCaps'):
            o.append(texto(n['c'][-1] if t in ('Span', 'Quoted') else n['c']))
        elif t == 'Note':
            continue
        else:
            o.append(n.get('c', '') if isinstance(n.get('c'), str) else '')
    return ''.join(o)


def plano(x):
    return re.sub(r'\*\*|\*|\[|\]\([^)]*\)', '', texto(x) if isinstance(x, list) else x)


def es_subtitulo(s):
    letras = [c for c in s if c.isalpha()]
    return bool(letras) and all(c.isupper() for c in letras) and len(s) < 90


def minuscula(s):
    s = s.strip()
    partes = s.split(' ')
    salida = []
    for p in partes:
        limpio = p.strip('.,:;¿?¡!()')
        propio = next((x for x in PROPIOS if x.upper() == limpio.upper()), None)
        salida.append(p.replace(limpio, propio) if propio else p.lower())
    s = ' '.join(salida)
    return s[0].upper() + s[1:] if s else s


def celdas(fila):
    return [t for t in fila[1]]


def filas_de(seccion):
    return [[c[4] for c in f[1]] for f in seccion]


def tabla(b):
    cabeza = filas_de(b['c'][3][1])
    cuerpo = [f for parte in b['c'][4] for f in filas_de(parte[3])]
    def celda(bloques):
        # dentro de una celda pandoc usa «Plain», no «Para»
        partes = [texto(x['c']).strip() for x in bloques if x['t'] in ('Para', 'Plain')]
        # la negrita del documento no viaja: en la tabla publicada esa jerarquía
        # la pone el diseño
        return re.sub(r'\*\*', '', ' '.join(p for p in partes if p))
    cabeza = [[celda(c) for c in f] for f in cabeza]
    cuerpo = [[celda(c) for c in f] for f in cuerpo]
    todas = cabeza + cuerpo
    # columnas vacías en todas las filas: en Word suelen ser la barra del gráfico
    vacias = [i for i in range(len(todas[0]))
              if all(len(f) > i and not f[i].strip() for f in todas)]
    recortar = lambda f: [c for i, c in enumerate(f) if i not in vacias]
    cabeza = [recortar(f) for f in cabeza]
    cuerpo = [recortar(f) for f in cuerpo]
    # una «cabecera» que son datos (números o porcentajes) no es una cabecera
    if cabeza and any(re.fullmatch(r'[+\-]?[\d.,]+\s*%?', c.strip())
                      for c in cabeza[0]):
        cuerpo = cabeza + cuerpo
        cabeza = []
    if not cabeza and cuerpo:
        cabeza, cuerpo = [cuerpo[0]], cuerpo[1:]
    n = len(cabeza[0])
    L = ['| ' + ' | '.join(cabeza[0]) + ' |', '| ' + ' | '.join(['---'] * n) + ' |']
    L += ['| ' + ' | '.join(f) + ' |' for f in cuerpo]
    return '\n'.join(L)


def recuadro(b):
    """Tabla de una sola celda: es el recuadro «Desde el origen»."""
    bloques = [c[4] for f in filas_de(b['c'][3][1]) + [f for p in b['c'][4] for f in filas_de(p[3])]
               for c in [f]][0] if False else None
    todos = []
    for seccion in [b['c'][3][1]] + [p[3] for p in b['c'][4]]:
        for fila in filas_de(seccion):
            for celda in fila:
                todos.extend(celda)
    partes = [texto(x['c']).strip() for x in todos if x['t'] in ('Para', 'Plain')]
    partes = [p for p in partes if p]
    etiqueta = re.sub(r'\*\*', '', partes[0])
    cuerpo = ' '.join(partes[1:]) if len(partes) > 1 else ''
    if not cuerpo:  # la etiqueta y el texto van en el mismo párrafo
        cuerpo = re.sub(r'^\*\*[^*]+\*\*\s*', '', partes[0]).strip()
    return cuerpo


def separar_negrita(s):
    """En el documento, el punto final de un rótulo en negrita a veces se come
    el espacio que sigue: «**¿Se percibe?**Una pregunta». Acá se repone."""
    return re.sub(r'(?<=[^\s*])\*\*(?=[^\s*,.;:)\]])', '** ', s)


def convertir(bloques_doc, idioma):
    salida, pendiente_tabla = [], False
    for b in bloques_doc:
        t = b['t']
        if t == 'Para':
            s = separar_negrita(texto(b['c']).strip())
            crudo = plano(b['c']).strip()
            if not s:
                continue
            if es_subtitulo(crudo):
                salida.append('## ' + minuscula(crudo))
                pendiente_tabla = False
            elif re.match(r'^\*\*(FUENTE|SOURCE)', s):
                cuerpo = re.sub(r'^\*\*(FUENTE|SOURCE)\s*\*\*\s*', '', s).strip()
                salida.append('FUENTE ' + cuerpo)
                pendiente_tabla = False
            elif re.match(r'^\*\*?→', s):
                item = re.sub(r'→\s*', '', s, count=1).strip()
                if salida and salida[-1].startswith('- '):
                    salida[-1] += '\n- ' + item
                else:
                    salida.append('- ' + item)
                pendiente_tabla = False
            elif re.fullmatch(r'\*[^*].*\*', s):
                cuerpo = s[1:-1].strip()
                salida.append(('PIE ' if pendiente_tabla else 'NOTA ') + cuerpo)
                pendiente_tabla = False
            else:
                salida.append(s)
                pendiente_tabla = False
        elif t == 'BlockQuote':
            partes = [texto(x['c']).strip() for x in b['c'] if x['t'] == 'Para']
            salida.append('> ' + ' '.join(partes))
            pendiente_tabla = False
        elif t == 'Table':
            if len(b['c'][2]) == 1:
                salida.append('ORIGEN ' + recuadro(b))
                pendiente_tabla = False
            else:
                salida.append(tabla(b))
                pendiente_tabla = True
        elif t in ('BulletList', 'OrderedList'):
            items = []
            for li in b['c']:
                items.append('- ' + ' '.join(texto(x['c']).strip() for x in li
                                             if x['t'] == 'Para'))
            salida.append('\n'.join(items))
            pendiente_tabla = False
        elif t == 'Header':
            salida.append('## ' + texto(b['c'][2]).strip())
    return '\n\n'.join(salida)


def partir_idiomas(bloques_doc):
    cortes = [i for i, b in enumerate(bloques_doc)
              if b['t'] == 'Para' and plano(b['c']).strip().upper().startswith('CORBEAU JOURNAL ·')]
    if len(cortes) != 2:
        raise SystemExit('Esperaba dos secciones «CORBEAU JOURNAL · …» y encontré %d'
                         % len(cortes))
    a, b = cortes
    return bloques_doc[a:b], bloques_doc[b:]


def extraer(docx, slugs, fecha, orden):
    bloques_doc = json.loads(subprocess.check_output(
        ['pandoc', '-f', 'docx', '-t', 'json', docx]))['blocks']
    secciones = partir_idiomas(bloques_doc)
    for idioma, seccion in zip(('es', 'en'), secciones):
        volanta = plano(seccion[0]['c']).split('·')[-1].strip()
        # el título va con estilo de título en unos documentos y como párrafo
        # común en otros: si no hay estilo, es el primer párrafo después del
        # rótulo «CORBEAU JOURNAL · …»
        cabezas = [i for i, b in enumerate(seccion) if b['t'] == 'Header']
        if cabezas:
            titulo = texto(seccion[cabezas[0]]['c'][2]).strip()
            resto = seccion[cabezas[0] + 1:]
        else:
            titulo = texto(seccion[1]['c']).strip()
            resto = seccion[2:]
        bajada = texto(resto[0]['c']).strip()
        bajada = re.sub(r'^\*(.*)\*$', r'\1', bajada).strip()
        cuerpo = convertir(resto[1:], idioma)
        datos = {'slug': slugs[idioma], 'par': slugs[A.OTRO[idioma]],
                 'volanta': minuscula(volanta), 'titulo': titulo, 'bajada': bajada,
                 'orden': orden, 'fecha': fecha}
        md = ('---\n' + ''.join('%s: %s\n' % (k, datos[k]) for k in
              ('slug', 'par', 'volanta', 'titulo', 'bajada', 'orden', 'fecha'))
              + '---\n\n' + cuerpo + '\n')
        destino = os.path.join(A.ANALISIS, '%s.%s.md' % (slugs[idioma], idioma))
        open(destino, 'w', encoding='utf-8').write(md)
        print('%-56s %5.1f KB' % (os.path.relpath(destino, A.REPO), len(md.encode()) / 1024))


if __name__ == '__main__':
    docx, es, en = sys.argv[1], sys.argv[2], sys.argv[3]
    fecha = sys.argv[4] if len(sys.argv) > 4 else '2026-10-01'
    orden = sys.argv[5] if len(sys.argv) > 5 else '1'
    os.makedirs(A.ANALISIS, exist_ok=True)
    extraer(docx, {'es': es, 'en': en}, fecha, orden)
