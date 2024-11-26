from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from trafficBase.agent import *
import json

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N, width, height):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []
        self.Destinations_list = []
        
        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/City_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.Nodes=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
            self.destinations_nodes=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"]
            self.grid = MultiGrid(width, height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<","="]:
                        agent = Road(f"r_{r * width + c}", self, dataDictionary[col], "straight")
                        self.grid.place_agent(agent, (c, height - r - 1))

                    elif col in self.Nodes:
                        
                        agent = Road(f"r_{r * width+c}", self, col, "intersection")
                        self.grid.place_agent(agent, (c, height - r - 1))
                    
                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r * width + c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r * width + c}", self)
                        self.grid.place_agent(agent, (c, height - r - 1))

                    elif col == "$":
                        agent = Destination(f"d_{r * width+c}", self, "Inner_destination", col)
                        self.grid.place_agent(agent, (c, height - r - 1))
                    
                    elif col in self.destinations_nodes:
                        agent = Destination(f"d_{r * width + c}", self, "Road_destination", col)
                        self.grid.place_agent(agent, (c, height - r - 1))
                        self.Destinations_list.append(col)    
                        
        poosibleSpawns = [(0, 0), (0, height-1), (width-1, 0), (width-1, height-1)]
        
        for i in range(1):
            location = poosibleSpawns[0] 
            direction = self.grid.get_cell_list_contents(location)[0].direction  
            agentCar = Car(f"c_{i}", self, self.random.choice(self.Destinations_list), direction)
            self.grid.place_agent(agentCar, location)
            self.schedule.add(agentCar)
        
        self.num_agents = N
        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        
        self.schedule.step()