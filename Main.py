import numpy as np


class Circuit():
    def __init__(self) -> None:
        self.components: list = []
        self.nodes: list = []
        self.branches = []

        self.incidence_matrix = None
        self.lvk_matrix = None
        self.zy_matrix = None
    
    def read(self, txt):
        matrix = txt.split("\n")
        for i in range(len(matrix)):
            matrix[i] = matrix[i].split(" ")
        
            type = ""
            number = 0
            for j in range(len(matrix[i][0])):
            
                if matrix[i][0][j].isalpha():
                    type += matrix[i][0][j]
                else:
                    number = int( matrix[i][0][j:] )

            matrix[i][0] = type
            matrix[i].insert(1, number)

            if len(matrix[i]) != 5:
                print("datos incorrectos")
                exit()
            self.add_component(*matrix[i])


    def calculate(self):
        self.__sort_nodes()
        self.get_incidence_matrix()
        self.get_lvk_matrix()
        self.get_zy_matrix()
        self.get_vector_s()
        self.get_full_matrix()
        self.get_solve()

    def reset(self):
        self.nodes.clear()
        self.branches.clear()
        self.components.clear()
        self.incidence_matrix = None
        self.lvk_matrix = None
        self.zy_matrix = None

    def print_branches(self):
        for branch in self.branches:
            print( "Branch", branch.number, "+"+str(branch.nodes[0]), "->", str(branch.nodes[1])+"-", "|", branch.component   )
    def get_branches_txt(self):
        txt = ""
        for branch in self.branches:
            txt += "Rama " + str(branch.number) + " | +" + str(branch.nodes[0]) + " -> " + str(branch.nodes[1]) + "- | " + str(branch.component) + "\n"
        return txt
    def print_nodes(self):
        for node in self.nodes:
            print(node, [str(x) for x in node.components])
    def get_nodes_txt(self):
        txt = ""
        for node in self.nodes:
            txt += "Nodo " + str(node.number) + " " + str([str(x) for x in node.components]) + "\n"
        return txt
    
    def print_solve(self):
        if self.solve.size <= 0: return 0
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
    
    def __fin(self, n, dato):
        print(f"Componente {dato} no definido") if n==1 else print(f"Nombre {dato} en uso")
        exit()

    def verify(self, type, number):
        tipos = ['V', 'I', 'R', 'VCV', 'ICI', 'VCI', 'ICV']
        if not (type in tipos): self.__fin(1, type)
        if self.find_component(type+str(number)): self.__fin(2, type+str(number))

    def add_component(self, type:str, number:int, value, node1:int, node2:int):
        self.verify(type, number)
        type = str(type)
        number = int(number)
        node1 = self.add_node(int(node1))
        node2 = self.add_node(int(node2))
        branch = self.add_branch(node1, node2)
        if type == 'V':
            newComponent = Vsource(number, float(value), node1, node2, branch)
        elif type == 'I':
            newComponent = Isource(number, float(value), node1, node2, branch)
        elif type == 'R':
            newComponent = Resistor(number, float(value), node1, node2, branch)
        elif type == 'VCV':
            newComponent = VCVsource(number, str(value), node1, node2, branch)
        elif type == 'ICI':
            newComponent = ICIsource(number, str(value), node1, node2, branch)
        elif type == 'VCI':
            newComponent = VCIsource(number, str(value), node1, node2, branch)
        elif type == 'ICV':
            newComponent = ICVsource(number, str(value), node1, node2, branch)
        self.components.append( newComponent)

    def find_component(self, name):
        for component in self.components:
            if component.name == name:
                return component
        return None


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
        return self.incidence_matrix

    def get_lvk_matrix(self):
        incidence = np.transpose(self.incidence_matrix)
        identity = np.eye(len(incidence))
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
    


    def row_z(self, branch):#De corrientes
        row = []
        if branch.component.type == 'R' or branch.component.type == 'I' or branch.component.type == 'ICV':
            for i in range(len(self.branches)):#ubicar en la columna correspondiente a la corriente
                if branch.number == i+1:
                    row.append(1)
                else:
                    row.append(0)
        elif branch.component.type == 'V' or branch.component.type == "VCV":
            row = [0]*len(self.branches)
        
        elif branch.component.type == "ICI":
            a = branch.component.constant
            # encontrar la rama a la que pertenece la referencia
            reference = self.find_component(branch.component.reference)
            for i in range(len(self.branches)):
                if reference.branch.number == i+1:
                    row.append(-a)
                elif branch.number == i +1:
                    row.append(1)
                else:
                    row.append(0)
        elif branch.component.type == "VCI":
            a = branch.component.constant
            reference = self.find_component(branch.component.reference)
            for i in range(len(self.branches)):
                if reference.branch.number == i+1:
                    row.append(-a)
                else:
                    row.append(0)

        return np.array(row)

    def row_y(self, branch): #De tensiones
        row = []
        if branch.component.type == 'R':
            for i in range(len(self.branches)):
                if branch.number == i+1:
                    row.append(-1/ branch.component.resistance )
                else:
                    row.append(0)
        elif branch.component.type == 'V' or branch.component.type == 'VCI':
            for i in range(len(self.branches)):
                if branch.number == i+1:
                    row.append(1)
                else:
                    row.append(0)
        elif branch.component.type == 'I' or branch.component.type == 'ICI':
            row = [0]*len(self.branches)
        
        elif branch.component.type == "VCV":
            a = branch.component.constant
            # encontrar la rama a la que pertenece la referencia
            reference = self.find_component(branch.component.reference)
            for i in range(len(self.branches)):
                if reference.branch.number == i+1:
                    row.append(-a)
                elif branch.number == i +1:
                    row.append(1)
                else:
                    row.append(0)

        elif branch.component.type == "ICV":
            a = branch.component.constant
            reference = self.find_component(branch.component.reference)
            for i in range(len(self.branches)):
                if reference.branch.number == i+1:
                    row.append(-a)
                else:
                    row.append(0)

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
            self.solve = np.array([])
            return 0
        self.solve = np.linalg.solve(self.full_matrix, self.vector_s)
        self.solve = np.round(self.solve, decimals=4)
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
        self.name = None
        self.value = None
        self.tension = None
        self.current = None
        self.resistance = None
        self.function :str = None

    #Conections
        self.node1 = node1
        self.node2 = node2
        node1.add_component(self)
        node2.add_component(self)

        self.nodes = [self.node1, self.node2]

        self.branch = branch
        self.branch.component = self
    
    def get_name(self):
        self.name = self.type + str(self.number)
    
    def decode_function(self): # n*C-n : -2*R.1
        txt = self.function.split("*")
        self.constant = int(txt[0])
        self.reference = txt[1]

    def __str__(self) -> str:
        return str(self.type) + str(self.number) +" "+ str(self.value) +" " + str(self.node1.number)+ " " +str(self.node2.number)
        

