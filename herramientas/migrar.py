# -*- coding: utf-8 -*-
"""Migración única: del archivo por idioma a las piezas en fuente/.

Hasta acá cada idioma era un solo index.html con once vistas adentro, que un
JavaScript mostraba de a una según el # de la dirección. Google no trata lo que
va después de # como páginas distintas, así que para el buscador existían dos
páginas en todo el sitio.

Este script corre UNA vez. Parte cada archivo por sus costuras y deja:

  sitio/assets/sitio.css        la hoja de estilos, compartida por todas
  fuente/plantilla.<idioma>.html cabecera, menú, pie y scripts de cada idioma
  fuente/paginas/<idioma>/<clave>.html   el contenido de cada página
  fuente/sprite.svg              los iconos (cada página lleva solo los suyos)

De acá en adelante se edita fuente/ y se corre herramientas/armar.py.

Los enlaces internos quedan como {{url:clave}} en vez de una dirección fija:
armar.py los resuelve según el idioma. Así cambiar una dirección es tocar una
línea de fuente/paginas.json, no buscar y reemplazar en veintidós archivos.
"""
import os
import re

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SITIO = os.path.join(REPO, 'sitio')
FUENTE = os.path.join(REPO, 'fuente')


def fin_de_etiqueta(s, i, nombre):
    """Índice justo después del cierre del elemento que abre en i, contando
    anidamiento. Dentro de cada vista hay otros <article> (las tarjetas), así
    que cortar en el primer </article> deja la vista partida."""
    prof = 0
    abre, cierra = '<' + nombre, '</' + nombre + '>'
    k = i
    while True:
        a = s.find(abre, k)
        c = s.find(cierra, k)
        if a != -1 and a < c and s[a + len(abre)] in ' >\n':
            prof += 1
            k = a + len(abre)
        else:
            prof -= 1
            k = c + len(cierra)
            if prof == 0:
                return k


def normalizar(html):
    """Lo que cambia igual en plantilla y páginas."""
    # navegación: data-go (resuelto por JavaScript) -> enlace de verdad
    html = re.sub(r'data-go="([a-z]+)"', r'href="{{url:\1}}"', html)
    html = html.replace('href="analisis/"', 'href="{{url:insights}}"').replace('href="insights/"', 'href="{{url:insights}}"')
    # rutas a archivos: relativas a /es/ -> desde la raíz, porque las páginas
    # nuevas viven a distintas profundidades (/es/, /es/contacto/,
    # /es/soluciones/vino-a-granel/)
    html = html.replace('"../assets/', '"/assets/').replace('"../descargas/', '"/descargas/')
    return html


def migrar(idioma):
    s = open(os.path.join(SITIO, idioma, 'index.html'), encoding='utf-8').read()

    # --- estilos: idénticos en los dos idiomas, van a un archivo compartido
    a = s.index('<style>') + len('<style>')
    b = s.index('</style>')
    css = s[a:b].replace('url("../assets/', 'url("/assets/')
    if idioma == 'es':
        open(os.path.join(SITIO, 'assets', 'sitio.css'), 'w', encoding='utf-8').write(
            '/* Hoja de estilos del sitio de Corbeau Wines, compartida por todas las\n'
            '   páginas y los dos idiomas. */\n' + css.strip() + '\n')

    # script de la cabecera (aparición de titulares), que va antes de pintar
    m = re.search(r'</style>\s*(<script>.*?</script>)\s*</head>', s, re.S)
    script_cabecera = m.group(1)

    # --- cuerpo
    cuerpo = s[s.index('<body>'):]
    main_a = cuerpo.index('<main>') + len('<main>')
    main_b = cuerpo.index('</main>')
    arriba, principal, abajo = cuerpo[:main_a], cuerpo[main_a:main_b], cuerpo[main_b:]

    # los iconos: se guardan aparte y cada página incluye solo los que usa
    ms = re.search(r'<svg class="icon-sprite".*?</svg>', arriba, re.S)
    if idioma == 'es':
        open(os.path.join(FUENTE, 'sprite.svg'), 'w', encoding='utf-8').write(ms.group(0) + '\n')
    arriba = arriba[:ms.start()] + '{{sprite}}' + arriba[ms.end():]

    # selector de idioma: pasa a apuntar a la página equivalente del otro idioma
    arriba = re.sub(r'(<a class="langs__alt" href=")[^"]*(")', r'\1{{url_par}}\2', arriba)

    # --- scripts del pie: sale lo que ya no tiene sentido con páginas reales
    j = abajo.index('<script>')
    pie, js = abajo[:j], abajo[j:]
    quitar = [
        # el enrutador de vistas
        ('  /* navegación entre páginas (una sola vista por vez) */',
         "  go(pages[initial] ? initial : 'home');\n"),
        # The Corbeau Way ya es un enlace común desde la etapa 1
        ('/* ---------- The Corbeau Way', '})();\n'),
        # el selector que arrastraba el # entre idiomas
        ('/* ---------- Selector de idioma', '})();\n'),
    ]
    for desde, hasta in quitar:
        x = js.index(desde)
        y = js.index(hasta, x) + len(hasta)
        js = js[:x] + js[y:]

    plantilla = (
        '<!DOCTYPE html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '{{seo}}\n'
        '<link rel="stylesheet" href="/assets/sitio.css">\n'
        '{{redireccion}}'
        '%s\n</head>\n' % (idioma, script_cabecera)
    ) + normalizar(arriba) + '\n{{principal}}\n' + normalizar(pie) + js
    open(os.path.join(FUENTE, 'plantilla.%s.html' % idioma), 'w', encoding='utf-8').write(plantilla)

    # --- una página por vista
    os.makedirs(os.path.join(FUENTE, 'paginas', idioma), exist_ok=True)
    claves = []
    for m in re.finditer(r'<article class="page" id="page-([a-z]+)"', principal):
        clave = m.group(1)
        # el comentario rotulado que precede a cada vista viaja con ella
        ini = principal.rfind('<!-- ====', 0, m.start())
        prev_fin = principal.rfind('</article>', 0, m.start())
        if ini == -1 or ini < prev_fin:
            ini = m.start()
        fin = fin_de_etiqueta(principal, m.start(), 'article')
        html = principal[ini:fin]
        html = html.replace('<article class="page" id="page-%s" hidden>' % clave,
                            '<article class="page" id="page-%s">' % clave)
        # el botón de cierre de Bulk Wine no llevaba a ningún lado
        html = html.replace('<a class="btn btn--onDark" href="#">',
                            '<a class="btn btn--onDark" href="{{url:contacto}}">')
        html = normalizar(html)
        open(os.path.join(FUENTE, 'paginas', idioma, clave + '.html'), 'w',
             encoding='utf-8').write(html.strip() + '\n')
        claves.append(clave)
    print('%s · %d páginas: %s' % (idioma, len(claves), ', '.join(claves)))


if __name__ == '__main__':
    os.makedirs(FUENTE, exist_ok=True)
    for idioma in ('es', 'en'):
        migrar(idioma)
