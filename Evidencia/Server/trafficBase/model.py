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

        #Obtenemos el diccionario de los datos de los agentes
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []
        self.Destinations_list = []
        self.step_counter = 0
        self.Active_agents = 0
        self.Destination_reached=0
        
        #Obtenemos el mapa de la ciudad
        with open('city_files/Mapa_Final.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)
            self.Nodes=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L","M","N","Ñ","O","P","Q","R","T","U","W","X","Y","Z","&","!","¡"]
            self.destinations_nodes=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l","m","n","ñ","o","p","q","r","t","u","w","x","y","z"]
            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            #Leemos el mapa y creamos los agentes
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    #Se crean los agentes de calle 
                    if col in ["V", "^", ">", "<","="]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col], "straight")
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    #Se ponene los agentes de interseccion como calles con tipo intersección
                    elif col in self.Nodes:
                        
                        agent = Road(f"r_{r*self.width+c}", self, col, "intersection")
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    
                    #Se crean los agentes de semaforo junto con calles debajo para la simulación 3d
                    elif col in ["S", "s"]:
                        agent1 = Road(f"r_{r*self.width+c}", self, "Same", "straight")
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent1, (c, self.height - r - 1))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)
                        
                    #Agentes de edificios
                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    #Agentes de destino
                    elif col == "$":
                        agent = Destination(f"d_{r*self.width+c}", self, "Inner_destination", col)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    
                    #Los destinos de la calle
                    elif col in self.destinations_nodes:
                        agent = Destination(f"d_{r*self.width+c}", self, "Road_destination", col)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.Destinations_list.append(col) 
          
        self.running = True                 
        
    #Sapwneamos 4 carros, uno en cada esquina, si no hay un carro en la esquina    
    def spawn_cars(self):  
        poosibleSpawns = [(0, 0), (0, self.height-1), (self.width-1, 0), (self.width-1, self.height-1)]  
        for i in range(4):
            location =poosibleSpawns[i]
            if len(self.grid.get_cell_list_contents(location))>1:
                continue
            else:
                direction = self.grid.get_cell_list_contents(location)[0].direction  
                agentCar = Car(f"c_{i}", self, self.random.choice(self.Destinations_list), direction)
                self.grid.place_agent(agentCar, location)
                self.schedule.add(agentCar)
                self.Active_agents += 1
        
        
        

    def step(self):
        '''Advance the model by one step.'''
        #Spawneamos carros cada 2 pasos
        if self.step_counter % 7 == 0:
            self.spawn_cars()
        
        self.schedule.step()
        self.step_counter += 1