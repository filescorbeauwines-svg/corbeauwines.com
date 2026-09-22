# -*- coding: utf-8 -*-
"""Arma el sitio publicado (sitio/) a partir de fuente/.

    python3 herramientas/armar.py

Entrada:
  fuente/paginas.json              dirección, título y descripción de cada página
  fuente/plantilla.<idioma>.html   cabecera, menú, pie y scripts
  fuente/paginas/<idioma>/*.html   el contenido de cada página
  fuente/sprite.svg                los iconos

Salida: una página real por sección y por idioma (sitio/es/..., sitio/en/...),
el sitemap, y los menús de las páginas de Análisis apuntando a las
direcciones nuevas.

Qué resuelve respecto del sitio anterior: cada sección tiene su propia
dirección, título, descripción, canónica y par de idioma, que es lo que Google
necesita para mostrarla en un resultado. Antes eran vistas de una sola página
separadas por #, y para el buscador existían dos páginas en todo el sitio.

Se puede correr las veces que haga falta: siempre produce lo mismo.
"""
import html
import json
import os
import re

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SITIO = os.path.join(REPO, 'sitio')
FUENTE = os.path.join(REPO, 'fuente')

DATOS = json.load(open(os.path.join(FUENTE, 'paginas.json'), encoding='utf-8'))
DOMINIO = DATOS['sitio']
IDIOMAS = ('es', 'en')
OTRO = {'es': 'en', 'en': 'es'}
LOCALE = {'es': 'es_AR', 'en': 'en_US'}
# las páginas que cuelgan de Soluciones: en el menú marcan «Soluciones»
HIJAS = {'bulk', 'private', 'marcas', 'desarrollo', 'pixels', 'madbird'}

SPRITE = open(os.path.join(FUENTE, 'sprite.svg'), encoding='utf-8').read()
SIMBOLOS = {m.group(1): m.group(0) for m in
            re.finditer(r'<symbol id="(ic-[^"]+)".*?</symbol>', SPRITE, re.S)}
APERTURA_SPRITE = SPRITE[:SPRITE.index('<defs>') + len('<defs>')]

BODEGA = {
    "@context": "https://schema.org",
    "@type": "Winery",
    "name": "Corbeau Wines",
    "url": DOMINIO + "/",
    "email": "frodriguez@corbeauwines.com",
    "telephone": "+54 9 263 466 5862",
    "address": {"@type": "PostalAddress", "streetAddress": "Ruta Provincial 50",
                "addressLocality": "San Martín", "addressRegion": "Mendoza",
                "postalCode": "M5570", "addressCountry": "AR"},
    "geo": {"@type": "GeoCoordinates", "latitude": -33.0964301, "longitude": -68.4313713},
    "hasMap": "https://maps.app.goo.gl/NbZ8NgX1AQ6m74EF8",
}


def url(idioma, clave):
    return DATOS[idioma][clave]['url']


def resolver(texto, idioma):
    def r(m):
        clave = m.group(1)
        if clave not in DATOS[idioma]:
            raise SystemExit('Enlace a una página que no existe: {{url:%s}}' % clave)
        return url(idioma, clave)
    return re.sub(r'\{\{url:([a-z]+)\}\}', r, texto)


def sprite_para(texto):
    """Solo los iconos que la página usa. El juego completo pesa 104 KB y la
    mayoría de las páginas no usa ninguno."""
    usados = sorted(set(re.findall(r'href="#(ic-[a-z0-9-]+)"', texto)))
    if not usados:
        return ''
    faltan = [u for u in usados if u not in SIMBOLOS]
    if faltan:
        raise SystemExit('Iconos que no están en sprite.svg: %s' % faltan)
    return APERTURA_SPRITE + ''.join(SIMBOLOS[u] for u in usados) + '</defs></svg>'


