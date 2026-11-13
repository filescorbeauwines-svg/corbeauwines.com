# -*- coding: utf-8 -*-
"""Arma el PDF de The Corbeau Way desde el texto estructurado.

    python3 armar_libro.py es|pt

Lee libro.<idioma>.txt y escribe libro.<idioma>.pdf, con la misma caja, las
mismas tipografías (Caladea y Carlito) y los mismos colores que el original.
"""
import re
import subprocess
import sys

IDIOMA = sys.argv[1] if len(sys.argv) > 1 else 'es'

ROTULOS = {
    'es': {'capitulo': 'CAPÍTULO', 'ley': 'LEY CORBEAU N.º', 'bloque': 'BLOQUE',
           'pregunta': 'LA PREGUNTA QUE RESPONDE', 'cierre': 'CIERRE',
           'indice': 'Índice', 'subtitulo': 'Los principios que sostienen nuestras decisiones',
           'bajada': 'Treinta leyes para construir una empresa que merezca perdurar',
           'pie': 'CORBEAU WINES · FAMILIA RODRÍGUEZ',
           'lugar': 'MENDOZA · ARGENTINA · MMXXVI'},
    'pt': {'capitulo': 'CAPÍTULO', 'ley': 'LEI CORBEAU N.º', 'bloque': 'BLOCO',
           'pregunta': 'A PERGUNTA QUE RESPONDE', 'cierre': 'FECHAMENTO',
           'indice': 'Sumário', 'subtitulo': 'Os princípios que sustentam nossas decisões',
           'bajada': 'Trinta leis para construir uma empresa que mereça perdurar',
           'pie': 'CORBEAU WINES · FAMÍLIA RODRÍGUEZ',
           'lugar': 'MENDOZA · ARGENTINA · MMXXVI'},
}[IDIOMA]
LENGUA = {'es': 'spanish', 'pt': 'portuguese'}[IDIOMA]