class Vsource(Component):
    def __init__(self, number, value: float, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = 'V'
        self.value = value
        self.tension = value
        self.get_name()

       

class VCVsource(Component): #Tensión controlada por tensión
    def __init__(self, number, function, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = 'VCV'
        self.value = function
        self.function = function
        self.get_name()
        self.decode_function()

class VCIsource(Component): #Tensión controlada por intensidad
    def __init__(self, number: int, function, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = "VCI"
        self.value = function
        self.function = function
        self.get_name()
        self.decode_function()
        



class Isource(Component):
    def __init__(self, number, value: float, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = 'I'
        self.value = value
        self.current = value
        self.get_name()


class ICIsource(Component): #Intencidad controlada por Intensidad
    def __init__(self, number, function, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = "ICI"
        self.value = function
        self.function = function
        self.get_name()
        self.decode_function()

class ICVsource(Component): #Intensidad controlada por voltaje
    def __init__(self, number: int, function, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = "ICV"
        self.value = function
        self.function = function
        self.get_name()
        self.decode_function()
 
    
        

class Resistor(Component):
    def __init__(self, number, value: float, node1: Node, node2: Node, branch: Branch) -> None:
        super().__init__(number, node1, node2, branch)
        self.type = 'R'
        self.value = value
        self.resistance = value
        self.get_name()




if __name__ == "__main__":

    def get_data():
        print("""V : Fuente de tensión
I : Fuente de Corriente
R : Resistor
ICI : Corriente controlada por corriente
VCV : Tensión controlada por tensión

Ingrese cada elemento según se indica:
Tipo-numero_identificador valor Nodo1 Nodo2
    Ejemplo: R.1 10 1 0

    Notas:
La polaridad se define por el orden de los nodos, el primer nodo es positivo.
El flujo de corriente tiene dirección del primer al segundo nodo en cada elemnto.
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
I2 -3 2 1
R3 3 1 2
V4 22 3 2
I5 -8 0 1
R6 1 2 0
R7 5 3 0
I8 -25 3 0"""

    texto2 = """I1 1 0 1
VCV2 2*R2 2 0
R1 2 2 1
R2 1 1 0
R3 4 2 0"""

    tres = """V1 2 1 0
R1 1000 1 2
R2 1000 2 0
ICI1 2*R4 2 0
R4 1000 2 0"""

    cuatro = """V1 10 1 0
R1 2 1 2
V2 3 2 0
R2 1 2 3
ICV1 2*R1 0 3"""

    # byInput = get_data()
    # circuit.read(byInput)

    circuit.read(cuatro)

    circuit.calculate()


    circuit.print_branches()

    circuit.print_nodes()

    print("-----------------")

    print("Solve:")
    circuit.print_solve()


    input("Presione Enter para salir")
