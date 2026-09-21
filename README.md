# corbeauwines.com

Sitio de Corbeau Wines. Netlify publica automáticamente cada cambio que entra
a la rama `main`.

## Qué hay acá

- `sitio/` — lo que se publica, tal cual. Es la carpeta que antes se subía
  arrastrando un zip.
  - `es/` y `en/` — el sitio en cada idioma.
  - `es/analisis/` y `en/insights/` — los artículos, una página cada uno.
  - `pedidos/` — puente al sistema de pedidos (atuq.net.ar).
  - `assets/img/` — fotos e imágenes, compartidas por los dos idiomas.
  - `assets/fuentes/`, `assets/analisis.css` — fuentes y estilos compartidos.
  - `descargas/` — las fichas técnicas, el catálogo y *The Corbeau Way*.
  - `_redirects`, `robots.txt`, `sitemap.xml` — reglas para Netlify y Google.
- `netlify.toml` — le dice a Netlify qué carpeta publicar.
- `herramientas/` — scripts de mantenimiento. No se publican.

## Estado

Etapa 1 del plan SEO hecha: las imágenes y los PDF, que iban incrustados en
el HTML, ahora son archivos. Cada página principal bajó de 21,9 MB a 265 KB,
así que Google la lee entera (antes leía el 11%). El sitio se ve idéntico:
verificado captura por captura en las once vistas, los dos idiomas, a 1440 y
430 px.

Pendiente: partir cada idioma en páginas reales (etapas 2 y 3).

## Si algo sale mal

Netlify guarda cada versión publicada: en *Deploys*, elegir la anterior y
tocar *Publish deploy* vuelve el sitio atrás en segundos. Y cada versión
también queda en el historial de este repositorio.
