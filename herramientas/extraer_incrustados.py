# -*- coding: utf-8 -*-
"""Etapa 1 del plan SEO: saca del HTML todo lo que va incrustado en base64.

Por qué: cada index.html pesaba 21,9 MB porque llevaba adentro 60 imágenes, 22
PDF y 8 fuentes. Google lee solo los primeros 2 MB de una página, así que veía
el 11% del texto; y GitHub no aceptaba subir archivos de ese tamaño por la web.
Con los archivos afuera, el HTML queda en unos cientos de KB y el navegador baja
cada imagen una sola vez, compartida entre los dos idiomas.

Qué hace:
  · imágenes           → sitio/assets/img/<nombre-del-alt>-<hash>.<ext>
  · PDF (fichas, catálogo) → sitio/descargas/<nombre de descarga>.pdf
  · fuentes            → sitio/assets/fuentes/ (reusa las que ya estaban)
  · The Corbeau Way    → sitio/descargas/the-corbeau-way-<idioma>.pdf, y el
    botón pasa a ser un enlace común en vez de armar el PDF con JavaScript.

El mismo archivo usado en las dos versiones se guarda una sola vez: se
identifica por su contenido, no por su nombre.

Uso: python3 herramientas/extraer_incrustados.py   (desde la raíz del repo)
"""
import base64
import hashlib
import os
import re
import unicodedata

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sitio')
EXT = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/svg+xml': 'svg',
       'image/webp': 'webp', 'image/gif': 'gif', 'application/pdf': 'pdf',
       'font/otf': 'otf', 'font/ttf': 'ttf', 'font/woff2': 'woff2'}

URI = re.compile(r'data:([a-z]+/[a-z0-9+.\-]+);base64,([A-Za-z0-9+/=]+)')


def babosa(s, largo=48):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-').lower()
    return s[:largo].strip('-') or 'archivo'


def huella(datos):
    return hashlib.sha1(datos).hexdigest()[:8]


# contenido -> ruta relativa a sitio/, para no escribir dos veces lo mismo
guardados = {}

# las fuentes que ya estaban en assets/fuentes (las puso la sección Análisis)
dir_fuentes = os.path.join(RAIZ, 'assets', 'fuentes')
for f in os.listdir(dir_fuentes):
    guardados[hashlib.sha1(open(os.path.join(dir_fuentes, f), 'rb').read())
              .hexdigest()] = 'assets/fuentes/' + f


def guardar(mime, datos, pista):
    """Escribe el archivo si no existe y devuelve su ruta relativa a sitio/."""
    clave = hashlib.sha1(datos).hexdigest()
    if clave in guardados:
        return guardados[clave]
    ext = EXT.get(mime, 'bin')
    if mime == 'application/pdf':
        nombre = pista if pista.lower().endswith('.pdf') else babosa(pista) + '.pdf'
        carpeta = 'descargas'
    elif mime.startswith('font/'):
        nombre = '%s-%s.%s' % (babosa(pista, 30), huella(datos), ext)
        carpeta = 'assets/fuentes'
    else:
        nombre = '%s-%s.%s' % (babosa(pista), huella(datos), ext)
        carpeta = 'assets/img'
    os.makedirs(os.path.join(RAIZ, carpeta), exist_ok=True)
    ruta = '%s/%s' % (carpeta, nombre)
    destino = os.path.join(RAIZ, ruta)
    # dos PDF distintos con el mismo nombre de descarga: se desempata
    if os.path.exists(destino):
        base, e = os.path.splitext(nombre)
        ruta = '%s/%s-%s%s' % (carpeta, base, huella(datos), e)
        destino = os.path.join(RAIZ, ruta)
    open(destino, 'wb').write(datos)
    guardados[clave] = ruta
    return ruta


def pista_para(html, inicio, mime):
    """Busca un nombre con sentido cerca del recurso: alt, download o nada."""
    etiqueta_ini = html.rfind('<', 0, inicio)
    etiqueta_fin = html.find('>', inicio)
    etiqueta = html[etiqueta_ini:inicio] + html[inicio:etiqueta_fin][-400:]
    if mime == 'application/pdf':
        m = re.search(r'download="([^"]+)"', etiqueta)
        return m.group(1) if m else 'documento.pdf'
    m = re.search(r'alt="([^"]+)"', html[etiqueta_ini:etiqueta_fin + 1][:200] +
                  html[inicio:etiqueta_fin + 1][-300:])
    if m:
        return m.group(1)
    if mime.startswith('font/'):
        m = re.search(r'font-family:\s*"([^"]+)"', html[max(0, inicio - 300):inicio])
        return m.group(1) if m else 'fuente'
    return 'textura'


def procesar(idioma):
    ruta = os.path.join(RAIZ, idioma, 'index.html')
    html = open(ruta, encoding='utf-8').read()
    antes = len(html.encode())

    # 1. The Corbeau Way: una variable de JavaScript con el PDF en base64
    m = re.search(r'<script>var PDF_WAY="([A-Za-z0-9+/=]+)";</script>\n?', html)
    if m:
        datos = base64.b64decode(m.group(1))
        pdf = guardar('application/pdf', datos,
                      'the-corbeau-way-%s.pdf' % idioma)
        html = html[:m.start()] + html[m.end():]
        # el botón pasa a ser un enlace común: sin id, el script que armaba el
        # blob no lo encuentra y no hace nada
        viejo = '<a class="btn btn--onDark" id="btn-way" href="#"'
        assert viejo in html, 'no encontré el botón de The Corbeau Way'
        html = html.replace(viejo, '<a class="btn btn--onDark" href="../%s" '
                            'target="_blank" rel="noopener"' % pdf, 1)

    # 2. todos los data: URI, de atrás para adelante para no correr índices
    cuenta = {}
    for m in reversed(list(URI.finditer(html))):
        mime = m.group(1)
        datos = base64.b64decode(m.group(2))
        rel = guardar(mime, datos, pista_para(html, m.start(), mime))
        html = html[:m.start()] + '../' + rel + html[m.end():]
        cuenta[mime] = cuenta.get(mime, 0) + 1

    open(ruta, 'w', encoding='utf-8').write(html)
    print('%s/index.html  %.1f MB -> %.0f KB   %s' % (
        idioma, antes / 1e6, len(html.encode()) / 1024,
        ', '.join('%d %s' % (n, t.split('/')[1]) for t, n in sorted(cuenta.items()))))


if __name__ == '__main__':
    for idioma in ('es', 'en'):
        procesar(idioma)
    for carpeta in ('assets/img', 'descargas', 'assets/fuentes'):
        d = os.path.join(RAIZ, carpeta)
        archivos = os.listdir(d)
        peso = sum(os.path.getsize(os.path.join(d, f)) for f in archivos)
        print('%-16s %3d archivos  %5.1f MB' % (carpeta, len(archivos), peso / 1e6))
