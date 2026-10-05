# -*- coding: utf-8 -*-
"""Piezas comunes de la sección Análisis / Insights.

Un artículo se escribe en un archivo de texto (Markdown) con sus datos
arriba, y de ahí sale la página. Acá viven las reglas de ese formato: qué
significa cada marca, y cómo se convierte en HTML y de vuelta.

El formato, completo:

    ---
    slug: que-cuesta-un-malbec-a-granel   dirección de la nota
    par: what-does-bulk-malbec-cost       la misma nota en el otro idioma
    volanta: Cómo se compra               la línea chica de arriba del título
    titulo: ...
    bajada: ...                           el resumen; también es la descripción
                                          que muestra Google
    fecha: 2026-09-11
    ---

    Un párrafo normal.

    ## Un subtítulo

    > Un destacado.

    FUENTE [INV, Exportaciones de varietales](https://…)
    FUENTE INV, Exportaciones de varietales      (cuando no hay enlace)

    | Encabezado | Encabezado |
    | --- | --- |
    | celda | celda |

    PIE La aclaración que va abajo de la tabla.

    - **Un punto.** Su explicación.

    ORIGEN Lo que Corbeau cuenta en primera persona.
    MODELO El texto del recuadro «Modelo de consulta», en cursiva.
    NOTA El párrafo de cierre.

Las marcas en mayúsculas se eligieron así para que se vean a simple vista
en el texto y no se confundan con el contenido.
"""
import html
import os
import re

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SITIO = os.path.join(REPO, 'sitio')
FUENTE = os.path.join(REPO, 'fuente')
ANALISIS = os.path.join(FUENTE, 'analisis')
DOMINIO = 'https://corbeauwines.com'

IDIOMA = {
    'es': {'carpeta': 'analisis', 'seccion': 'Análisis',
           'origen': 'Desde el origen', 'modelo': 'Modelo de consulta',
           'fuente': 'Fuente', 'publicado': 'Publicado el %-d de %s de %Y',
           'meses': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
                     'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']},
    'en': {'carpeta': 'insights', 'seccion': 'Insights',
           'origen': 'From the origin', 'modelo': 'Enquiry template',
           'fuente': 'Source', 'publicado': 'Published %-d %s %Y',
           'meses': ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                     'August', 'September', 'October', 'November', 'December']},
}
OTRO = {'es': 'en', 'en': 'es'}


def ruta(idioma, slug=None):
    base = '/%s/%s/' % (idioma, IDIOMA[idioma]['carpeta'])
    return base + (slug + '/' if slug else '')


def fecha_larga(idioma, iso):
    a, m, d = (int(x) for x in iso.split('-'))
    mes = IDIOMA[idioma]['meses'][m - 1]
    return ('Publicado el %d de %s de %d' % (d, mes, a) if idioma == 'es'
            else 'Published %d %s %d' % (d, mes, a))


# --- leer un artículo -------------------------------------------------------

def leer(ruta_md):
    s = open(ruta_md, encoding='utf-8').read()
    if not s.startswith('---'):
        raise SystemExit('Falta la cabecera de datos en %s' % ruta_md)
    cab, cuerpo = s[3:].split('\n---\n', 1)
    datos = {}
    for linea in cab.strip().splitlines():
        if ':' in linea:
            k, v = linea.split(':', 1)
            datos[k.strip()] = v.strip()
    faltan = [k for k in ('slug', 'par', 'volanta', 'titulo', 'bajada', 'fecha')
              if k not in datos]
    if faltan:
        raise SystemExit('Faltan datos en %s: %s' % (ruta_md, ', '.join(faltan)))
    datos['cuerpo'] = cuerpo.strip('\n')
    return datos


def bloques(cuerpo):
    """Corta el cuerpo en bloques por línea en blanco, salvo dentro de una
    tabla: una tabla es un solo bloque aunque tenga una fila por línea."""
    salida, actual = [], []
    for linea in cuerpo.split('\n'):
        if linea.strip() == '':
            if actual:
                salida.append('\n'.join(actual))
                actual = []
        else:
            actual.append(linea)
    if actual:
        salida.append('\n'.join(actual))
    return salida


# --- texto con formato ------------------------------------------------------

def enlinea(t):
    """**negrita**, *cursiva* y [texto](dirección)."""
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![*\w])\*([^*]+)\*(?!\*)', r'<em>\1</em>', t)
    return t


