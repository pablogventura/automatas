import numpy
import re
from  IPython.display import Math
import tikz

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
        c=r"""\node[state,initial]   (q)                {$q$};
\node[state]  (i) [right=of q] {$i$};
\node[state,accepting]  (f) [right=of q,below=of i] {$f$};
\path[->] (q) edge [above]   node         {$0$} (i)
(q) edge [loop below]   node         {$1$} ()
(q) edge [below]   node         {$1$} (f)
(f) edge [right]   node         {$\varepsilon$} (i);
"""

        return Tikz(c,"positioning,automata","on top/.style={preaction={draw=white,-}},on top/.default=4pt").svg()
