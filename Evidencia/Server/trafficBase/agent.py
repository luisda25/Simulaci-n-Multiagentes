'''
José Antonio González Martínez A01028517
Luis Daniel Filorio Luna A01028418

Codigo de modelado de agentes para la simulación de tráfico

'''



from mesa import Agent
import json
from collections import deque

class Car(Agent):
    
    def __init__(self, unique_id, model,Destination,vision):
        

        super().__init__(unique_id, model)
        self.Directions= json.load(open("city_files/directions.json"))
        self.vision=vision
        self.state="Straight"
        self.Destination=Destination
        self.Destination_pos=False
        self.posible_moves=[]
        self.map= json.load(open("city_files/Node_directions.json"))
    
    #Función para determinar si la celda va en sentido contrario    
    def can_move(self,celda_actual,Posible_celda):
        if Posible_celda.type=="intersection":
            return True
        else:
            # Obtenemos las posiciones de las dos celdas
            Posible_celda_posicion=Posible_celda.pos
            celda_actual_posicion=celda_actual.pos
            #Leemos la dirección de esa celda 
            Direccion_Posible_celda=self.Directions[Posible_celda.direction]
            
            #calculamos hacia donde nos llevaria la dirección de la celda
            posible_x=Posible_celda_posicion[0]+Direccion_Posible_celda[0]
            posible_y=Posible_celda_posicion[1]+Direccion_Posible_celda[1]
            
            #si nos nos regresa al mismo lugar, no se puede mover
            if posible_x==celda_actual_posicion[0] and posible_y==celda_actual_posicion[1]:
                return False
            else:
                return True
        
    
    
    #Función para encontrar el camino que recorra menos intersecciones 
    def search_path(self,Actual_node):
        queue = deque([(Actual_node, [])])  # Cola con tuplas (nodo actual, camino hasta aquí)
        visited = set()

        while queue:
            current, path = queue.popleft()

            if current in visited:
                continue

            visited.add(current)
            path = path + [current]

            # Si encontramos el nodo objetivo, devolvemos el camino
            if current == self.Destination:
                return self.Transform_path(path)

            # Explorar vecinos
            for neighbor in self.map.get(current, {}):
                if neighbor not in visited:
                    queue.append((neighbor, path))

        return None 
     
     #Función para traducir hacia que dirreccion se encuentra la intersección de interes   
    def Transform_path(self,Nodes_path):
        directions=[]
        for i in range(len(Nodes_path)-1):
            direction=self.map[Nodes_path[i]][Nodes_path[i+1]]
            directions.append(direction)
        return directions
    
    #Función para moverse en una intersección        
    def Intersection(self):
        for place in self.model.grid.get_cell_list_contents(self.pos):
            
            if isinstance(place, Road) and place.type=="intersection":
                #aqui va a ir Calcular a* para saber a que direccion se va a mover
                Nodes_path=self.search_path(place.direction)
                #Asignamos nuestra nueva dirección
                self.vision=Nodes_path[0]
                Actual_pos=self.pos
                Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
                #Movemos el carro a la nueva posición y deckaramos que se mueva derecho en la nueva dirección
                self.model.grid.move_agent(self, Front_pos)
                self.state="Straight"
                break
    
    #Función para revisar las tres celdas que tiene enfrente        
    def check_three(self):
        Actual_pos=self.pos
        Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
        First_pos=None
        Second_pos=None
        
        #Definimos las posiciones de las celdas que tiene enfrente dependiendo la dirección que tienen el carro
        if self.vision=="Left" or self.vision=="Right":
            First_pos=(self.Directions["Up"][0]+Front_pos[0],self.Directions["Up"][1]+Front_pos[1]) 
            Second_pos=(self.Directions["Down"][0]+Front_pos[0],self.Directions["Down"][1]+Front_pos[1])
            
        elif self.vision=="Up" or self.vision=="Down":
            First_pos=(self.Directions["Left"][0]+Front_pos[0],self.Directions["Left"][1]+Front_pos[1]) 
            Second_pos=(self.Directions["Right"][0]+Front_pos[0],self.Directions["Right"][1]+Front_pos[1])

        #Definimos las tres celdas que tiene enfrente
        Front_row=[First_pos,Front_pos,Second_pos]
        self.posible_moves=[]
        
        for pos in Front_row:
            #Si la celda esta fuera del grid, no se considera
            if pos[0]<0 or pos[0]>=self.model.width or pos[1]<0 or pos[1]>=self.model.height:
                continue
            
            for place in self.model.grid.get_cell_list_contents(pos):
                #Si encuentra su destino enfrente de el, cambia su estado a que ha encontrado su destino
                if isinstance(place, Destination) and place.identifier==self.Destination:
                    self.state="In Destination"
                    break
                #Si ve que el espacio está libre de carros, lo agrega a sus posibles movimientos
                elif isinstance(place, Road) and len(self.model.grid.get_cell_list_contents(place.pos))==1:
                    #Si ese espacio no es en sentido contrario
                    if self.can_move(self.model.grid.get_cell_list_contents(Front_pos)[0],place):
                        self.posible_moves.append(place)
                    
        #Analisiamos ahora solamente el espacio de enfrente
        for front in self.model.grid.get_cell_list_contents(Front_pos):
            #Si hay un carro, se detiene
            if isinstance(front, Car):
                self.state="Stop"
                break
            #Analisa el estado del semaforo que tiene enfrente
            elif isinstance(front, Traffic_Light ):
                if self.state!="In Destination":
                    if front.state==True:
                        self.state="Straight"
                    else:
                        self.state="Stop"
    #Función solamente para moverse derecho basado en la dirección actual del carro
    def move_straight(self):
        Actual_pos=self.pos
        Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
        self.model.grid.move_agent(self, Front_pos)
     
    #Función para cambiar de dirección     
    def change_direction(self,next_pos):
        self.model.grid.move_agent(self, next_pos.pos)
        self.vision=next_pos.direction
        
        
    
    #REvisar si la celda de enfrente esta libre
    def check_clear(self):
        Actual_pos=self.pos
        Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
        if len(self.model.grid.get_cell_list_contents(Front_pos))==1:
            self.state="Straight"
        #Si no está libre, revisa si puede moverse a una de las celdas que tiene enfrente
        elif self.posible_moves:
            if len(self.model.grid.get_cell_list_contents(self.posible_moves[0].pos))==1:
                self.model.grid.move_agent(self, self.posible_moves[0].pos)
            
    #Función encargada de moverse a la celda de destino
    def Enter_destination(self):
        Posible_1=None
        Posible_2=None
        
        #Determinamos las celdas laterales dependiendo la dirección del carro
        if self.vision=="Left" or self.vision=="Right":
            Posible_1=(self.Directions["Up"][0]+self.pos[0],self.Directions["Up"][1]+self.pos[1]) 
            Posible_2=(self.Directions["Down"][0]+self.pos[0],self.Directions["Down"][1]+self.pos[1])
        elif self.vision=="Up" or self.vision=="Down":
            Posible_1=(self.Directions["Left"][0]+self.pos[0],self.Directions["Left"][1]+self.pos[1]) 
            Posible_2=(self.Directions["Right"][0]+self.pos[0],self.Directions["Right"][1]+self.pos[1])
            
        sides=[Posible_1,Posible_2]
        #Revisamos donde está el destino del carro
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=False):
            if isinstance(neighbor, Destination) :
                if len(self.model.grid.get_cell_list_contents(neighbor.pos))==1:
                    #Si encuentra el destino dentro de los edificios, se mueve ahi y cambia su estado
                    if (neighbor.identifier=="$" and self.Destination_pos==True) :
                        self.model.grid.move_agent(self, neighbor.pos)
                        self.state="Final"
                        break
                    #Si encuentra el destino de la calle, se mueve ahi y determina que ya solo le falta encontrar
                    #el destino dentro de los edificios
                    elif neighbor.identifier==self.Destination:
                        
                        self.model.grid.move_agent(self, neighbor.pos)
                        self.Destination_pos=True
                        break
    #Función para revisar la celda actual
    def check_actual(self):
        for place in self.model.grid.get_cell_list_contents(self.pos):
            #Si se encuentra en una intersección, se mueve a la intersección
            if isinstance(place, Road) and place.type=="intersection":
                    self.model.grid.move_agent(self, place.pos)
                    self.state="Intersection"
                    break
            
            #Si se encuentra en una calle, revisa si puede moverse derecho o si tiene que cambiar de dirección
            elif isinstance(place, Road) and ((place.direction==self.vision) or (place.direction=="Same")):
                    self.state="Straight"
                    break
                    
            elif isinstance(place, Road) and place.direction!=self.vision:
                if self.can_move(self,place):
                    self.vision=place.direction
                    break
            #Si se encuentra en la celda de destino, cambia su estado a que ha encontrado su destino
            elif isinstance(place, Destination) and place.identifier==self.Destination:
                self.state="In Destination" 
                self.Destination_pos=True
                break   

    #Finalmente revidasmos en que estado se encuentra el carro
    def step(self):
        #Revisamos la celda actual
        self.check_actual()
        #Y las de enfrente
        self.check_three()
        
        #Y dependiendo el estado, toma acciones
        if self.state=="In Destination":
            self.Enter_destination()
            return
        elif self.state=="Straight":
            self.move_straight()
            return
        elif self.state=="Intersection":
            self.Intersection()
            return
        elif self.state=="Stop":
            self.check_clear()
            return
        #Si se encuentra en estado final, se elimina del grid
        elif self.state=="Final":
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            self.model.Active_agents -= 1
            self.model.Destination_reached += 1
            return
        
        
class Traffic_Light(Agent):
    
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        
        
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        #Cambiamos el estado entre avance y detengase
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    #Destinos de los carros
    def __init__(self, unique_id, model,type_,identifier):
        super().__init__(unique_id, model)
        #Identificadores de los destinos
        self.type=type_
        self.identifier=identifier
    def step(self):
        pass

class Obstacle(Agent):
    #Edificios
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    
    def __init__(self, unique_id, model, direction= "Left",tipo="Road"):
        
        super().__init__(unique_id, model)
        #Direcciones de las celdas
        self.direction = direction
        self.type=tipo

    def step(self):
        pass