def a_markdown(frag):
    """De vuelta a Markdown, para recuperar un artículo ya publicado."""
    t = frag
    t = re.sub(r'<a href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', t, flags=re.S)
    t = re.sub(r'</?strong>', '**', t)
    t = re.sub(r'</?em>', '*', t)
    t = re.sub(r'<[^>]+>', '', t)
    return html.unescape(t).strip()


# --- de Markdown a HTML -----------------------------------------------------

def cuerpo_html(datos, idioma):
    L = IDIOMA[idioma]
    salida = []
    for b in bloques(datos['cuerpo']):
        linea = b.strip()
        if linea.startswith('## '):
            salida.append('<h2>%s</h2>' % enlinea(linea[3:].strip()))
        elif linea.startswith('> '):
            salida.append('<p class="destacado">%s</p>' % enlinea(linea[2:].strip()))
        elif linea.startswith('FUENTE '):
            salida.append('<p class="fuente"><b>%s</b>%s</p>'
                          % (L['fuente'], enlinea(linea[7:].strip())))
        elif linea.startswith('PIE '):
            salida.append('<p class="pie">%s</p>' % enlinea(linea[4:].strip()))
        elif linea.startswith('NOTA '):
            salida.append('<p class="nota">%s</p>' % enlinea(linea[5:].strip()))
        elif linea.startswith('ORIGEN '):
            salida.append('<aside class="origen"><b>%s</b><p>%s</p></aside>'
                          % (L['origen'], enlinea(linea[7:].strip())))
        elif linea.startswith('MODELO '):
            salida.append('<aside class="modelo"><b>%s</b><p><em>%s</em></p></aside>'
                          % (L['modelo'], enlinea(linea[7:].strip())))
        elif linea.startswith('|'):
            salida.append(tabla_html(linea))
        elif linea.startswith('- '):
            items = ['<li>%s</li>' % enlinea(x[2:].strip())
                     for x in linea.split('\n') if x.strip().startswith('- ')]
            salida.append('<ul class="puntos">%s</ul>' % ''.join(items))
        else:
            salida.append('<p>%s</p>' % enlinea(linea.replace('\n', ' ')))
    return salida


def tabla_html(bloque):
    filas = [[c.strip() for c in f.strip().strip('|').split('|')]
             for f in bloque.split('\n') if f.strip()]
    filas = [f for f in filas if not all(set(c) <= set('-: ') for c in f)]
    enc, resto = filas[0], filas[1:]
    th = ''.join('<th>%s</th>' % enlinea(c) for c in enc)
    tb = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % enlinea(c) for c in f)
                 for f in resto)
    return ('<div class="tabla-envoltura"><table><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>' % (th, tb))


# --- la parte de la cabecera que ve Google ---------------------------------

def seo(datos, idioma, par):
    e = lambda s: html.escape(s, quote=True)
    propia = DOMINIO + ruta(idioma, datos['slug'])
    otra = DOMINIO + ruta(OTRO[idioma], datos['par'])
    L = [
        '<title>%s · Corbeau Wines</title>' % e(datos['titulo']),
        '<meta name="description" content="%s">' % e(datos['bajada']),
        '<link rel="canonical" href="%s">' % propia,
        '<link rel="alternate" hreflang="%s" href="%s">' % (idioma, propia),
        '<link rel="alternate" hreflang="%s" href="%s">' % (OTRO[idioma], otra),
        '<meta property="og:type" content="article">',
        '<meta property="og:title" content="%s">' % e(datos['titulo']),
        '<meta property="og:description" content="%s">' % e(datos['bajada']),
        '<meta property="og:url" content="%s">' % propia,
        '<link rel="stylesheet" href="../../../assets/analisis.css">',
        '<script type="application/ld+json">',
        '{"@context":"https://schema.org","@type":"Article",',
        ' "headline":%s,' % _j(datos['titulo']),
        ' "description":%s,' % _j(datos['bajada']),
        ' "datePublished":"%s",' % datos['fecha'],
        ' "inLanguage":"%s",' % idioma,
        ' "author":{"@type":"Organization","name":"Corbeau Wines"},',
        ' "publisher":{"@type":"Organization","name":"Corbeau Wines"},',
        ' "mainEntityOfPage":"%s"}' % propia,
        '</script>',
    ]
    return '\n'.join(L)


def _j(s):
    import json
    return json.dumps(s, ensure_ascii=False)
