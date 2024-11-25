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
    def __init__(self, N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []
        self.Destinations_list = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/City_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<","="]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col], "straight")
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["L", "l", "R", "r"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col], "intersection")
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    
                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.Destinations_list.append((c, self.height - r - 1))
                        
        poosibleSpawns = [(0, 0), (0, self.height-1), (self.width-1, 0), (self.width-1, self.height-1)]
        
        for i in range(4):
            location = self.random.choice(poosibleSpawns) 
            direction = self.grid.get_cell_list_contents(location)[0].direction  
            agentCar = Car(f"c_{i}", self, self.random.choice(self.Destinations_list), direction)
            self.grid.place_agent(agentCar, location)
            self.schedule.add(agentCar)
        
        self.num_agents = N
        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        
        self.schedule.step()