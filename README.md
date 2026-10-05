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
- `fuente/` — de donde salen las páginas:
  - `paginas.json` — dirección, título y descripción (lo que muestra Google)
    de cada página, en los dos idiomas.
  - `plantilla.es.html`, `plantilla.en.html` — cabecera, menú, pie y scripts.
  - `paginas/es/*.html`, `paginas/en/*.html` — el contenido de cada página.
  - `sprite.svg` — los iconos.
  - `analisis/<slug>.<idioma>.md` — el texto de cada nota de Análisis, con su
    título, su resumen y su fecha arriba. Es el original: se edita acá, no en
    la página publicada.
  - `plantilla.articulo.<idioma>.html`, `plantilla.indice.<idioma>.html` — el
    armazón de las páginas de Análisis.
- `netlify.toml` — le dice a Netlify qué carpeta publicar.
- `herramientas/` — scripts de mantenimiento. No se publican.
  - `armar.py` — arma las páginas, el sitemap y los menús de Análisis.
    Después de tocar algo en `fuente/`: `python3 herramientas/armar.py`.
  - `construir.py` — arma las páginas de Análisis y sus índices a partir de
    `fuente/analisis/`. Después conviene correr `armar.py`, que regenera el
    sitemap con las notas nuevas.
  - `extraer.py` — pasa el `.docx` de una nota (español e inglés adentro) a
    los dos archivos `.md`:
    `python3 herramientas/extraer.py nota.docx slug-es slug-en 2026-10-01 1`
  - `articulos.py` — el formato de las notas: qué significa cada marca.
  - `migrar.py`, `recuperar.py`, `extraer_incrustados.py` — se usaron una sola
    vez; quedan como registro.

## Estado

- Etapa 1: las imágenes y los PDF, que iban incrustados en el HTML, ahora son
  archivos. La página de cada idioma bajó de 21,9 MB a 265 KB.
- Etapas 2 y 3: cada sección es una página real con su dirección, título,
  descripción, canónica, par de idioma e imagen para redes; la portada y
  Contacto llevan además los datos de la bodega para Google (schema.org
  `Winery`). Los enlaces viejos del tipo `/es/#bulk` llevan a la página nueva.
  Verificado captura por captura: las 22 páginas se ven idénticas a las vistas
  que reemplazan, a 1440 y 430 px.

## Agregar una nota a Análisis

1. Escribir o editar `fuente/analisis/<slug>.es.md` y `<slug>.en.md`. Si viene
   en un `.docx`, `extraer.py` hace el borrador.
2. `python3 herramientas/construir.py`
3. `python3 herramientas/armar.py`
4. Subir los cambios. Netlify publica solo.

Los dos archivos de una nota tienen que apuntarse entre sí con el campo `par`;
`construir.py` avisa si uno quedó sin pareja.

## Si algo sale mal

Netlify guarda cada versión publicada: en *Deploys*, elegir la anterior y
tocar *Publish deploy* vuelve el sitio atrás en segundos. Y cada versión
también queda en el historial de este repositorio.
