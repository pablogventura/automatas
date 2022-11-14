import numpy
import re
import graphviz

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
    def _generate_tikz(self):
        graph = graphviz.Digraph(comment='DFA')
        graph.graph_attr['rankdir'] = 'LR'
        graph.node("fake",style="invisible",root="true")
        for q in self.estados:
            if q in self.finales:
                graph.node(q,label=self.delta._prettify_name(q),shape="doublecircle")
            else:
                graph.node(q,label=self.delta._prettify_name(q),shape="circle")
        graph.edge("fake",self.inicial,style="bold")
        for q in self.estados:
            for a in self.alfabeto:
                graph.edge(q, self.delta(q,a), label=a)
        self.graph = graph

    def _repr_latex_(self):
        return self.graph.source
    def _repr_svg_(self):
        return self.graph._repr_svg_()


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

    print(a._repr_latex_())
