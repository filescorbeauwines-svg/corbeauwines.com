# -*- coding: utf-8 -*-
"""Arma las páginas de Análisis / Insights a partir de fuente/analisis/.

    python3 herramientas/construir.py

Entrada:
  fuente/analisis/<slug>.<idioma>.md     una nota, en un idioma
  fuente/plantilla.articulo.<idioma>.html
  fuente/plantilla.indice.<idioma>.html

Salida, una carpeta por idioma:
  sitio/es/analisis/<slug>/index.html   y su índice
  sitio/en/insights/<slug>/index.html   y su índice
  sitio/pt/analises/<slug>/index.html   y su índice

Las tres versiones de una nota se reconocen por el campo «clave», que es el
mismo en los tres archivos; el «slug» puede ser distinto en cada idioma.

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
LEER = {'es': 'Leer la nota', 'en': 'Read the piece', 'pt': 'Ler a nota'}
VOLVER = {'es': 'Volver a Análisis', 'en': 'Back to Insights', 'pt': 'Voltar para Análises'}
OTRO_IDIOMA = {'es': {'en': 'Leer en inglés', 'pt': 'Leer en portugués'},
               'en': {'es': 'Read in Spanish', 'pt': 'Read in Portuguese'},
               'pt': {'es': 'Ler em espanhol', 'en': 'Ler em inglês'}}
INDICE_SEO = {
    'es': ('Análisis · Corbeau Wines',
           'Análisis desde el origen: mercado, costos, normativa y producción de '
           'vino argentino. Corbeau Wines.'),
    'en': ('Insights · Corbeau Wines',
           'Analysis from the origin: market, costs, regulation and production of '
           'Argentine wine. Corbeau Wines.'),
    'pt': ('Análises · Corbeau Wines',
           'Análises desde a origem: mercado, custos, regulamentação e produção de '
           'vinho argentino. Corbeau Wines.'),
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


def hermanas(clave, idioma):
    """La misma nota en los otros idiomas: {idioma: slug}. Las notas se
    emparejan por el campo «clave», no por el nombre del archivo."""
    salida = {}
    for i in A.otros(idioma):
        for d in notas(i):
            if d['clave'] == clave:
                salida[i] = d['slug']
    return salida


def armar_articulo(datos, idioma):
    plantilla = open(os.path.join(A.FUENTE, 'plantilla.articulo.%s.html' % idioma),
                     encoding='utf-8').read()
    e = lambda s: html.escape(s, quote=False)
    cuerpo = '\n'.join('      ' + b for b in A.cuerpo_html(datos, idioma))
    pares = hermanas(datos['clave'], idioma)
    p = plantilla.replace('{{seo}}', A.seo(datos, idioma, pares))
    p = p.replace('{{volanta}}', e(datos['volanta']))
    p = p.replace('{{titulo}}', e(datos['titulo']))
    p = p.replace('{{bajada}}', e(datos['bajada']))
    p = p.replace('{{fecha}}', A.fecha_larga(idioma, datos['fecha']))
    p = p.replace('{{cuerpo}}', cuerpo)
    rel = lambda i: '../../../%s/%s/%s/' % (i, A.IDIOMA[i]['carpeta'], pares[i])
    sel = []
    # una nota puede estar todavía en dos idiomas y no en los tres: el selector
    # muestra solamente los que existen
    for i in [x for x in A.IDIOMAS if x == idioma or x in pares]:
        if sel:
            sel.append('<span class="langs__sep" aria-hidden="true">·</span>')
        if i == idioma:
            sel.append('<b class="langs__on" aria-current="true">%s</b>' % A.ROTULO[i])
        else:
            sel.append('<a class="langs__alt" href="%s" hreflang="%s" lang="%s">%s</a>'
                       % (rel(i), A.HREFLANG[i], A.HREFLANG[i], A.ROTULO[i]))
    p = p.replace('{{idiomas}}', ''.join(sel))
    cierre = '\n    '.join(
        '<a href="%s" hreflang="%s">%s %s</a>'
        % (rel(i), A.HREFLANG[i], OTRO_IDIOMA[idioma][i], FLECHA)
        for i in A.otros(idioma) if i in pares)
    p = p.replace('{{cierre}}', cierre)
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
    seo = '\n'.join([
        '<title>%s</title>' % titulo,
        '<meta name="description" content="%s">' % html.escape(descripcion, quote=True),
        '<link rel="canonical" href="%s">' % propia,
    ] + [
        '<link rel="alternate" hreflang="%s" href="%s">'
        % (A.HREFLANG[i], A.DOMINIO + A.ruta(i)) for i in A.IDIOMAS
    ] + [
        '<link rel="stylesheet" href="../../assets/analisis.css">',
    ])
    sel = []
    for i in A.IDIOMAS:
        if sel:
            sel.append('<span class="langs__sep" aria-hidden="true">·</span>')
        if i == idioma:
            sel.append('<b class="langs__on" aria-current="true">%s</b>' % A.ROTULO[i])
        else:
            sel.append('<a class="langs__alt" href="../../%s/%s/" hreflang="%s" lang="%s">%s</a>'
                       % (i, A.IDIOMA[i]['carpeta'], A.HREFLANG[i], A.HREFLANG[i], A.ROTULO[i]))
    p = (plantilla.replace('{{seo}}', seo).replace('{{listado}}', '\n'.join(piezas))
         .replace('{{idiomas}}', ''.join(sel)))
    destino = os.path.join(A.SITIO, idioma, A.IDIOMA[idioma]['carpeta'], 'index.html')
    open(destino, 'w', encoding='utf-8').write(p)
    return destino, len(p.encode())


if __name__ == '__main__':
    for idioma in A.IDIOMAS:
        lista = notas(idioma)
        for d in lista:
            faltan = [i for i in A.otros(idioma)
                      if not any(x['clave'] == d['clave'] for x in notas(i))]
            if faltan:
                # no es un error: una nota puede publicarse en dos idiomas y
                # traducirse al tercero más adelante
                print('  aviso: «%s» todavía no está en %s' % (d['slug'], ', '.join(faltan)))
        for d in lista:
            destino, peso = armar_articulo(d, idioma)
            print('%-62s %5.1f KB' % (os.path.relpath(destino, A.REPO), peso / 1024))
        destino, peso = armar_indice(lista, idioma)
        print('%-62s %5.1f KB · %d notas' % (os.path.relpath(destino, A.REPO),
                                             peso / 1024, len(lista)))
