import numpy as np


class Circuit():
    def __init__(self) -> None:
        self.components: list = []
        self.nodes: list = []
        self.branches = []

    def print_branches(self):
        for branch in self.branches:
            print( "Branch", branch.number, [str(x) for x in branch.nodes]   )
    
    def print_nodes(self):
        for node in self.nodes:
            print(node, [str(x) for x in node.components])

    def add_node(self, number):
        for i in range(len(self.nodes)): #Busca si el nodo ya está creado
            if number == self.nodes[i].number:
                return self.nodes[i]
        
        newNode = Node(number)
        self.nodes.append( newNode)
        return newNode
    
    def add_branch(self, node1, node2):
        newBranch = Branch(node1, node2, len(self.branches)+1)
        self.branches.append(newBranch)
        return newBranch
    
    def add_component(self, type:str, value:float, node1:int, node2:int):
        type = str(type)
        value = float(value)
        node1 = self.add_node(int(node1))
        node2 = self.add_node(int(node2))
        branch = self.add_branch(node1, node2)
        if type == 'V':
            newComponent = Vsourse(value, node1, node2, branch)
        elif type == 'I':
            newComponent = Csourse(value, node1, node2, branch)
        elif type == 'R':
            newComponent = Resistor(value, node1, node2, branch)
        self.components.append( newComponent)


                
    def get_incidence_matrix(self):
        pass

    def row_incidence(self, node):
        row = []
        for branch in self.branches:
            row.append(node.conected_branch(branch))
            
        return np.array(row)


circuit = Circuit()

class Node():
    def __init__(self, number) -> None:
        self.components = []
        self.number = number
        self.branches = []

    def add_component(self, component):
        self.components.append(component)
    
    def next_component(self, component): #si solo tiene dos componentes
        if len(self.components) != 2:
            return None
        if component == self.components[0]:
            return self.components[1]
        if component == self.components[1]:
            return self.components[0]
        else:
            return None
    
    def add_branch(self, branch):
        self.branches.append(branch)

    def conected_branch(self, branch): #Retorna si una branch está o no conectada al nodo y su sentido. -1 saliendo, 1 entrando, 0 no conectada

        for conected in self.branches:
            if conected == branch:#Buscar si la rama está conectada
                if branch.nodes[0] == self: #Si coincide con el primer nodo es positivo
                    return 1
                else:
                    return -1
        return 0
                
    def __str__(self) -> str:
        return "N" + str(self.number)




class Branch():
    def __init__(self, node1, node2, number:int) -> None:
        self.component = None
        self.number = number
        self.nodes = [node1, node2] #[0]=inicio, [1]=final
        self.ends = (node1.number, node2.number)
        node1.add_branch(self)
        node2.add_branch(self)


    def add_component(self, component):
        self.components = component

    def __str__(self) -> str:
        return "r"+ str(self.number)



    def get_resistance(self):
        comp = self.components
        resis = 0
        for i in range(len(comp)):
            resis += comp[i].resistance
        return resis

class Component():
    def __init__(self, node1:Node, node2:Node, branch:Branch) -> None:
        self.type: str = None
        self.value = None
        self.tension = None
        self.current = None
        self.resistance = None

    #Conections
        self.node1 = node1
        self.node2 = node2

        self.nodes = [self.node1, self.node2]

        self.branch = branch
        self.branch.component = self
    
    def next_node(self, node) -> Node:
        if node == self.node1:
            return self.node2
        if node == self.node2:
            return self.node1
        else:
            return None

    def __str__(self) -> str:
        return str(self.type) + " " + str(self.value) +" " + str(self.node1.number)+ " " +str(self.node2.number)
        

class Vsourse(Component):
    def __init__(self, value: float, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(node1, node2, branch)
        self.type = 'V'
        self.value = value
        self.tension = value

        node1.add_component(self)
        node2.add_component(self)



class Csourse(Component):
    def __init__(self, value: float, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(node1, node2, branch)
        self.type = 'I'
        self.value = value
        self.current = value

        node1.add_component(self)
        node2.add_component(self)    


class Resistor(Component):
    def __init__(self, value: float, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(node1, node2, branch)
        self.type = 'R'
        self.value = value
        self.resistance = value

        node1.add_component(self)
        node2.add_component(self)



def read_circuit(txt, circuit=circuit):
    matrix = txt.split("\n")
    for i in range(len(matrix)):
        matrix[i] = matrix[i].split(" ")
        circuit.add_component(*matrix[i])

#Type, value, pin1+, pin2-
texto = """V 2 1 0
R 1 1 2
R 2 2 0
I 10 2 0"""
read_circuit(texto)




circuit.print_branches()

circuit.print_nodes()

print(circuit.nodes[0])

print(circuit.row_incidence(circuit.nodes[2]))