def tex(t):
    """Texto plano a LaTeX."""
    t = re.sub(r'\s+', ' ', t).strip()   # los espacios dobles vienen de juntar
                                        # líneas del PDF y se ven en el renglón
    t = t.replace('\\', '\\textbackslash{}')
    for a, b in (('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
                 ('_', r'\_'), ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'),
                 ('^', r'\textasciicircum{}')):
        t = t.replace(a, b)
    return t


def espaciar(t):
    return r'{\marca %s}' % tex(t)


CABEZA = r'''\documentclass[11pt]{book}
\usepackage[paperwidth=160mm,paperheight=240mm,left=22.05mm,right=22.05mm,
            top=25.4mm,bottom=24mm,footskip=14mm]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{microtype}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage[hidelinks]{hyperref}
\usepackage{polyglossia}
\setmainlanguage{LENGUA}

\setmainfont{Caladea}[Numbers=OldStyle]
\newfontfamily\sansita{Carlito}

\definecolor{bordo}{RGB}{122,34,48}
\definecolor{tinta}{RGB}{26,26,26}
\definecolor{gris}{RGB}{74,74,74}
\definecolor{malva}{RGB}{185,163,168}
\color{tinta}

\linespread{1.07}
\setlength{\parindent}{12pt}
\setlength{\parskip}{0pt}
\setlength{\emergencystretch}{1.2em}
\frenchspacing

% las marcas en versalitas espaciadas
\newcommand{\marca}[1]{{\sansita\fontsize{8}{10}\selectfont\color{gris}%
  \addfontfeature{LetterSpace=38}\MakeUppercase{#1}}}
\newcommand{\marcabordo}[1]{{\sansita\fontsize{8}{10}\selectfont\color{bordo}%
  \addfontfeature{LetterSpace=38}\MakeUppercase{#1}}}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{{\fontsize{10}{12}\selectfont\color{gris}\thepage}}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{{\fontsize{10}{12}\selectfont\color{gris}\thepage}}}

\newcommand{\titulosec}[1]{%
  \par\vspace*{10mm}{\fontsize{21}{25}\selectfont\color{bordo}#1\par}%
  \vspace{3mm}{\color{malva}\hrule height 0.4pt}\vspace{9mm}\noindent\ignorespaces}
\newcommand{\volanta}[1]{\par\vspace{2mm}{\sansita\fontsize{9}{12}\selectfont
  \color{gris}\addfontfeature{LetterSpace=12}#1\par}\vspace{2mm}\noindent\ignorespaces}
\newcommand{\seccion}[2]{\par\vspace{5.5mm}\noindent
  {\fontsize{9.5}{12}\selectfont\color{malva}#1}\hspace{5pt}%
  {\fontsize{12}{14}\selectfont\color{bordo}#2}\par\vspace{1.6mm}\noindent\ignorespaces}
\newcommand{\cita}[1]{\par\vspace{7mm}\begin{center}\begin{minipage}{0.76\textwidth}
  \centering\itshape\color{bordo}#1\end{minipage}\end{center}\vspace{4mm}\noindent\ignorespaces}
\newcommand{\manifiestotitulo}[1]{\thispagestyle{fancy}\vspace*{14mm}
  \begin{center}{\marca{THE CORBEAU WAY}}\par\vspace{9mm}
  {\fontsize{21}{25}\selectfont\color{bordo}#1\par}\end{center}
  \addcontentsline{toc}{subsection}{\textit{#1}}\vspace{8mm}}
\newcommand{\manifiesto}[1]{\par\begin{center}\begin{minipage}{0.84\textwidth}
  \centering #1\end{minipage}\end{center}\vspace{3.2mm}}
% --- aperturas ------------------------------------------------------------
\newcounter{capnum}
\newcommand{\capitulomarca}[1]{\setcounter{capnum}{#1}%
  \thispagestyle{fancy}\vspace*{8mm}\begin{center}\marca{ROTCAP\ #1}\end{center}}
\newcommand{\capitulotitulo}[1]{%
  \begin{center}{\fontsize{20}{24}\selectfont\color{bordo}#1\par}\end{center}
  \addcontentsline{toc}{subsection}{\protect\numberline{\thecapnum}#1}%
  \vspace{4mm}\noindent\ignorespaces}
\newcommand{\leymarca}[1]{\vspace{4mm}{\color{malva}\hrule height 0.4pt}\vspace{4mm}
  \begin{center}\marcabordo{ROTLEY\ #1}\end{center}\vspace{-1mm}}
\newcommand{\leytexto}[1]{\begin{center}\begin{minipage}{0.80\textwidth}
  \centering{\fontsize{12.5}{16}\selectfont\itshape\color{bordo}#1}\end{minipage}\end{center}
  \vspace{4mm}{\color{malva}\hrule height 0.4pt}\vspace{7mm}}
\newcommand{\preguntatexto}[1]{\begin{center}\marca{ROTPREG}\par\vspace{1.5mm}
  \begin{minipage}{0.82\textwidth}\centering{\fontsize{11}{14}\selectfont\color{gris}#1}\end{minipage}
  \end{center}\vspace{7mm}\noindent\ignorespaces}
\newcommand{\bloquemarca}[1]{\thispagestyle{empty}\vspace*{32mm}
  \begin{center}\marcabordo{ROTBLO\ #1}\end{center}\gdef\bloqueromano{#1}}
\newcommand{\bloquetitulo}[1]{\begin{center}\vspace{3mm}
  {\fontsize{27}{32}\selectfont\color{bordo}#1\par}\end{center}
  \addcontentsline{toc}{section}{\MakeUppercase{ROTBLO\ \bloqueromano\ · #1}}%
  \vspace{6mm}\noindent\ignorespaces}
\newcommand{\seccionlibro}[1]{\thispagestyle{fancy}\titulosec{#1}%
  \addcontentsline{toc}{subsection}{\textit{#1}}}
\newcommand{\itemlista}[1]{\par\vspace{2mm}\noindent\hspace{12pt}%
  \begin{minipage}{\dimexpr\textwidth-24pt\relax}\noindent\textemdash\hspace{6pt}#1\end{minipage}\par}
\newcommand{\leylista}[2]{\par\vspace{3.4mm}\noindent
  \makebox[0pt][l]{\hspace{-0pt}{\sansita\fontsize{9.5}{12}\selectfont\color{bordo}#1}}%
  \hspace{19pt}\begin{minipage}[t]{\dimexpr\textwidth-19pt\relax}#2\end{minipage}\par}

% --- índice ---------------------------------------------------------------
\usepackage{tocloft}
\renewcommand{\cftdot}{.}
\renewcommand{\cftdotsep}{1.2}
\setlength{\cftbeforesecskip}{4mm}
\setlength{\cftbeforesubsecskip}{1.1mm}
\renewcommand{\cftsecfont}{\sansita\fontsize{8}{11}\selectfont\color{bordo}\addfontfeature{LetterSpace=28}}
\renewcommand{\cftsecpagefont}{\sansita\fontsize{8}{11}\selectfont\color{bordo}}
\renewcommand{\cftsecleader}{\hfill}
\renewcommand{\cftsubsecfont}{\fontsize{10.5}{13}\selectfont}
\renewcommand{\cftsubsecpagefont}{\fontsize{10}{13}\selectfont}
\renewcommand{\cftsubsecleader}{\color{malva}\cftdotfill{\cftdotsep}}
\setlength{\cftsubsecindent}{0pt}
\setlength{\cftsubsecnumwidth}{16pt}
\renewcommand{\cftsubsecaftersnum}{\hspace{2pt}}
\renewcommand{\cftsubsecpresnum}{\sansita\fontsize{9}{12}\selectfont\color{bordo}}

\begin{document}
\frenchspacing   % polyglossia lo reactiva al abrir el documento
\frontmatter
\pagestyle{empty}
'''


def portada():
    return r'''
\begin{center}
\vspace*{38mm}
{\fontsize{19}{23}\selectfont\color{gris}\addfontfeature{LetterSpace=60}THE}\par
\vspace{2mm}
{\fontsize{36}{40}\selectfont\bfseries\color{bordo}\addfontfeature{LetterSpace=22}CORBEAU}\par
\vspace{2mm}
{\fontsize{19}{23}\selectfont\color{gris}\addfontfeature{LetterSpace=60}WAY}\par
\vspace{12mm}
{\color{malva}\rule{0.78\textwidth}{0.4pt}}\par
\vspace{6mm}
{\fontsize{12}{15}\selectfont\itshape SUBTITULO}\par
\vspace{2mm}
{\fontsize{10}{13}\selectfont\color{gris} BAJADA}\par
\vspace{60mm}
{\sansita\fontsize{8}{11}\selectfont\bfseries\color{tinta}\addfontfeature{LetterSpace=28}PIE}\par
\vspace{1.5mm}
{\sansita\fontsize{8}{11}\selectfont\color{malva}\addfontfeature{LetterSpace=28}LUGAR}\par
\end{center}
\clearpage\thispagestyle{empty}\mbox{}\clearpage
'''.replace('SUBTITULO', tex(ROTULOS['subtitulo'])).replace('BAJADA', tex(ROTULOS['bajada'])) \
   .replace('PIE', tex(ROTULOS['pie'])).replace('LUGAR', tex(ROTULOS['lugar']))


def leer():
    for linea in open('libro.%s.txt' % IDIOMA, encoding='utf-8'):
        linea = linea.rstrip('\n')
        if not linea:
            continue
        partes = [p.strip() for p in linea.split(' | ')]
        yield partes[0], partes[1:]


def main():
    cabeza = (CABEZA.replace('LENGUA', LENGUA)
              .replace('ROTCAP', tex(ROTULOS['capitulo']))
              .replace('ROTLEY', tex(ROTULOS['ley']))
              .replace('ROTPREG', tex(ROTULOS['pregunta']))
              .replace('ROTBLO', tex(ROTULOS['bloque'])))
    salida = [cabeza, portada()]
    salida.append('\\titulosec{%s}\n\\vspace{-6mm}\n' % tex(ROTULOS['indice']))
    salida.append('\\renewcommand{\\contentsname}{}\n\\tableofcontents\n\\clearpage\n')
    salida.append('\\mainmatter\n\\pagestyle{fancy}\n')
    esperando_titulo = None
    for marca, partes in leer():
        t = [tex(x) for x in partes]
        if marca == 'TITULO_SECCION':
            if esperando_titulo == 'capitulo':
                salida.append('\\capitulotitulo{%s}\n' % t[0]); esperando_titulo = None
            elif esperando_titulo == 'bloque':
                salida.append('\\bloquetitulo{%s}\n' % t[0]); esperando_titulo = None
            else:
                salida.append('\\clearpage\\seccionlibro{%s}\n' % t[0])
        elif marca == 'CAPITULO_N':
            salida.append('\\clearpage\\capitulomarca{%s}\n' % t[0]); esperando_titulo = 'capitulo'
        elif marca == 'BLOQUE_N':
            salida.append('\\clearpage\\bloquemarca{%s}\n' % t[0]); esperando_titulo = 'bloque'
        elif marca == 'LEY_N':
            salida.append('\\leymarca{%s}\n' % t[0])
        elif marca == 'LEY':
            salida.append('\\leytexto{%s}\n' % t[0])
        elif marca == 'PREGUNTA':
            salida.append('\\preguntatexto{%s}\n' % t[0])
        elif marca == 'SECCION':
            salida.append('\\seccion{%s}{%s}\n' % (t[0], t[1]))
        elif marca == 'CIERRE':
            salida.append('\\volanta{%s}\n' % tex(ROTULOS['cierre']))
        elif marca == 'VOLANTA':
            salida.append('\\volanta{%s}\n' % t[0])
        elif marca == 'CITA':
            salida.append('\\cita{%s}\n' % t[0])
        elif marca == 'TITULO_MANIFIESTO':
            salida.append('\\clearpage\\manifiestotitulo{%s}\n' % t[0])
        elif marca == 'MANIFIESTO':
            salida.append('\\manifiesto{%s}\n' % t[0])
        elif marca == 'LISTA':
            salida.append('\\itemlista{%s}\n' % t[0])
        elif marca.startswith('LEYN_'):
            salida.append('\\leylista{%s}{%s}\n' % (marca[5:], t[0]))
        elif marca == 'P':
            # después de un título el párrafo sigue sin sangría: va pegado
            pegado = salida[-1].rstrip().endswith('\\ignorespaces')
            salida.append(('%s\n' if pegado else '\n%s\n') % t[0])
        elif marca == 'MARCA':
            salida.append('\\par\\vspace{2mm}%s\\par\n' % espaciar(t[0]))
    salida.append('\\end{document}\n')
    open('libro.%s.tex' % IDIOMA, 'w', encoding='utf-8').write(''.join(salida))
    print('escrito libro.%s.tex' % IDIOMA)


if __name__ == '__main__':
    main()
