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
        self.nodes.append( Node(pin, len(self.nodes +1))  )
        pin.isNode = True

    def define_branches(self):
        if len(self.nodes) == 0:
            pass #Se hace solo una rama que recorre todo el ciruito

        for node in self.nodes:
            for conection in node.components:
                conection.pin1


circuit = Circuit()

class Pin():
    def __init__(self, number, circuit=circuit) -> None:
        self.components = []
        self.number = number
        self.isNode = False

    def add_component(self, component):
        self.components.append(component)





class Node():
    def __init__(self, pin, number) -> None:
        self.pin = pin
        self.number = number
        self.components = pin.components

    def add_component(self, component):
        self.pin.add_component(component)




class Branch():
    def __init__(self) -> None:
        self.components = []
        self.nodes = [] #extremos
        #self.current = self.get_current()
        #self.resistance = self.get_resistance()

    def add_component(self, component):
        self.components.append(component)

    def get_current(self):
        pass

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
    
    def get_other_pin(self, pin):
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
texto = """V 12 1 0
R 1 1 2
R 2 2 0"""
read_circuit(texto)


print("\n".join(str(x)for x in circuit.components))


