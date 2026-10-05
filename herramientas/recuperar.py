# -*- coding: utf-8 -*-
"""Recuperación única: de las páginas publicadas de Análisis a fuente/.

Las notas se publicaron en septiembre desde un espacio de trabajo que después
se recicló, así que el texto original quedó solamente dentro del HTML. Este
script lo devuelve a su formato editable y, de paso, saca de las mismas
páginas la plantilla con la que se arman: cabecera, menú, pie y scripts.

Corre una vez. De acá en adelante se edita fuente/analisis/*.md y se corre
herramientas/construir.py.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import articulos as A


def partir(s, inicio, fin):
    a = s.index(inicio)
    b = s.index(fin, a)
    return s[:a], s[a + len(inicio):b], s[b:]


def plantilla_articulo(s, idioma):
    """La página sin su contenido: lo variable queda como {{marcador}}."""
    p = s[:s.index('<title>')] + '{{seo}}' + s[s.index('</head>'):]
    p = re.sub(r'<p class="volanta">.*?</p>', '<p class="volanta">{{volanta}}</p>', p)
    p = re.sub(r'<h1 class="titulo">.*?</h1>', '<h1 class="titulo">{{titulo}}</h1>', p)
    p = re.sub(r'<p class="bajada">.*?</p>', '<p class="bajada">{{bajada}}</p>', p)
    p = re.sub(r'<span class="fecha">.*?</span>', '<span class="fecha">{{fecha}}</span>', p)
    a = p.index('<div class="cuerpo">') + len('<div class="cuerpo">')
    b = p.index('</div>\n  </article>')
    p = p[:a] + '\n{{cuerpo}}\n    ' + p[b:]
    # los dos enlaces al otro idioma: el del menú y el del cierre
    p = re.sub(r'(class="langs__alt" href=")[^"]*(")', r'\1{{par}}\2', p)
    p = re.sub(r'(<a href=")\.\./\.\./\.\./(?:en/insights|es/analisis)/[^"]*(" hreflang=)',
               r'\1{{par}}\2', p)
    return p


def cuerpo_a_markdown(cuerpo, idioma):
    L = A.IDIOMA[idioma]
    salida = []
    for m in re.finditer(r'<(h2|p|ul|aside|div)(?: class="([a-z-]+)")?[ >].*?</\1>',
                         cuerpo, re.S):
        etiqueta, clase, frag = m.group(1), m.group(2) or '', m.group(0)
        interior = frag[frag.index('>') + 1:frag.rindex('</')]
        if etiqueta == 'h2':
            salida.append('## ' + A.a_markdown(interior))
        elif clase == 'destacado':
            salida.append('> ' + A.a_markdown(interior))
        elif clase == 'fuente':
            texto = re.sub(r'^<b>.*?</b>', '', interior, flags=re.S)
            salida.append('FUENTE ' + A.a_markdown(texto))
        elif clase == 'pie':
            salida.append('PIE ' + A.a_markdown(interior))
        elif clase == 'nota':
            salida.append('NOTA ' + A.a_markdown(interior))
        elif clase in ('origen', 'modelo'):
            texto = re.search(r'<p>(.*?)</p>', interior, re.S).group(1)
            # el «modelo» ya va en cursiva por su forma: no se guarda el marcador
            texto = re.sub(r'^<em>(.*)</em>$', r'\1', texto.strip(), flags=re.S)
            salida.append(('ORIGEN ' if clase == 'origen' else 'MODELO ')
                          + A.a_markdown(texto))
        elif clase == 'puntos':
            salida.append('\n'.join('- ' + A.a_markdown(li) for li in
                                    re.findall(r'<li>(.*?)</li>', interior, re.S)))
        elif clase == 'tabla-envoltura':
            salida.append(tabla_a_markdown(interior))
        elif etiqueta == 'p':
            salida.append(A.a_markdown(interior))
        else:
            raise SystemExit('Bloque que no sé leer: %s' % frag[:80])
    return '\n\n'.join(salida)


def tabla_a_markdown(interior):
    filas = []
    for tr in re.findall(r'<tr>(.*?)</tr>', interior, re.S):
        filas.append([A.a_markdown(c) for c in
                      re.findall(r'<t[hd]>(.*?)</t[hd]>', tr, re.S)])
    L = ['| ' + ' | '.join(filas[0]) + ' |',
         '| ' + ' | '.join('---' for _ in filas[0]) + ' |']
    L += ['| ' + ' | '.join(f) + ' |' for f in filas[1:]]
    return '\n'.join(L)


def volanta_de(indice, slug):
    m = re.search(r'<a class="pieza-nota" href="%s/">\s*<p class="volanta">(.*?)</p>'
                  % re.escape(slug), indice, re.S)
    return m.group(1) if m else ''


def recuperar(idioma):
    carpeta = os.path.join(A.SITIO, idioma, A.IDIOMA[idioma]['carpeta'])
    slugs = sorted(d for d in os.listdir(carpeta)
                   if os.path.isdir(os.path.join(carpeta, d)))
    indice = open(os.path.join(carpeta, 'index.html'), encoding='utf-8').read()
    primera = True
    for slug in slugs:
        s = open(os.path.join(carpeta, slug, 'index.html'), encoding='utf-8').read()
        if primera:
            open(os.path.join(A.FUENTE, 'plantilla.articulo.%s.html' % idioma),
                 'w', encoding='utf-8').write(plantilla_articulo(s, idioma))
            pi = indice[:indice.index('<title>')] + '{{seo}}' + indice[indice.index('</head>'):]
            a = pi.index('<div class="listado">') + len('<div class="listado">')
            b = pi.index('</div>', a)
            pi = pi[:a] + '\n{{listado}}\n  ' + pi[b:]
            open(os.path.join(A.FUENTE, 'plantilla.indice.%s.html' % idioma),
                 'w', encoding='utf-8').write(pi)
            primera = False
        datos = {
            'slug': slug,
            'par': re.search(r'hreflang="%s" href="https://corbeauwines.com/\w+/\w+/([^/]+)/"'
                             % A.OTRO[idioma], s).group(1),
            'volanta': volanta_de(indice, slug),
            'titulo': re.search(r'<h1 class="titulo">(.*?)</h1>', s, re.S).group(1),
            'bajada': re.search(r'<p class="bajada">(.*?)</p>', s, re.S).group(1),
            'fecha': re.search(r'"datePublished":"(.*?)"', s).group(1),
        }
        cuerpo = s[s.index('<div class="cuerpo">') + len('<div class="cuerpo">'):
                   s.index('</div>\n  </article>')]
        md = ('---\n' + ''.join('%s: %s\n' % (k, datos[k]) for k in
              ('slug', 'par', 'volanta', 'titulo', 'bajada', 'fecha')) + '---\n\n'
              + cuerpo_a_markdown(cuerpo, idioma) + '\n')
        destino = os.path.join(A.ANALISIS, '%s.%s.md' % (slug, idioma))
        open(destino, 'w', encoding='utf-8').write(md)
        print('%-60s %5.1f KB' % (os.path.relpath(destino, A.REPO), len(md.encode()) / 1024))


if __name__ == '__main__':
    os.makedirs(A.ANALISIS, exist_ok=True)
    for idioma in ('es', 'en'):
        recuperar(idioma)
