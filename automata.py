import numpy
import re
import graphviz
from itertools import chain, combinations
from collections import defaultdict

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return map(set,chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))

def to_unicode(text):
    match = re.match(r"([a-z]+)([0-9]+)", text, re.I)
    if match:
        text,number = match.groups()
        for i,s in enumerate(["₀","₁","₂","₃","₄","₅","₆","₇","₈","₉"]):
            number = number.replace(str(i),s)
        return text + number
    elif text == "epsilon":
        return "ε"
    else:
        return text

def set_to_text(s):
    s = list(sorted(s))
    return "[" + ",".join(s) + "]"

def tex_to_set(text):
    result = text.replace(",",'","')
    result = result.replace("[",'{"')
    result = result.replace("]",'"}')
    return eval(result) - {""}


class Delta(object):
    def __init__(self,tabla):
        self.tabla = tabla
        self.matriz=numpy.genfromtxt(self.tabla.splitlines(),dtype=str)
        self.estados = list(self.matriz[1:,0])
        self.alfabeto = list(self.matriz[0,1:])
        
        if "{" in self.tabla or "}" in self.tabla:
            self.is_dfa=False
            assert self.tabla.count("{") == len(self.estados) * len(self.alfabeto), "Tiene que haber un { por par (estado,simbolo)"
            assert self.tabla.count("}") == len(self.estados) * len(self.alfabeto), "Tiene que haber un } por par (estado,simbolo)"
            self.matriz = self.set_parsing()
        else:
            self.is_dfa=True

    def set_parsing(self):
        print(self.matriz)
        matriz = self.matriz.copy()
        matriz = matriz.astype(object)
        for i in range(1,matriz.shape[0]):
            for j in range(1,matriz.shape[1]):
                matriz[i,j] = set(s.strip() for s in self.matriz[i,j][1:-1].split(",") if s)
        return matriz
    
    def _epsilon_clausure(self, estados):
        nuevos_estados = set()
        while estados != nuevos_estados:
            nuevos_estados = estados.union(self(estados,"epsilon"))
            estados = nuevos_estados
        return estados

    def __call__(self, estado, simbolo):
        if self.is_dfa or type(estado) != set:
            return self.matriz[self.estados.index(estado)+1,self.alfabeto.index(simbolo)+1]
        else:
            assert not self.is_dfa
            result = set()
            for e in estado:
                result = result.union(self.matriz[self.estados.index(e)+1,self.alfabeto.index(simbolo)+1])
            print(result)
            if "epsilon" in self.alfabeto:
                result = self._epsilon_clausure(result)

        return result

    def _latex_name(self, text):
        match = re.match(r"([a-z]+)([0-9]+)", text, re.I)
        if match:
            text,number = match.groups()
            return f"{text}_{{{number}}}"
        else:
            return text

    def _repr_latex_(self):
        result = r"\begin{array}{c|"+ "c" * len(self.alfabeto) + "}\n"
        result += f"\delta_{{{self.matriz[0,0]}}} & " + " & ".join(self.alfabeto) + r"\\\hline" + "\n"
        for q in self.estados:
            result += self._latex_name(q)
            for a in self.alfabeto:
                if self.is_dfa:
                    result += " & " + self._latex_name(self(q,a))
                else:
                    result += " & " + "\{" + ",".join([self._latex_name(s) for s in self(q,a)]) + "\}"
            result += r"\\" + "\n"
        result += r"\end{array}"
        return result

        

class DFA(object):
    """
    Clase para definir un automata finito determinista
    """
    def __init__(self, delta, inicial, finales, estados=None, alfabeto=None):
        if not estados:
            self.estados = set(delta.estados)
        else:
            self.estados = estados
        if not alfabeto:
            self.alfabeto = set(delta.alfabeto)
        else:
            self.alfabeto = alfabeto
        self.delta = delta
        self.inicial = inicial
        self.finales = set(finales)
        assert inicial in self.estados
        assert finales <= self.estados
        self._generate_graph()
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

    def _generate_graph(self):
        graph = graphviz.Digraph(comment='DFA')
        graph.graph_attr['rankdir'] = 'LR'
        graph.node("fake",style="invisible",root="true")
        for q in self.estados:
            if q in self.finales:
                graph.node(q,label=to_unicode(q),shape="doublecircle")
            else:
                graph.node(q,label=to_unicode(q),shape="circle")
        graph.edge("fake",self.inicial,style="bold")
        flechas = defaultdict(list)
        for q in self.estados:
            for a in self.alfabeto:
                flechas[(q,self.delta(q,a))].append(to_unicode(a))
        for q0,q1 in flechas.keys():
            graph.edge(q0, q1, label=", ".join(sorted(flechas[(q0,q1)])))
        self.graph = graph

    #def _repr_latex_(self):
    #    return self.graph.source
    def _repr_svg_(self):
        return self.graph._repr_svg_()
    
    def view(self):
        return self.graph.view()

