from mesa import Agent
import json
from collections import deque

class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model,Destination,vision):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """

        super().__init__(unique_id, model)
        self.Directions= json.load(open("city_files/directions.json"))
        self.vision=vision
        self.state="Straight"
        self.Destination=Destination
        self.Destination_pos=None
        self.map= json.load(open("city_files/Node_directions.json"))
        
    def can_move(self,celda_actual,Posible_celda):
        if Posible_celda.type=="intersection":
            return True
        else:
            Posible_celda_posicion=Posible_celda.pos
            celda_actual_posicion=celda_actual.pos
            Direccion_Posible_celda=self.Directions[Posible_celda.direction]
            
            posible_x=Posible_celda_posicion[0]+Direccion_Posible_celda[0]
            posible_y=Posible_celda_posicion[1]+Direccion_Posible_celda[1]
            
            
            if posible_x==celda_actual_posicion[0] and posible_y==celda_actual_posicion[1]:
                return False
            else:
                return True
        
    
    def move(self):
        for place in self.model.grid.iter_neighbors(self.pos, moore=False, include_center=False):
            print(place.pos)
            if isinstance(place, Road):
                print(place.direction)
                if self.can_move(self,place):  
                    self.model.grid.move_agent(self, place.pos)
                    break
    
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
        
    def Transform_path(self,Nodes_path):
        directions=[]
        for i in range(len(Nodes_path)-1):
            direction=self.map[Nodes_path[i]][Nodes_path[i+1]]
            directions.append(direction)
        return directions
            
    def Intersection(self):
        for place in self.model.grid.get_cell_list_contents(self.pos):
            
            if isinstance(place, Road) and place.type=="intersection":
                #aqui va a ir Calcular a* para saber a que direccion se va a mover
                Nodes_path=self.search_path(place.direction)
                print(self.Destination)
                print(Nodes_path)
                self.vision=Nodes_path[0]
                Actual_pos=self.pos
                Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
                self.model.grid.move_agent(self, Front_pos)
                self.state="Straight"
                break
            
    def check_three(self):
        Actual_pos=self.pos
        Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
        First_pos=None
        Second_pos=None
        
        if self.vision=="Left" or self.vision=="Right":
            First_pos=(self.Directions["Up"][0]+Front_pos[0],self.Directions["Up"][1]+Front_pos[1]) 
            Second_pos=(self.Directions["Down"][0]+Front_pos[0],self.Directions["Down"][1]+Front_pos[1])
            
        elif self.vision=="Up" or self.vision=="Down":
            First_pos=(self.Directions["Left"][0]+Front_pos[0],self.Directions["Left"][1]+Front_pos[1]) 
            Second_pos=(self.Directions["Right"][0]+Front_pos[0],self.Directions["Right"][1]+Front_pos[1])


        Front_row=[First_pos,Front_pos,Second_pos]
        print(Front_row)
        for pos in Front_row:
            if pos[0]<0 or pos[0]>=self.model.width or pos[1]<0 or pos[1]>=self.model.height:
                continue
            
            for place in self.model.grid.get_cell_list_contents(pos):
                if isinstance(place, Destination) and place.identifier==self.Destination:
                    
                    self.state="In Destination"
                    break

    def move_straight(self):
        Actual_pos=self.pos
        Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
        if self.model.grid.get_cell_list_contents(Front_pos):
            for place in self.model.grid.get_cell_list_contents(Front_pos):
                
                
                if isinstance(place, Road) and place.type=="intersection":
                    self.model.grid.move_agent(self, place.pos)
                    self.state="Intersection"
                    break
                
                elif isinstance(place, Traffic_Light ) :
                    self.model.grid.move_agent(self, place.pos)
                    break
                
                elif isinstance(place, Road) and (place.direction==self.vision):
                        self.model.grid.move_agent(self, place.pos)
                        
                
                elif isinstance(place, Road) and place.direction!=self.vision:
                    if self.can_move(self,place):
                        self.change_direction(place)
                        break
                    
                elif isinstance(place, Destination) and place.identifier!=self.Destination:
                    self.model.grid.move_agent(self, place.pos)
                    break
        
    def change_direction(self,next_pos):
        self.model.grid.move_agent(self, next_pos.pos)
        self.vision=next_pos.direction
        
        
    def check_vision(self):
        Actual_pos=self.pos
        Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
        
        
        for place in self.model.grid.get_cell_list_contents(Front_pos):
            if isinstance(place, Traffic_Light ):
                if place.state==True:
                    self.state="Straight"
                else:
                    self.state="Stop"
            elif isinstance(place, Car):
                self.state="Stop"

    def check_clear(self):
        Actual_pos=self.pos
        Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
        if len(self.model.grid.get_cell_list_contents(Front_pos))==1:
            self.state="Straight"

    def Enter_destination(self):
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True, include_center=False):
            if isinstance(neighbor, Destination):
                if neighbor.identifier=="$":
                    self.model.grid.move_agent(self, neighbor.pos)
                    self.state="Final"
                    break
                
                elif neighbor.identifier==self.Destination:
                    
                    self.model.grid.move_agent(self, neighbor.pos)
                    break

    def step(self):
        self.check_three()
        if self.state!="In Destination":
            self.check_vision()
        
        if self.state=="In Destination":
            self.Enter_destination()
        elif self.state=="Straight":
            self.move_straight()
            return
        elif self.state=="Intersection":
            self.Intersection()
            return
        elif self.state=="Stop":
            self.check_clear()
            return
        elif self.state=="Final":
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            return
        elif self.state=="In Destination":
            self.Enter_destination()
            return
        else:
            self.move()
            return
class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model,type_,identifier):
        super().__init__(unique_id, model)

        self.type=type_
        self.identifier=identifier
    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left",tipo="Road"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction
        self.type=tipo

    def step(self):
        pass

