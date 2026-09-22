# corbeauwines.com

Sitio de Corbeau Wines. Netlify publica automáticamente cada cambio que entra
a la rama `main`.

## Qué hay acá

- `sitio/` — lo que se publica, tal cual. Es la carpeta que antes se subía
  arrastrando un zip.
  - `es/` y `en/` — el sitio en cada idioma, una carpeta por página
    (`es/soluciones/vino-a-granel/`, `en/contact/`…). **No se editan a mano**:
    las arma `herramientas/armar.py` a partir de `fuente/`.
  - `es/analisis/` y `en/insights/` — los artículos, una página cada uno.
  - `pedidos/` — puente al sistema de pedidos (atuq.net.ar).
  - `assets/img/` — fotos e imágenes, compartidas por los dos idiomas.
  - `assets/sitio.css` — la hoja de estilos de las páginas principales.
  - `assets/fuentes/`, `assets/analisis.css` — fuentes y estilos compartidos.
  - `descargas/` — las fichas técnicas, el catálogo y *The Corbeau Way*.
  - `_redirects`, `robots.txt`, `sitemap.xml` — reglas para Netlify y Google.
- `fuente/` — de donde salen las páginas principales:
  - `paginas.json` — dirección, título y descripción (lo que muestra Google)
    de cada página, en los dos idiomas.
  - `plantilla.es.html`, `plantilla.en.html` — cabecera, menú, pie y scripts.
  - `paginas/es/*.html`, `paginas/en/*.html` — el contenido de cada página.
  - `sprite.svg` — los iconos.
- `netlify.toml` — le dice a Netlify qué carpeta publicar.
- `herramientas/` — scripts de mantenimiento. No se publican.
  - `armar.py` — arma las páginas, el sitemap y los menús de Análisis.
    Después de tocar algo en `fuente/`: `python3 herramientas/armar.py`.
  - `migrar.py`, `extraer_incrustados.py` — se usaron una sola vez; quedan
    como registro.

## Estado

- Etapa 1: las imágenes y los PDF, que iban incrustados en el HTML, ahora son
  archivos. La página de cada idioma bajó de 21,9 MB a 265 KB.
- Etapas 2 y 3: cada sección es una página real con su dirección, título,
  descripción, canónica, par de idioma e imagen para redes; la portada y
  Contacto llevan además los datos de la bodega para Google (schema.org
  `Winery`). Los enlaces viejos del tipo `/es/#bulk` llevan a la página nueva.
  Verificado captura por captura: las 22 páginas se ven idénticas a las vistas
  que reemplazan, a 1440 y 430 px.

## Si algo sale mal

Netlify guarda cada versión publicada: en *Deploys*, elegir la anterior y
tocar *Publish deploy* vuelve el sitio atrás en segundos. Y cada versión
también queda en el historial de este repositorio.
