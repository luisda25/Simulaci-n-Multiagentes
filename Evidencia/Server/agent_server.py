# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with webGL.
# Octavio Navarro. 2024

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from trafficBase.model import CityModel
from trafficBase.agent import Car, Traffic_Light, Destination, Obstacle, Road

# Size of the board:
number_cars = 10
cityModel = None
currentStep = 0

# This application will be used to interact with WebGL
app = Flask("Traffic Server")
cors = CORS(app, origins=['http://localhost'])

# This route will be used to send the parameters of the simulation to the server.
# The servers expects a POST request with the parameters in a.json.
@app.route('/init', methods=['POST'])
@cross_origin()
def initModel():
    global currentStep, cityModel, number_cars, width, height

    if request.method == 'POST':
        try:

            number_cars = int(request.json.get('NAgents'))
            currentStep = 0

            print(request.json)
            print(f"Model parameters:{number_cars}")

            # Create the model using the parameters sent by the application
            cityModel = CityModel(number_cars)

            # Return a message to saying that the model was created successfully
            return jsonify({"message":"Parameters recieved, model initiated."})

        except Exception as e:
            print(e)
            return jsonify({"message":"Erorr initializing the model"}), 500

# This route will be used to get the positions of the agents
@app.route('/getAgents', methods=['GET'])
@cross_origin()
def getAgents():
    global cityModel

    if cityModel is None:
        return jsonify({"message":"Model not initialized."}), 500
    
    if request.method == 'GET':
        # Get the positions of the agents and return them to WebGL in JSON.json.t.
        # Note that the positions are sent as a list of dictionaries, where each dictionary has the id and position of an agent.
        # The y coordinate is set to 1, since the agents are in a 3D world. The z coordinate corresponds to the row (y coordinate) of the grid in mesa.
        try:
            agentPositions = [
                {"id": str(a.unique_id), "x": a.pos[0], "y":1, "z":a.pos[1]}
                for a in cityModel.schedule.agents()
                if isinstance(a, Car)
            ]

            return jsonify({'positions':agentPositions})
        except Exception as e:
            print(e)
            return jsonify({"message":"Error with the agent positions"}), 500

# This route will be used to get the positions of the obstacles
@app.route('/getObstacles', methods=['GET'])
@cross_origin()
def getObstacles():
    global cityModel

    if cityModel is None:
        return jsonify({"message":"Model not initialized."}), 500
    
    if request.method == 'GET':
        try:
        # Get the positions of the obstacles and return them to WebGL in JSON.json.t.
        # Same as before, the positions are sent as a list of dictionaries, where each dictionary has the id and position of an obstacle.
            carPositions = [
                {"id": str(a.unique_id), "x": x, "y":1, "z":z}
                for cell, (x, z) in cityModel.grid.coord_iter()
                for a in cell if isinstance(a, Obstacle)
            ]

            return jsonify({'positions':carPositions})
        except Exception as e:
            print(e)
            return jsonify({"message":"Error with obstacle positions"}), 500

# This route will be used to update the model
@app.route('/update', methods=['GET'])
@cross_origin()
def updateModel():
    global currentStep, cityModel
    if request.method == 'GET':
        try:
        # Update the model and return a message to WebGL saying that the model was updated successfully
            cityModel.step()
            currentStep += 1
            return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})
        except Exception as e:
            print(e)
            return jsonify({"message":"Error during step."}), 500


if __name__=='__main__':
    # Run the flask server in port 8585
    app.run(host="localhost", port=8585, debug=True)
