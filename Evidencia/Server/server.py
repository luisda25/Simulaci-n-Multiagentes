from trafficBase.agent import *
from trafficBase.model import CityModel
from mesa.visualization import CanvasGrid, BarChartModule
from mesa.visualization import ModularServer

def agent_portrayal(agent):
    if agent is None: return
    
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "w": 1,
                 "h": 1
                 }

    if (isinstance(agent, Road)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0
    
    if (isinstance(agent, Destination)):
        if agent.type=="Road_destination":
            portrayal["Color"] = "grey"
            portrayal["Layer"] = 0
        else:
            portrayal["Color"] = "lightgreen"
            portrayal["Layer"] = 0

    if (isinstance(agent, Traffic_Light)):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Obstacle)):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
    
    if (isinstance(agent, Car)):
        portrayal["Color"] = "yellow"
        portrayal["Layer"] = 1
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5

    return portrayal

width = 0
height = 0

with open('city_files/Mapa_Final.txt') as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0])-1
    height = len(lines)

model_params = {"N":5}

print(width, height)
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

server = ModularServer(CityModel, [grid], "Traffic Base", model_params)
                       
server.port = 8522 # The default
server.launch()
