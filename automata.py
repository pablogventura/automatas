import numpy
from  IPython.display import Math


class Delta(object):
    def __init__(self,tabla):
        self.tabla = tabla
        self.matriz=numpy.genfromtxt(self.tabla.splitlines(),dtype=str)
        self.estados = list(self.matriz[1:,0])
        self.alfabeto = list(self.matriz[0,1:])

    
    def __call__(self, estado, simbolo):
        return self.matriz[self.estados.index(estado)+1,self.alfabeto.index(simbolo)+1]
    
    def __repr__(self):
        result = ""
        for q in self.estados:
            for a in self.alfabeto:
                pass
    
    def _repr_svg_(self):
        return r"""<svg height="100" width="100">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
  Sorry, your browser does not support inline SVG.  
</svg>"""

        

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

f="""
f  a  b
q0 q1 q1
q1 q0 q2
q2 q0 q1
"""

a = DFA(Delta(f),"q0",{"q0","q2"})

    