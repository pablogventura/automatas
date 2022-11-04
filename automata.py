import numpy


class Delta(object):
    def __init__(self,tabla):
        self.tabla = tabla
        self.matriz=numpy.genfromtxt(self.tabla.splitlines(),dtype=str)
        self.estados = list(self.matriz[1:,0])
        self.alfabeto = list(self.matriz[0,1:])

    
    def __call__(self, estado, simbolo):
        return self.matriz[self.estados.index(estado)+1,self.alfabeto.index(simbolo)+1]
        

class DFA(object):
    """
    Clase para definir un automata finito determinista
    """
    def __init__(self,estados, alfabeto, delta, inicial, finales):
        self.estados = estados
        self.alfabeto = alfabeto
        self.delta = delta
        self.inicial = inicial
        self.finales = finales
        assert inicial in estados
        assert finales <= estados

        self.estado_actual = None

    def reset(self):
        self.estado_actual = self.inicial

    def delta_sombrero(self, palabra):
        for a in palabra:
            assert a in self.alfabeto
            self.estado_actual = self.delta[(self.estado_actual,a)]
            assert self.estado_actual in self.estados

f="""
f  a  b
q0 q1 q1
q1 q0 q2
q2 q0 q1
"""

#a = DFA({"q0","q1","q2"},"ab",f,"q0",{"q0","q2"})
r=[]
for l in f.split("\n"):
    if l:
        r.append(l.split())

del r[0][0]


    