import numpy


class Circuit():
    def __init__(self) -> None:
        self.components: list = []
        self.pines: list = []
        self.nodes = []
        self.branches = []

    def add_pin(self, number):
        for i in range(len(self.pines)): #Busca si el pin ya está creado
            if number == self.pines[i].number:
                return self.pines[i]
        
        newPin = Pin(number)
        self.pines.append( newPin)
        return newPin
    
    def add_component(self, type:str, value:float, pin1:int, pin2:int):
        newComponent = Component(type, value, pin1, pin2)
        self.components.append( newComponent)

    def define_nodes(self):
        for pin in self.pines:
            if len(pin.components) >= 3:
                self.__add_node(pin)

    def __add_node(self, pin :object):
        newNode = Node(pin, len(self.nodes )+1)
        self.nodes.append( newNode )
        pin.isNode = True
        pin.define_node(newNode)
    
    def exixting_branch(self, branch):
        for i in range(len(self.branches)):
            if self.branches[i].compare_branches(branch):
                return True
        return False
            

    def define_branches(self):
        if len(self.nodes) == 0:
            pass #Se hace solo una rama que recorre todo el ciruito

        for node in self.nodes:
            components = [] #Guarda componentes de la rama
            for rama in node.components: #rama es un componente que sirve como dirección de branch
                components.append(rama)
                next : Pin = rama.next_pin(node.pin) #next es el siguiente pin
                
                while not next.isNode:
                    nextComponent : Component = next.next_component(components[-1])# Si next no es Nodo, se pide el componente al que está conectado, y luego el otro pin del componente, se repite
                    components.append(nextComponent)

                    next = nextComponent.next_pin(next)
                #Cuando se encuentre otro nodo:
                newBranch = Branch(node, next.node, components, len(self.branches)+1)
                components = []
                if not self.exixting_branch(newBranch):
                    self.branches.append(newBranch)
                

                


circuit = Circuit()

class Pin():
    def __init__(self, number) -> None:
        self.components = []
        self.number = number
        self.isNode = False

    def add_component(self, component):
        self.components.append(component)
    
    def define_node(self, node):
        self.node = node

    def next_component(self, component):
        if component == self.components[0]:
            return self.components[1]
        if component == self.components[1]:
            return self.components[0]
        else:
            return None





class Node():
    def __init__(self, pin, number) -> None:
        self.pin = pin
        pin.define_node(self)
        self.number = number
        self.components = pin.components

    def add_component(self, component):
        self.pin.add_component(component)

    def __str__(self) -> str:
        return "N" + str(self.number)


class Branch():
    def __init__(self, node1, node2, components:list, number:int) -> None:
        self.components = components
        self.number = number
        self.nodes = [node1, node2] #extremos
        #self.current = self.get_current()
        #self.resistance = self.get_resistance()

    def add_component(self, component):
        self.components.append(component)

    def get_current(self):
        pass

    def compare_branches(self, branch):
        s = False
        #s = s or self.nodes[0] == branch.nodes[0] and self.nodes[1] == branch.nodes[1] # Esta no porque existen ramas con el mismo inicio y final pero diferentes componentes
        s = s or self.nodes[0] == branch.nodes[1] and self.nodes[1] == branch.nodes[0]
        return s

    def __str__(self) -> str:
        return "r"+ str(self.number)



    def get_resistance(self):
        comp = self.components
        resis = 0
        for i in range(len(comp)):
            resis += comp[i].resistance
        return resis

class Component():
    def __init__(self, type:str, value:float, pin1:int, pin2:int, circuit=circuit) -> None:
        self.type: str = type
        self.value = value
        self.tension = None
        self.current = None
        self.resistance = None

        if self.type == 'V':
            self.tension = value

        elif self.type == 'I':
            self.current = value
        elif self.type == 'R':
            self.resistance = value

    #Conections
        self.pin1 = circuit.add_pin(pin1)
        self.pin1.add_component(self)

        self.pin2 = circuit.add_pin(pin2)
        self.pin2.add_component(self)

        self.pines = [self.pin1, self.pin2]
    
    def next_pin(self, pin) -> Pin:
        if pin == self.pin1:
            return self.pin2
        if pin == self.pin2:
            return self.pin1
        else:
            return None


    def __str__(self) -> str:
        return str(self.type) + " " + str(self.value) +" " + str(self.pin1.number)+ " " +str(self.pin2.number)
        


def read_circuit(txt, circuit=circuit):
    matrix = txt.split("\n")
    for i in range(len(matrix)):
        matrix[i] = matrix[i].split(" ")
        circuit.add_component(*matrix[i])

#Type, value, pin1, pin2
texto = """I 2 1 0
R 1 1 0
R 2 2 1
R 3 2 0
I 10 2 0"""
read_circuit(texto)

circuit.define_nodes()
print([str(x) for x in circuit.nodes])
print(len(circuit.nodes))
circuit.define_branches()


print("\n".join(str(x)for x in circuit.components))
print([str(x) for x in circuit.branches])
print(len(circuit.branches))

