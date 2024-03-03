import numpy as np


class Circuit():
    def __init__(self) -> None:
        self.components: list = []
        self.nodes: list = []
        self.branches = []

        self.incidence_matrix = None
        self.lvk_matrix = None
        self.zy_matrix = None
    
    def calculate(self):
        self.__sort_nodes()
        self.get_incidence_matrix()
        self.get_lvk_matrix()
        self.get_zy_matrix()
        self.get_vector_s()
        self.get_full_matrix()
        self.get_solve()

    def print_branches(self):
        for branch in self.branches:
            print( "Branch", branch.number, [str(x) for x in branch.nodes], branch.component   )
    
    def print_nodes(self):
        for node in self.nodes:
            print(node, [str(x) for x in node.components])
    
    def print_solve(self):
        if self.solve == []: return 0
        index = 0
        print("\n Current in each branch")
        for i in range(len(self.branches)):
            print(self.solve[index], "Ampers", str(self.branches[i]))
            index += 1
        print("\n Tension in each branch")
        for i in range(len(self.branches)):
            print(self.solve[index], "Volts", str(self.branches[i]))
            index += 1
        print("\n Tension in each node")
        for i in range(len(self.nodes)-1):
            print(self.solve[index], "Volts", str(self.nodes[i]))
            index += 1

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
    
    def add_component(self, typeNumber:str, value:float, node1:int, node2:int):
        type = str(typeNumber[0])
        number = int(typeNumber[1])
        value = float(value)
        node1 = self.add_node(int(node1))
        node2 = self.add_node(int(node2))
        branch = self.add_branch(node1, node2)
        if type == 'V':
            newComponent = Vsource(number, value, node1, node2, branch)
        elif type == 'I':
            newComponent = Csource(number, value, node1, node2, branch)
        elif type == 'R':
            newComponent = Resistor(number, value, node1, node2, branch)
        self.components.append( newComponent)

    def __sort_nodes(self):
        sort = []
        node_0 = 0
        for current in range(1, len(self.nodes)):
            for i in range(len(self.nodes)):
                if self.nodes[i].number == current:
                    sort.append(self.nodes[i])
                elif self.nodes[i].number == 0:
                    node_0 = i
        sort.append(self.nodes[node_0])
        self.nodes = sort


    
    def get_incidence_matrix(self):
        matrix =[]
        for node in self.nodes:
            if node.number != 0:
                matrix.append(self.row_incidence(node))
        self.incidence_matrix = np.array(matrix)
        print(self.incidence_matrix)
        return self.incidence_matrix

    def get_lvk_matrix(self):
        incidence = np.transpose(self.incidence_matrix)
        identity = np.eye(len(incidence))
        print(identity)
        print(incidence)
        self.lvk_matrix = (np.hstack([identity, incidence]) if len(identity) !=0 or len(incidence)!=0 else []) 
        return self.lvk_matrix

    def get_zy_matrix(self):
        matrixZ = []
        matrixY = []
        for branch in self.branches:
            matrixZ.append(self.row_z(branch))
            matrixY.append(self.row_y(branch))
        self.zy_matrix = np.hstack([np.array(matrixZ), np.array(matrixY)])
        return self.zy_matrix
    
    def row_y(self, branch):
        row = []
        if branch.component.type == 'R':
            for i in range(len(self.branches)):
                if branch.number == i+1:
                    row.append(-1/branch.component.resistance)
                else:
                    row.append(0)
        elif branch.component.type == 'V':
            for i in range(len(self.branches)):
                if branch.number == i+1:
                    row.append(1)
                else:
                    row.append(0)
        elif branch.component.type == 'I':
            row = [0]*len(self.branches)
        return np.array(row)


    def row_z(self, branch):
        row = []
        if branch.component.type == 'R' or branch.component.type == 'I':
            for i in range(len(self.branches)):
                if branch.number == i+1:
                    row.append(1)
                else:
                    row.append(0)
        elif branch.component.type == 'V':
            row = [0]*len(self.branches)
        return np.array(row)


    def row_incidence(self, node):
        row = []
        for branch in self.branches:
            row.append(node.conected_branch(branch))
        
        return np.array(row)

    def get_vector_s(self):
        currents = np.zeros((len(self.branches), 1))
        tensions = np.zeros((len(self.nodes)-1, 1))
        sources = self.get_source_vector()
        self.vector_s = np.vstack([currents, tensions, sources])
        return self.vector_s

    def get_source_vector(self):
        column = []
        for branch in self.branches:
            if branch.component.type == 'V' or branch.component.type == 'I':
                column.append([branch.component.value])
            else:
                column.append([0])
        self.source_vector = np.array(column)
        return self.source_vector

    def get_full_matrix(self):
        incidence = np.hstack([self.incidence_matrix, np.zeros((len(self.incidence_matrix), len(self.branches)+len(self.nodes)-1))])
        lvk = np.hstack([np.zeros((len(self.lvk_matrix), len(self.branches))), self.lvk_matrix])
        zy = np.hstack([self.zy_matrix, np.zeros((len(self.zy_matrix), len(self.nodes)-1))  ])
        self.full_matrix = np.vstack([incidence, lvk, zy])
        return self.full_matrix
    
    def get_solve(self):
        if np.linalg.det(self.full_matrix) == 0:
            print("No hay solución")
            self.solve = []
            return 0
        self.solve = np.linalg.solve(self.full_matrix, self.vector_s)
        self.solve = np.round(self.solve, decimals=2)
        return self.solve