class NFA(object):
    """
    Clase para definir un automata finito no determinista
    """
    def __init__(self, delta, inicial, finales):
        self.estados = set(delta.estados)
        self.alfabeto = set(delta.alfabeto)
        self.delta = delta
        self.inicial = inicial
        self.finales = set(finales)
        self.estados_actual = None
        assert inicial in self.estados
        assert finales <= self.estados
        self._generate_graph()
        self.reset()

    def reset(self):
        self.estados_actual = {self.inicial}

    def delta_sombrero(self, palabra):
        for a in palabra:
            assert a in self.alfabeto
            print((self.estados_actual,a))
            self.estados_actual = self.delta(self.estados_actual,a)
            assert self.estados_actual <= self.estados, self.estados_actual
    
    def en_lenguaje(self, palabra):
        self.reset()
        self.delta_sombrero(palabra)
        print(self.estados_actual)
        return any(e in self.finales for e in self.estados_actual)

    def _generate_graph(self):
        graph = graphviz.Digraph(comment='NFA')
        graph.graph_attr['rankdir'] = 'LR'
        graph.node("fake",style="invisible",root="true")
        for q in self.estados:
            if q in self.finales:
                graph.node(q,label=to_unicode(q),shape="doublecircle")
            else:
                graph.node(q,label=to_unicode(q),shape="circle")
        graph.edge("fake",self.inicial,style="bold")
        flechas = defaultdict(list)
        for q in self.estados:
            for a in self.alfabeto:
                for q1 in self.delta(q,a):
                    flechas[(q,q1)].append(to_unicode(a))
        for q0,q1 in flechas.keys():
            graph.edge(q0, q1, label=", ".join(sorted(flechas[(q0,q1)])))
        self.graph = graph

    def determinization(self):
        estados = []
        finales = []
        for p in powerset(self.estados):
            clausura = self.delta._epsilon_clausure(set(p))
            if clausura not in estados:
                estados.append(clausura)
        for estado in estados:
            if estado.intersection(self.finales) != set():
                finales.append(estado)
        inicial = set_to_text(self.delta._epsilon_clausure({self.inicial}))
        finales = {set_to_text(f) for f in finales}
        estados = {set_to_text(e) for e in estados}
        def delta_dfa(d,s):
            d=tex_to_set(d)
            return set_to_text(self.delta(d,s))
        
        return DFA(delta_dfa,inicial,finales,estados,self.alfabeto-{"epsilon"})
        

    #def _repr_latex_(self):
    #    return self.graph.source
    def _repr_svg_(self):
        return self.graph._repr_svg_()
    
    def view(self):
        return self.graph.view()


class Regex(object):
    pass

class Vacio(Regex):
    def en_lenguaje(self,v):
        return False
    def __repr__(self) -> str:
        return "∅"

class Epsilon(Regex):
    def en_lenguaje(self,v):
        return not v
    def __repr__(self) -> str:
        return "ε"

class Symbol(Regex):
    def __init__(self, s):
        super().__init__()
        self.symbol = s
    def __repr__(self) -> str:
        return self.symbol

    def en_lenguaje(self, v):
        return v==self.symbol
    
class Union(Regex):
    def __init__(self,re1,re2) -> None:
        super().__init__()
        self.re1 = re1
        self.re2 = re2
    def en_lenguaje(self,v):
        return self.re1.en_lenguaje(v) or self.re2.en_lenguaje(v)
    def __repr__(self) -> str:
        return f"({self.re1} + {self.re2})"

class Concatenacion(Regex):
    def __init__(self,re1,re2) -> None:
        super().__init__()
        self.re1 = re1
        self.re2 = re2
    def en_lenguaje(self,v):
        for i in range(len(v)):
            a,b = v[:i],v[i:]
            if self.re1.en_lenguaje(a) and self.re2.en_lenguaje(b):
                return True
        return False
    def __repr__(self) -> str:
        return f"{self.re1}{self.re2}"

class Clausura(Regex):
    def __init__(self,re) -> None:
        super().__init__()
        self.re = re
    def divide_palabra(self,v,t):
        chunks = list({v[x:x+t] for x in range(0, len(v), t)})
        if len(chunks) <= 1:
            return chunks[0]
        else:
            return None

    def en_lenguaje(self,v):
        if not v:
            return True
        for i in range(1,len(v)+1):
            subpalabra = self.divide_palabra(v,i)
            if subpalabra is not None and self.re.en_lenguaje(subpalabra):
                return True
        return False
    def __repr__(self) -> str:
        return f"{self.re}*"

def l(n,m,R,a):
    """
    Lnm (R) := de qn a qm (sólo estados en R).
    """
    if n == m:
        return Clausura(i(n,R,a))
    else:
        return Concatenacion(Clausura(i(n,R,a)),f(n,m,R,a))

def i(n, R, a):
    """
    In (R) := de qn a sí mismo sin repetirlo (sólo estados en R).
    """
    for t in R:
        for s in R:
            return Concatenacion(Concatenacion(Symbol(a),l(t,s,R-{n},a)),Symbol(b))

def f(n,m,R,a):
    """
    Fnm (R) := de qn a qm sin repetir qn (sólo estados en R).
    """
    pass

def regex(v):
    parser = []
    profundidad = []
    while v:
        a,v = v[0],v[1:]
        if a == "(":
            profundidad.append(temp)
        elif a == ")":
            profundidad.append([])
        else:
            profundidad[-1].append(a)
    return parser



if __name__ == "__main__":
    f="""
    f  a  b
    q0 q1 q1
    q1 q0 q2
    q2 q0 q1
    """
    d = Delta(f)

    a = DFA(d,"q0",{"q2"})

    a.view()

    f = r"""
    f a b c epsilon
    q0 {} {q3} {q1} {}
    q1 {q1,q2} {q3} {} {q0,q2,q3}
    q2 {} {q0,q1,q3} {} {}
    q3 {} {} {} {q0}
    """
    d = Delta(f)
    print(d._repr_latex_())
    a = NFA(d,"q0",{"q1"})

    a.view()
