import numpy
import re
from  IPython.display import Math
import subprocess
from math import sqrt

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
    
    def _get_steps(self,q0,q1):
        result = set()
        for a in self.alfabeto:
            v = self(q0,a)
            if v == q1:
                result.add(a)
        return result

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
        self._generate_tikz()
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
    def find_place(self,q,x,y,places):
        places[(x,y)] = q
        if x==0 and y==0:
            return ""
        elif x==0:
            return ", below of=" + places[(x,y-1)]
        elif y==0:
            return ", right of=" + places[(x-1,y)]
        else:
            return ", below of=" + places[(x,y-1)]
    def _arrow(self,q0,q1,places):
        x_q0,y_q0 = list(places.keys())[list(places.values()).index(q0)]
        x_q1,y_q1 = list(places.keys())[list(places.values()).index(q1)]
        distancia = sqrt((x_q1-x_q0)**2+(y_q1-y_q0)**2)
        if distancia > 1:
            modificador = " bend"
        else:
            modificador = ""

        syms = self.delta._get_steps(q0,q1)
        if syms:
            return {r"  (" + q0 + r") edge[above" + modificador + r"] node{$" + ", ".join(syms) + r"$} (" + q1 + r")" + "\n"}
        else:
            return {}

    def _arrow_loop(self,q,places):
        syms = self.delta._get_steps(q,q)
        if syms:
            return {r"  (" + q + r") edge[loop above] node{$" + ", ".join(syms) + r"$} (" + q + r")" + "\n"}
        else:
            return {}
    def _arrows(self,q0,q1,places):
        result = set()

        result = result.union(self._arrow(q0,q1,places))
        result = result.union(self._arrow(q1,q0,places))
        result = result.union(self._arrow_loop(q0,places))
        result = result.union(self._arrow_loop(q1,places))
        return result

    def _generate_tikz(self):
        places = dict()
        node_x=0
        node_y=0
        c=""
        for q in self.estados:
            modifiers = self.find_place(q,node_x,node_y,places)
            if q in self.finales:
                modifiers+= ", accepting"
            if q == self.finales:
                modifiers+= ", initial"
            
            c+=r"\node[state" + modifiers + r"] ("+ q + r") {$"+ self.delta._prettify_name(q) + r"$};" + "\n"
            
            node_x = (node_x + 1) % 4
            if node_x == 0:
                node_y += 1
        c += r"\draw "
        arrows = set()
        for q0 in self.estados:
            for q1 in self.estados:
                if not q0 < q1:
                    continue
                arrows = arrows.union(self._arrows(q0,q1,places))
        c += "".join(arrows)
        c += ";"
        self.tikz = Tikz(c,"","")

    def _repr_latex_(self):
        return self.tikz.latex()
    def _repr_svg_(self):
        return self.tikz.svg()


#         c=r"""\node[state] (phi) {$\emptyset$};
# \node[state, accepting, right of=phi] (1) {$\{1\}$};
# \node[state, right of=1] (2) {$\{2\}$};
# \node[state, accepting, right of=2] (12) {$\{1, 2\}$};
# \node[state, below of=phi] (3) {$\{3\}$};
# \node[state, initial, initial where=above, accepting, right of=3] (13) {$\{1, 3\}$};
# \node[state, right of=13] (23) {$\{2, 3\}$};
# \node[state, accepting, right of=23] (123) {$\{1, 2, 3\}$};
# \draw (phi) edge[loop left] node{$a, b$} (phi)
#     (1) edge[above] node{$a$} (phi)
#     (1) edge[above] node{$b$} (2)
#     (2) edge[right] node{$a$} (23)
#     (2) edge[above] node{$b$} (3)
#     (12) edge[above, pos=.3, left=2pt] node{$a, b$} (23)
#     (3) edge[left] node{$b$} (phi)
#     (3) edge[below] node{$a$} (13)
#     (13) edge[loop right] node{$a$} (13)
#     (13) edge[above] node{$b$} (2)
#     (23) edge[bend left, above] node{$a$} (123)
#     (23) edge[bend left, below] node{$b$} (3)
#     (123) edge[loop above] node{$a$} (123)
#     (123) edge[bend left, below] node{$b$} (23);
#"""

if __name__ == "__main__":
    f="""
    f  a  b
    q0 q1 q1
    q1 q0 q2
    q2 q0 q1
    """
    f="""
    f  a  b
    q0 q1 q1
    q1 q0 q2
    q2 q0 q1
    q3 q3 q1
    q4 q0 q3
    q5 q1 q1
    q6 q0 q2
    q7 q0 q1
    q8 q8 q8
    q9 q0 q3
    """
    d = Delta(f)



    a = DFA(d,"q0",{"q2"})

    print(a._repr_latex_().decode())