def bloque_seo(idioma, clave, imagen):
    d = DATOS[idioma][clave]
    propia = DOMINIO + d['url']
    par = DOMINIO + url(OTRO[idioma], clave)
    e = lambda s: html.escape(s, quote=True)
    L = [
        '<title>%s</title>' % e(d['titulo']),
        '<meta name="description" content="%s">' % e(d['descripcion']),
        '<link rel="canonical" href="%s">' % propia,
        '<link rel="alternate" hreflang="%s" href="%s">' % (idioma, propia),
        '<link rel="alternate" hreflang="%s" href="%s">' % (OTRO[idioma], par),
        '<link rel="alternate" hreflang="x-default" href="%s">' % (DOMINIO + url('es', clave)),
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Corbeau Wines">',
        '<meta property="og:locale" content="%s">' % LOCALE[idioma],
        '<meta property="og:title" content="%s">' % e(d['titulo']),
        '<meta property="og:description" content="%s">' % e(d['descripcion']),
        '<meta property="og:url" content="%s">' % propia,
        '<meta property="og:image" content="%s">' % (DOMINIO + imagen),
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if clave in ('home', 'contacto'):
        datos = dict(BODEGA, image=DOMINIO + imagen)
        L.append('<script type="application/ld+json">%s</script>' %
                 json.dumps(datos, ensure_ascii=False))
    return '\n'.join(L)


def redireccion(idioma):
    """Solo en la portada: los enlaces viejos del tipo /es/#bulk.

    El servidor nunca ve lo que va después de #, así que no se puede redirigir
    desde _redirects: lo resuelve el navegador, antes de pintar nada."""
    mapa = {k: v['url'] for k, v in DATOS[idioma].items() if k != 'home'}
    return ('<script>\n/* Enlaces viejos con # (del sitio de una sola página) a su página nueva. */\n'
            '(function(){var m=%s;var k=(location.hash||"").slice(1);'
            'if(m[k])location.replace(m[k]);})();\n</script>\n' %
            json.dumps(mapa, ensure_ascii=False))


def marcar_menu(pagina, idioma, clave):
    """Lo que antes hacía el enrutador al cambiar de vista: subrayar en el menú
    la sección actual."""
    a = pagina.index('<nav class="site-nav"')
    b = pagina.index('</nav>', a)
    nav = pagina[a:b]
    activo = url(idioma, 'soluciones' if clave in HIJAS else clave)
    propia = url(idioma, clave)
    d0 = nav.index('<div class="drop">')
    d1 = nav.index('</div>', d0)
    arriba, drop, resto = nav[:d0], nav[d0:d1], nav[d1:]
    marca = '<a href="%s">' % activo
    arriba = arriba.replace(marca, '<a href="%s" aria-current="page">' % activo, 1)
    resto = resto.replace(marca, '<a href="%s" aria-current="page">' % activo, 1)
    drop = drop.replace('<a href="%s">' % propia, '<a href="%s" class="is-current">' % propia, 1)
    return pagina[:a] + arriba + drop + resto + pagina[b:]


def armar_pagina(idioma, clave):
    plantilla = open(os.path.join(FUENTE, 'plantilla.%s.html' % idioma), encoding='utf-8').read()
    principal = open(os.path.join(FUENTE, 'paginas', idioma, clave + '.html'), encoding='utf-8').read()
    imagen = re.search(r'src="(/assets/img/[^"]+)"',
                       open(os.path.join(FUENTE, 'paginas', idioma, 'home.html'),
                            encoding='utf-8').read()).group(1)
    p = plantilla.replace('{{principal}}', principal)
    p = p.replace('{{sprite}}', sprite_para(p))
    p = p.replace('{{seo}}', bloque_seo(idioma, clave, imagen))
    p = p.replace('{{redireccion}}', redireccion(idioma) if clave == 'home' else '')
    p = p.replace('{{url_par}}', url(OTRO[idioma], clave))
    p = resolver(p, idioma)
    p = marcar_menu(p, idioma, clave)
    sobra = re.findall(r'\{\{[^}]*\}\}', p)
    if sobra:
        raise SystemExit('Quedaron marcadores sin resolver en %s/%s: %s' % (idioma, clave, sobra))
    destino = os.path.join(SITIO, url(idioma, clave).strip('/'), 'index.html')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    open(destino, 'w', encoding='utf-8').write(p)
    return destino, len(p.encode())


# páginas viejas -> nuevas, para los menús de Análisis, que se armaron con
# enlaces al archivo de una sola página (../../index.html#why)
def ajustar_analisis():
    tocadas = 0
    for idioma, carpeta in (('es', 'analisis'), ('en', 'insights')):
        base = os.path.join(SITIO, idioma, carpeta)
        for raiz, _, archivos in os.walk(base):
            for f in archivos:
                if f != 'index.html':
                    continue
                ruta = os.path.join(raiz, f)
                s = open(ruta, encoding='utf-8').read()
                n = re.sub(r'href="(?:\.\./)+index\.html#([a-z]+)"',
                           lambda m: 'href="%s"' % url(idioma, m.group(1)), s)
                if n != s:
                    open(ruta, 'w', encoding='utf-8').write(n)
                    tocadas += 1
    return tocadas


def sitemap():
    E = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
         'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    n = 0
    claves = [k for k in DATOS['es'] if k != 'insights']
    for idioma in IDIOMAS:
        for k in claves:
            E.append('  <url><loc>%s</loc>' % (DOMINIO + url(idioma, k)))
            for i2 in IDIOMAS:
                E.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>'
                         % (i2, DOMINIO + url(i2, k)))
            E.append('  </url>')
            n += 1
    # Análisis: índice y artículos, con su par tomado de su propio hreflang
    for idioma, carpeta in (('es', 'analisis'), ('en', 'insights')):
        base = os.path.join(SITIO, idioma, carpeta)
        for raiz, _, archivos in sorted(os.walk(base)):
            if 'index.html' not in archivos:
                continue
            s = open(os.path.join(raiz, 'index.html'), encoding='utf-8').read()
            canon = re.search(r'<link rel="canonical" href="([^"]+)"', s).group(1)
            E.append('  <url><loc>%s</loc>' % canon)
            for hl, href in re.findall(r'<link rel="alternate" hreflang="([a-z-]+)" href="([^"]+)"', s):
                if hl != 'x-default':
                    E.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (hl, href))
            E.append('  </url>')
            n += 1
    E.append('</urlset>')
    open(os.path.join(SITIO, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(E) + '\n')
    return n


if __name__ == '__main__':
    for idioma in IDIOMAS:
        for clave in DATOS[idioma]:
            if clave == 'insights':
                continue
            destino, peso = armar_pagina(idioma, clave)
            print('%-52s %4.0f KB' % (os.path.relpath(destino, REPO), peso / 1024))
    print('menús de Análisis actualizados en %d páginas' % ajustar_analisis())
    print('sitemap.xml · %d direcciones' % sitemap())
