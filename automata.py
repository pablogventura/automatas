import numpy
import re
from  IPython.display import Math
import subprocess

class Tikz(object):

    def __init__(self, code, tikzlibraries, tikzpictureoptions):
        self.code = code
        self.tikzlibraries = tikzlibraries
        self.tikzpictureoptions = tikzpictureoptions

    def latex(self):
        return (r"""
\documentclass[convert={convertexe={convert},size=400x240,outext=.png},border=0pt]{standalone}
\usepackage[]{tikz}
\usetikzlibrary{automata,positioning,arrows}
\tikzset{
->, % makes the edges directed
%>=stealth’, % makes the arrow heads bold
node distance=3cm, % specifies the minimum distance between two nodes. Change if necessary.
every state/.style={thick, fill=gray!10}, % sets the properties for each ’state’ node
initial text=$ $, % sets the text that appears on the start arrow
}
\usetikzlibrary{""" + self.tikzlibraries + r"""}

\begin{document}
\begin{tikzpicture}[""" + self.tikzpictureoptions + r"""]
""" + self.code + r"""
\end{tikzpicture}
\end{document}
""").encode()

    def svg(self):
        subprocess.run(["latex"],capture_output=True,input=self.latex())
        subprocess.run(["dvisvgm", "--zoom=1", "--exact", "--font-format=woff", "texput.dvi"],capture_output=True)
        with open("/content/texput.svg","r") as f:
            svg_code = f.read()
        subprocess.call(["rm", "/content/texput.svg", "/content/texput.aux", "/content/texput.dvi", "/content/texput.log"])
        return svg_code



class Delta(object):
    def __init__(self,tabla):
        self.tabla = tabla
        self.matriz=numpy.genfromtxt(self.tabla.splitlines(),dtype=str)
        self.estados = list(self.matriz[1:,0])
        self.alfabeto = list(self.matriz[0,1:])

    
    def __call__(self, estado, simbolo):
        return self.matriz[self.estados.index(estado)+1,self.alfabeto.index(simbolo)+1]

    def _prettify_name(self, text):
        match = re.match(r"([a-z]+)([0-9]+)", text, re.I)
        if match:
            text,number = match.groups()
            return f"{text}_{{{number}}}"


    def _repr_latex_(self):
        result = r"\begin{array}{c|"+ "c" * len(self.alfabeto) + "}\n"
        result += f"\delta_{{{self.matriz[0,0]}}} & " + " & ".join(self.alfabeto) + r"\\\hline" + "\n"
        for q in self.estados:
            result += self._prettify_name(q)
            for a in self.alfabeto:
                result += " & " + self._prettify_name(self(q,a))
            result += r"\\" + "\n"
        result += r"\end{array}"
        return result
#d & d & g\\\hline
#a & a & n
#\end{array}"""

        

class DFA(object):
    """
    Clase para definir un automata finito determinista
    """
    def __init__(self, delta, inicial, finales):
        self.estados = set(delta.estados)
        self.alfabeto = set(delta.alfabeto)
        self.delta = delta
        self.inicial = inicial
        self.finales = set(finales)
        assert inicial in self.estados
        assert finales <= self.estados

        self.reset()

    def reset(self):
        self.estado_actual = self.inicial

    def delta_sombrero(self, palabra):
        for a in palabra:
            assert a in self.alfabeto
            self.estado_actual = self.delta(self.estado_actual,a)
            assert self.estado_actual in self.estados
    
    def en_lenguaje(self, palabra):
        self.reset()
        self.delta_sombrero(palabra)
        return self.estado_actual in self.finales

    def _repr_svg_(self):
        c=r"""\node[state] (phi) {$\emptyset$};
\node[state, accepting, right of=phi] (1) {$\{1\}$};
\node[state, right of=1] (2) {$\{2\}$};
\node[state, accepting, right of=2] (12) {$\{1, 2\}$};
\node[state, below of=phi] (3) {$\{3\}$};
\node[state, initial, initial where=above, accepting, right of=3] (13) {$\{1, 3\}$};
\node[state, right of=13] (23) {$\{2, 3\}$};
\node[state, accepting, right of=23] (123) {$\{1, 2, 3\}$};
\draw (phi) edge[loop left] node{$a, b$} (phi)
    (1) edge[above] node{$a$} (phi)
    (1) edge[above] node{$b$} (2)
    (2) edge[right] node{$a$} (23)
    (2) edge[above] node{$b$} (3)
    (12) edge[above, pos=.3, left=2pt] node{$a, b$} (23)
    (3) edge[left] node{$b$} (phi)
    (3) edge[below] node{$a$} (13)
    (13) edge[loop right] node{$a$} (13)
    (13) edge[above] node{$b$} (2)
    (23) edge[bend left, above] node{$a$} (123)
    (23) edge[bend left, below] node{$b$} (3)
    (123) edge[loop above] node{$a$} (123)
    (123) edge[bend left, below] node{$b$} (23);
"""

        return Tikz(c,"","").svg()
