from mesa import Agent
import json

class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """

        super().__init__(unique_id, model)
        self.Directions= json.load(open("city_files/directions.json"))
        self.vision="Right"
        self.state="Straight"
        
        
    def can_move(self,celda_actual,Posible_celda):
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
    
    def move_straight(self):
        Actual_pos=self.pos
        Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
        if self.model.grid.get_cell_list_contents(Front_pos):
            for place in self.model.grid.get_cell_list_contents(Front_pos):
                if isinstance(place, Road):
                    if self.can_move(self,place):
                        self.model.grid.move_agent(self, place.pos)
                        break
        
                   
    def check_vision(self):
        Actual_pos=self.pos
        Front_pos=(self.Directions[self.vision][0]+Actual_pos[0],self.Directions[self.vision][1]+Actual_pos[1])
        for place in self.model.grid.get_cell_list_contents(Front_pos):
            if isinstance(place, Traffic_Light ):
                if place.state==True:
                    self.model.grid.move_agent(self, place.pos)
                    self.state="Straight"
                else:
                    self.state="Stop"
        


    def step(self):
        self.check_vision()
        
        if self.state=="Straight":
            self.move_straight()
        elif self.state=="Stop":
            pass
        else:
            self.move()

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
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

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
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
