# -*- coding: utf-8 -*-
"""Arma las páginas de Análisis / Insights a partir de fuente/analisis/.

    python3 herramientas/construir.py

Entrada:
  fuente/analisis/<slug>.<idioma>.md     una nota, en un idioma
  fuente/plantilla.articulo.<idioma>.html
  fuente/plantilla.indice.<idioma>.html

Salida:
  sitio/es/analisis/<slug>/index.html  y su índice
  sitio/en/insights/<slug>/index.html  y su índice

Se puede correr las veces que haga falta: siempre produce lo mismo. Después
conviene correr herramientas/armar.py, que regenera el sitemap con las notas
nuevas adentro.

El orden del listado: primero la fecha más reciente; entre notas del mismo
día manda el campo «orden».
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import articulos as A

FLECHA = ('<svg viewBox="0 0 19 14" aria-hidden="true">'
          '<path d="M0 7h18M12 1l6 6-6 6"/></svg>')
LEER = {'es': 'Leer la nota', 'en': 'Read the piece'}
INDICE_SEO = {
    'es': ('Análisis · Corbeau Wines',
           'Análisis desde el origen: mercado, costos, normativa y producción de '
           'vino argentino. Corbeau Wines.'),
    'en': ('Insights · Corbeau Wines',
           'Analysis from the origin: market, costs, regulation and production of '
           'Argentine wine. Corbeau Wines.'),
}


def notas(idioma):
    salida = []
    for f in sorted(os.listdir(A.ANALISIS)):
        if f.endswith('.%s.md' % idioma):
            d = A.leer(os.path.join(A.ANALISIS, f))
            d['orden'] = int(d.get('orden', 99))
            salida.append(d)
    salida.sort(key=lambda d: (d['fecha'], -d['orden']), reverse=True)
    return salida


def armar_articulo(datos, idioma):
    plantilla = open(os.path.join(A.FUENTE, 'plantilla.articulo.%s.html' % idioma),
                     encoding='utf-8').read()
    e = lambda s: html.escape(s, quote=False)
    cuerpo = '\n'.join('      ' + b for b in A.cuerpo_html(datos, idioma))
    p = plantilla.replace('{{seo}}', A.seo(datos, idioma, datos['par']))
    p = p.replace('{{volanta}}', e(datos['volanta']))
    p = p.replace('{{titulo}}', e(datos['titulo']))
    p = p.replace('{{bajada}}', e(datos['bajada']))
    p = p.replace('{{fecha}}', A.fecha_larga(idioma, datos['fecha']))
    p = p.replace('{{cuerpo}}', cuerpo)
    p = p.replace('{{par}}', '../../../%s/%s/%s/'
                  % (A.OTRO[idioma], A.IDIOMA[A.OTRO[idioma]]['carpeta'], datos['par']))
    sobra = re.findall(r'\{\{[^}]*\}\}', p)
    if sobra:
        raise SystemExit('Marcadores sin resolver en %s/%s: %s'
                         % (idioma, datos['slug'], sobra))
    destino = os.path.join(A.SITIO, idioma, A.IDIOMA[idioma]['carpeta'],
                           datos['slug'], 'index.html')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    open(destino, 'w', encoding='utf-8').write(p)
    return destino, len(p.encode())


def armar_indice(lista, idioma):
    plantilla = open(os.path.join(A.FUENTE, 'plantilla.indice.%s.html' % idioma),
                     encoding='utf-8').read()
    e = lambda s: html.escape(s, quote=False)
    piezas = []
    for d in lista:
        piezas.append(
            '    <a class="pieza-nota" href="%s/">\n'
            '      <p class="volanta">%s</p>\n'
            '      <h2>%s</h2>\n'
            '      <p>%s</p>\n'
            '      <span class="leer">%s %s</span>\n'
            '    </a>' % (d['slug'], e(d['volanta']), e(d['titulo']), e(d['bajada']),
                          LEER[idioma], FLECHA))
    titulo, descripcion = INDICE_SEO[idioma]
    propia = A.DOMINIO + A.ruta(idioma)
    otra = A.DOMINIO + A.ruta(A.OTRO[idioma])
    seo = '\n'.join([
        '<title>%s</title>' % titulo,
        '<meta name="description" content="%s">' % html.escape(descripcion, quote=True),
        '<link rel="canonical" href="%s">' % propia,
        '<link rel="alternate" hreflang="%s" href="%s">' % (idioma, propia),
        '<link rel="alternate" hreflang="%s" href="%s">' % (A.OTRO[idioma], otra),
        '<link rel="stylesheet" href="../../assets/analisis.css">',
    ])
    p = plantilla.replace('{{seo}}', seo).replace('{{listado}}', '\n'.join(piezas))
    destino = os.path.join(A.SITIO, idioma, A.IDIOMA[idioma]['carpeta'], 'index.html')
    open(destino, 'w', encoding='utf-8').write(p)
    return destino, len(p.encode())


if __name__ == '__main__':
    for idioma in ('es', 'en'):
        lista = notas(idioma)
        pares = {d['slug']: d['par'] for d in lista}
        otros = {d['slug'] for d in notas(A.OTRO[idioma])}
        for slug, par in pares.items():
            if par not in otros:
                raise SystemExit('La nota %s dice que su par es %s, que no existe en %s'
                                 % (slug, par, A.OTRO[idioma]))
        for d in lista:
            destino, peso = armar_articulo(d, idioma)
            print('%-62s %5.1f KB' % (os.path.relpath(destino, A.REPO), peso / 1024))
        destino, peso = armar_indice(lista, idioma)
        print('%-62s %5.1f KB · %d notas' % (os.path.relpath(destino, A.REPO),
                                             peso / 1024, len(lista)))