circuit = Circuit()

class Node():
    def __init__(self, number) -> None:
        self.components = []
        self.number = number
        self.branches = []

        self.tension = (0 if number == 0 else None)

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
                if branch.nodes[0] == self: #Si coincide con el primer nodo este es el inicio
                    return -1
                else: #final. Considerando que corriente va del primer nodo al segundo
                    return 1
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


    def __str__(self) -> str:
        return "B"+ str(self.number)


class Component():
    def __init__(self, number:int, node1:Node, node2:Node, branch:Branch) -> None:
        self.type: str = None
        self.number :int= number
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

    def __str__(self) -> str:
        return str(self.type) + "-"+str(self.number) +" "+ str(self.value) +" " + str(self.node1.number)+ " " +str(self.node2.number)
        

class Vsource(Component):
    def __init__(self, number, value: float, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = 'V'
        self.value = value
        self.tension = value

        node1.add_component(self)
        node2.add_component(self)

class VCVsource(Component): #Voltaje Control Voltage Source
    def __init__(self, number, function, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = 'VCV'
        self.value = function
        



class Csource(Component):
    def __init__(self, number, value: float, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = 'I'
        self.value = value
        self.current = value

        node1.add_component(self)
        node2.add_component(self)    


class Resistor(Component):
    def __init__(self, number, value: float, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = 'R'
        self.value = value
        self.resistance = value

        node1.add_component(self)
        node2.add_component(self)



def read_circuit(txt, circuit=circuit):
    matrix = txt.split("\n")
    for i in range(len(matrix)):
        matrix[i] = matrix[i].split(" ")
        matrix[i][0] = matrix[i][0].split("-")
        if len(matrix[i]) != 4:
            print("datos incorrectos")
            exit()
        circuit.add_component(*matrix[i])

def get_data():
    print("""V : Fuente de tensión
I : Fuente de Corriente
R : Resistor

Ingrese cada elemento según se indica:
Tipo-numero_identificador valor Nodo1 Nodo2
    Ejemplo: R-1 10 1 0

    Notas:
La polaridad se define por el orden de los terminales, el terminal1 es positivo.
El flujo de corriente tiene dirección del terminal2 al terminal1 en cada elemnto.
El nodo de referencia será aquel con número 0.
Para finalziar el envío de datos, ingresar una cadena vacía.
""")
    elements = []
    adding = "0"
    i=1
    while adding != '':
        adding = input(f"Ingrese elemento {i}: ")
        if adding != '':
            elements.append(adding)
        
        i+=1
    txt = elements[0]
    for i in range(1, len(elements)):
        txt += "\n" + elements[i]

    return txt


#Type-number value, pin1+, pin2-
        

texto = """R-1 4 1 3
I-2 -3 2 1
R-3 3 1 2
V-4 22 3 2
I-5 -8 0 1
R-6 1 2 0
R-7 5 3 0
I-8 -25 3 0"""

texto2 = """I-1 1 1 0
I-2 2 0 2
R-1 2 2 1
R-2 1 1 0
R-3 4 2 0"""
texto3 = """V-1 10 0 1
V-2 10 1 0"""

read_circuit(texto3)

circuit.calculate()


circuit.print_branches()

circuit.print_nodes()

print("-----------------")

#print("Incidence")
#print(circuit.incidence_matrix)

# print("lvk")
# print(circuit.lvk_matrix)
# print("zy")
# print(circuit.zy_matrix)
# print("Solve:")

circuit.print_solve()

input("Presione Enter para salir")
