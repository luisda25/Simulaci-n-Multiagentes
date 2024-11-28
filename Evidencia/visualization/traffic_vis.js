/*
* City Traffic Visualization from mesa using WebGL
* Authors: Luis Daniel Filorio Luna, Jose Antonio Gonzalez Martinez
* 28/11/2024
*/

'use strict';

import * as twgl from 'twgl.js';
import GUI from 'lil-gui';
import obj from '../visualization/coche.obj?raw'; // import the obj file
import { loadObj } from '../visualization/OBJ_reader.js'; // import the loadObj function
import { v3 } from '../visualization/libs/3D_lib';

// Import shader codes, using GLSL 3.00
import vsGLSL from '../visualization/shaders/vs_phong.glsl?raw';
import fsGLSL from '../visualization/shaders/fs_phong.glsl?raw';

// Define the settings for the visualization
const settings = {
  
  cameraPosition: {
      x: 0,
      y: 0,
      z: 10,
  },
  lightPosition: {
      x: 10,
      y: 10,
      z: 10,
  },
  ambientColor: [0.5, 0.5, 0.5, 1.0],
  diffuseColor: [0.5, 0.5, 0.5, 1.0],
  specularColor: [0.5, 0.5, 0.5, 1.0],
};

// Define the Object3D class to represent 3D objects
class Object3D {
  constructor(id, position=[0,0,0], rotation=[0,0,0], scale=[1,1,1], color = [1,1,1,1], shininess = 100){
    this.id = id;
    this.position = position;
    this.rotation = rotation;
    this.scale = scale;
    this.color = color;
    this.shininess = shininess;
    this.matrix = twgl.m4.create();
  }
}

// Define the Car class to represent agents
class Car {
  constructor(id, position=[0,0,0], rotation=[0,0,0], scale=[0.0000001, 0.0000001 , 0.000001], color = [1,1,1,1], shininess = 100){
    this.id = id;
    this.position = position;
    this.rotation = rotation;
    this.scale = scale;
    this.color = color;
    this.shininess = shininess;
    this.matrix = twgl.m4.create();
  }
}

// Define the agent server URI
const agent_server_uri = "http://localhost:8585/";

// Initialize arrays to store agents and obstacles
const cars = [];   
const obstacles = [];
const traffic_lights = [];
const destinations = [];
const roads = [];

// Initialize WebGL-related variables
let gl, 
  programInfo, 
  carsArrays,
  obstacleArrays,
  roadsArrays,
  trafficLightsArrays,
  destinationsArrays,
  carsBufferInfo, 
  obstaclesBufferInfo,
  trafficLightsBufferInfo,
  destinationsBufferInfo,
  roadsBufferInfo, 
  carsVao, 
  obstaclesVao,
  trafficLifghtsVao,
  destinationsVao,
  roadsVao
  ;

// Define the camera position
let cameraPosition = {x:0, y:40, z:0.01};

// Initialize the frame count
let frameCount = 0;

// Define the data object
const data = {
  NAgents: 1
};

// Main function to initialize and run the application
async function main() {
  const canvas = document.querySelector('canvas');
  gl = canvas.getContext('webgl2');

  // Create the program information using the vertex and fragment shaders
  programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

  // Generate object arrays
  carsArrays = loadObj(obj); // Loads arrays from the obj file
  console.log(carsArrays);
  obstacleArrays = generateData(1);
  trafficLightsArrays = generateData(1);
  destinationsArrays = generateData(1);
  roadsArrays = generateData(1);

  // Create buffer information from the objects data
  carsBufferInfo = twgl.createBufferInfoFromArrays(gl, carsArrays);
  obstaclesBufferInfo = twgl.createBufferInfoFromArrays(gl, obstacleArrays);
  trafficLightsBufferInfo = twgl.createBufferInfoFromArrays(gl, trafficLightsArrays);
  destinationsBufferInfo = twgl.createBufferInfoFromArrays(gl, destinationsArrays);
  roadsBufferInfo = twgl.createBufferInfoFromArrays(gl, roadsArrays);

  // Create vertex array objects (VAOs) from the buffer information
  carsVao = twgl.createVAOFromBufferInfo(gl, programInfo, carsBufferInfo);
  obstaclesVao = twgl.createVAOFromBufferInfo(gl, programInfo, obstaclesBufferInfo);
  trafficLifghtsVao = twgl.createVAOFromBufferInfo(gl, programInfo, trafficLightsBufferInfo);
  destinationsVao = twgl.createVAOFromBufferInfo(gl, programInfo, destinationsBufferInfo);
  roadsVao = twgl.createVAOFromBufferInfo(gl, programInfo, roadsBufferInfo);

  // Set up the user interface
  setupUI();

  // Initialize the agents model
  await initAgentsModel();

  // Get the agents and obstacles
  await getAgents();
  await getObstacles();
  await getTrafficLights();
  await getRoads();
  await getDestinations();

  // Draw the scene
  await drawScene();
}

/*
 * Initializes the agents model by sending a POST request to the agent server.
 */
async function initAgentsModel() {
  try {
    // Send a POST request to the agent server to initialize the model
    let response = await fetch(agent_server_uri + "init", {
      method: 'POST', 
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify(data)
    })

    // Check if the response was successful
    if(response.ok){
      // Parse the response as JSON and log the message
      let result = await response.json()
      console.log(result.message)
    }
      
  } catch (error) {
    // Log any errors that occur during the request
    console.log(error)    
  }
}

/*
 * Retrieves the current positions of all car agents from the server.
 */
async function getAgents() {
  try {
    // Send a GET request to the agent server to retrieve the agent positions
    let response = await fetch(agent_server_uri + "getAgents") 
    let rotation = [0, 0, 0];

    // Check if the response was successful
    if(response.ok){
      // Parse the response as JSON
      let result = await response.json()

      // Log the agent positions
      console.log(result.positions)

      // Clear the existing agents array
      cars.length = 0;

      // Create new agents and add them to the agents array
      for (const agent of result.positions) {
        if (agent.vision == "Up") {
          rotation = [0, 0, 0];
        } else if (agent.vision == "Down") {
          rotation = [0, Math.PI, 0];
        } else if (agent.vision == "Left") {
          rotation = [0, -Math.PI / 2, 0];
        } else if (agent.vision == "Right") {
          rotation = [0, Math.PI / 2, 0];
        } else {
          rotation = [0, 0, 0];
        }

        const newAgent = new Car(
          agent.id, 
          [agent.x, agent.y, agent.z],
          rotation,
          [0.12, 0.12 , 0.09],
          [0.5, 0, 0.5, 1],
        )
        cars.push(newAgent)
      }
      // Log the agents array
      console.log("Agents:", cars)
    }

  } catch (error) {
    // Log any errors that occur during the request
    console.log(error) 
  }
}

/*
 * Retrieves the current positions of all obstacles from the agent server.
 */
async function getObstacles() {
  try {
    // Send a GET request to the agent server to retrieve the obstacle positions
    let response = await fetch(agent_server_uri + "getObstacles") 

    // Check if the response was successful
    if(response.ok){
      // Parse the response as JSON
      let result = await response.json()

      // Create new obstacles and add them to the obstacles array
      for (const obstacle of result.positions) {
        const newObstacle = new Object3D(obstacle.id, [obstacle.x, obstacle.y, obstacle.z], [0,0,0], [1,1,1], [0.0, 0.5, 0.8, 1.0])
        obstacles.push(newObstacle)
      }
      // Log the obstacles array
      console.log("Obstacles:", obstacles)
    }

  } catch (error) {
    // Log any errors that occur during the request
    console.log(error) 
  }
}

async function getTrafficLights() {
  try {
    // Send a GET request to the agent server to retrieve the traffic light positions
    let response = await fetch(agent_server_uri + "getTrafficLights");

    // Check if the response was successful
    if (response.ok) {
      // Parse the response as JSON
      let result = await response.json();

      // Log the traffic light positions
      console.log(result.positions);

      // Check if the trafficLights array is empty
      if (traffic_lights.length == 0) {
        // Create new traffic lights and add them to the trafficLights array
        for (const i of result.positions) {
          const color = i.state ? [0, 1, 0, 1] : [1, 0, 0, 1]; // Green if true, red if false
          const newLight = new Object3D(
            i.id,
            [i.x, i.y, i.z],
            [0, 0, 0],
            [0.35, 0.35, 0.35],
            color,
          );
          traffic_lights.push(newLight);
        }
        // Log the traffic lights array
        console.log("Traffic Lights:", traffic_lights);

      } else {
        // Update the positions and states of existing traffic lights
        for (const i of result.positions) {
          const color = i.state ? [0, 1, 0, 1] : [1, 0, 0, 1]; // Green if true, red if false
          const currentTrafficLight = traffic_lights.find(
            (object3d) => object3d.id == i.id,
          );

          // Check if the traffic light exists in the trafficLights array
          if (currentTrafficLight != undefined) {
            // Update the traffic light's state and color
            currentTrafficLight.state = i.state;
            currentTrafficLight.color = color; // Green if true, red if false
          }
        }
      }
    }
  } catch (error) {
    // Log any errors that occur during the request
    console.log(error);
  }
}

async function getRoads() {
  try {
    let response = await fetch(agent_server_uri + "getRoads");

    if (response.ok) {
      let result = await response.json();

      for (const r of result.positions) {
        const newRoad = new Object3D(
          r.id, 
          [r.x, r.y, r.z],
          [0, 0, 0],
          [1, 1, 1],
          [0.5, 0.5, 0.5, 1],
        );
        roads.push(newRoad);
      }
      console.log("Roads:", roads);
    }
  } catch (error) {
    console.log(error);
  }
}

async function getDestinations() {
  try {
    let response = await fetch(agent_server_uri + "getDestinations");

    if (response.ok) {
      let result = await response.json();

      for (const d of result.positions) {
        if (d.type == "Inner_destination") {
          const newDestination = new Object3D(
            d.id,
            [d.x, d.y, d.z],
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 1, 1],
          );
          destinations.push(newDestination);
        } else {
          const newDestination = new Object3D(
            d.id,
            [d.x, d.y, d.z],
            [0, 0, 0],
            [1, 1, 1],
            [0.5, 0.5, 0.5, 1],
          );
          destinations.push(newDestination);
        }
      }
      console.log("Destinations:", destinations);
    }
  } catch (error) {
    console.log(error);
  }
}
/*
 * Updates the agent positions by sending a request to the agent server.
 */
async function update() {
  try {
    // Send a request to the agent server to update the agent positions
    let response = await fetch(agent_server_uri + "update") 

    // Check if the response was successful
    if(response.ok){
      // Retrieve the updated agent positions
      await getAgents()
      await getTrafficLights()
      // Log a message indicating that the agents have been updated
      console.log("Updated agents")
    }

  } catch (error) {
    // Log any errors that occur during the request
    console.log(error) 
  }
}

/*
 * Draws the scene by rendering the agents and obstacles.
 * 
 */
async function drawScene() {
    // Resize the canvas to match the display size
    twgl.resizeCanvasToDisplaySize(gl.canvas);

    // Set the viewport to match the canvas size
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    // Set the clear color and enable depth testing
    gl.clearColor(0.2, 0.2, 0.2, 1);
    gl.enable(gl.DEPTH_TEST);

    // Clear the color and depth buffers
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    // Use the program
    gl.useProgram(programInfo.program);

    let v3_lightPosition = v3.create(settings.lightPosition.x, settings.lightPosition.y, settings.lightPosition.z);
    let v3_cameraPosition = v3.create(settings.cameraPosition.x, settings.cameraPosition.y, settings.cameraPosition.z);

    const globalUniforms = {
      u_ambientLight: settings.ambientColor,
      u_diffuseLight: settings.diffuseColor,
      u_specularLight: settings.specularColor,
      u_viewWorldPosition: v3_cameraPosition,
      u_lightWorldPosition: v3_lightPosition,
    }
    twgl.setUniforms(programInfo, globalUniforms);
    // Set up the view-projection matrix
    const viewProjectionMatrix = setupWorldView(gl);

    // Draw the agents
    draw(cars, carsVao, carsBufferInfo, viewProjectionMatrix)    
    // Draw the obstacles
    draw(obstacles, obstaclesVao, obstaclesBufferInfo, viewProjectionMatrix)
    // Draw the traffic lights
    draw(traffic_lights, trafficLifghtsVao, trafficLightsBufferInfo, viewProjectionMatrix)
    // Draw the destinations
    draw(destinations, destinationsVao, destinationsBufferInfo, viewProjectionMatrix)
    // Draw the roads
    draw(roads, roadsVao, roadsBufferInfo, viewProjectionMatrix)

    // Increment the frame count
    frameCount++

    // Update the scene every 30 frames
    if(frameCount % 30 == 0){
      frameCount = 0
      await update()
    } 

    // Request the next frame
    requestAnimationFrame(()=>drawScene());
}

/*
 * Draws the agents.
 * 
 * @param {Number} distance - The distance for rendering.
 * @param {WebGLVertexArrayObject} agentsVao - The vertex array object for agents.
 * @param {Object} agentsBufferInfo - The buffer information for agents.
 * @param {Float32Array} viewProjectionMatrix - The view-projection matrix.
 */
function draw(arrays, vao, bufferInfo, viewProjectionMatrix){
    // Bind the vertex array object for agents
    gl.bindVertexArray(vao);

    // Iterate over the agents
    for(const object of arrays){

      // Create the agent's transformation matrix
      const object_trans = v3.create(...object.position);
      const object_scale = v3.create(...object.scale);

      // Calculate the agent's matrix
      object.matrix = twgl.m4.translate(twgl.m4.identity(), object_trans);
      object.matrix = twgl.m4.rotateX(object.matrix, object.rotation[0]);
      object.matrix = twgl.m4.rotateY(object.matrix, object.rotation[1]);
      object.matrix = twgl.m4.rotateZ(object.matrix, object.rotation[2]);
      object.matrix = twgl.m4.scale(object.matrix, object_scale);

      const modelViewProjectionMatrix = twgl.m4.multiply(viewProjectionMatrix, object.matrix);


      // Set the uniforms for the agent
      let uniforms = {
          u_world: object.matrix,
          u_worldViewProjection: modelViewProjectionMatrix,
          u_diffuseColor: object.color,
          u_specularColor: object.color,
          u_ambientColor: object.color,
          u_shininess: object.shininess,
      }


      // Set the uniforms and draw the agent
      twgl.setUniforms(programInfo, uniforms);
      twgl.drawBufferInfo(gl, bufferInfo);
      
    }
}


/*
 * Sets up the world view by creating the view-projection matrix.
 * 
 * @param {WebGLRenderingContext} gl - The WebGL rendering context.
 * @returns {Float32Array} The view-projection matrix.
 */
function setupWorldView(gl) {
    // Set the field of view (FOV) in radians
    const fov = 45 * Math.PI / 180;

    // Calculate the aspect ratio of the canvas
    const aspect = gl.canvas.clientWidth / gl.canvas.clientHeight;

    // Create the projection matrix
    const projectionMatrix = twgl.m4.perspective(fov, aspect, 1, 200);

    // Set the target position
    const target = [28/2, 0, 28/2];

    // Set the up vector
    const up = [0, 1, 0];

    // Calculate the camera position
    const camPos = twgl.v3.create(cameraPosition.x + 28/2, cameraPosition.y, cameraPosition.z+28/2)

    // Create the camera matrix
    const cameraMatrix = twgl.m4.lookAt(camPos, target, up);


    // Calculate the view matrix
    const viewMatrix = twgl.m4.inverse(cameraMatrix);

    // Calculate the view-projection matrix
    const viewProjectionMatrix = twgl.m4.multiply(projectionMatrix, viewMatrix);

    // Return the view-projection matrix
    return viewProjectionMatrix;
}

/*
 * Sets up the user interface (UI) for the camera position.
 */
function setupUI() {
    // Create a new GUI instance
    const gui = new GUI();

    // Create a folder for the camera position
    const posFolder = gui.addFolder('Position:')

    // Add a slider for the x-axis
    posFolder.add(cameraPosition, 'x', -50, 50)
        .onChange( value => {
            // Update the camera position when the slider value changes
            cameraPosition.x = value
        });

    // Add a slider for the y-axis
    posFolder.add( cameraPosition, 'y', -50, 50)
        .onChange( value => {
            // Update the camera position when the slider value changes
            cameraPosition.y = value
        });

    // Add a slider for the z-axis
    posFolder.add( cameraPosition, 'z', -50, 50)
        .onChange( value => {
            // Update the camera position when the slider value changes
            cameraPosition.z = value
        });

    // Create a folder for the light position
    const lightFolder = gui.addFolder('Light Position:')
    lightFolder.add(settings.lightPosition, 'x', -50, 50)
        .onChange( value => {
            // Update the light position when the slider value changes
            settings.lightPosition.x = value
        });
    lightFolder.add(settings.lightPosition, 'y', -50, 50)
        .onChange( value => {
            // Update the light position when the slider value changes
            settings.lightPosition.y = value
        });
    lightFolder.add(settings.lightPosition, 'z', -50, 50)
        .onChange( value => {
            // Update the light position when the slider value changes
            settings.lightPosition.z = value
        });

    const colorFolder = gui.addFolder('Colors:')
    colorFolder.addColor(settings, 'ambientColor')
        .onChange( value => {
            settings.ambientColor = value
        });
    colorFolder.addColor(settings, 'diffuseColor')
        .onChange( value => {
            settings.diffuseColor = value
        });
    colorFolder.addColor(settings, 'specularColor')
        .onChange( value => {
            settings.specularColor = value
        });
}

function generateData(size) {
    let arrays =
    {
        a_position: {
                numComponents: 3,
                data: [
                  // Front Face
                  -0.5, -0.5,  0.5,
                  0.5, -0.5,  0.5,
                  0.5,  0.5,  0.5,
                 -0.5,  0.5,  0.5,

                 // Back face
                 -0.5, -0.5, -0.5,
                 -0.5,  0.5, -0.5,
                  0.5,  0.5, -0.5,
                  0.5, -0.5, -0.5,

                 // Top face
                 -0.5,  0.5, -0.5,
                 -0.5,  0.5,  0.5,
                  0.5,  0.5,  0.5,
                  0.5,  0.5, -0.5,

                 // Bottom face
                 -0.5, -0.5, -0.5,
                  0.5, -0.5, -0.5,
                  0.5, -0.5,  0.5,
                 -0.5, -0.5,  0.5,

                 // Right face
                  0.5, -0.5, -0.5,
                  0.5,  0.5, -0.5,
                  0.5,  0.5,  0.5,
                  0.5, -0.5,  0.5,

                 // Left face
                 -0.5, -0.5, -0.5,
                 -0.5, -0.5,  0.5,
                 -0.5,  0.5,  0.5,
                 -0.5,  0.5, -0.5
                ].map(e => size * e)
            },

            a_normal: {
              numComponents: 3,
              data: [
                  // Front Face
                  0, 0, 1,
                  0, 0, 1,
                  0, 0, 1,
                  0, 0, 1,
  
                  // Back face
                  0, 0, -1,
                  0, 0, -1,
                  0, 0, -1,
                  0, 0, -1,
  
                  // Top face
                  0, 1, 0,
                  0, 1, 0,
                  0, 1, 0,
                  0, 1, 0,
  
                  // Bottom face
                  0, -1, 0,
                  0, -1, 0,
                  0, -1, 0,
                  0, -1, 0,
  
                  // Right face
                  1, 0, 0,
                  1, 0, 0,
                  1, 0, 0,
                  1, 0, 0,
  
                  // Left face
                  -1, 0, 0,
                  -1, 0, 0,
                  -1, 0, 0,
                  -1, 0, 0,
              ]
          },
        a_color: {
                numComponents: 4,
                data: [
                  // Front face
                    1, 0, 0, 1, // v_1
                    1, 0, 0, 1, // v_1
                    1, 0, 0, 1, // v_1
                    1, 0, 0, 1, // v_1
                  // Back Face
                    0, 1, 0, 1, // v_2
                    0, 1, 0, 1, // v_2
                    0, 1, 0, 1, // v_2
                    0, 1, 0, 1, // v_2
                  // Top Face
                    0, 0, 1, 1, // v_3
                    0, 0, 1, 1, // v_3
                    0, 0, 1, 1, // v_3
                    0, 0, 1, 1, // v_3
                  // Bottom Face
                    1, 1, 0, 1, // v_4
                    1, 1, 0, 1, // v_4
                    1, 1, 0, 1, // v_4
                    1, 1, 0, 1, // v_4
                  // Right Face
                    0, 1, 1, 1, // v_5
                    0, 1, 1, 1, // v_5
                    0, 1, 1, 1, // v_5
                    0, 1, 1, 1, // v_5
                  // Left Face
                    1, 0, 1, 1, // v_6
                    1, 0, 1, 1, // v_6
                    1, 0, 1, 1, // v_6
                    1, 0, 1, 1, // v_6
                ]
            },
        indices: {
                numComponents: 3,
                data: [
                  0, 1, 2,      0, 2, 3,    // Front face
                  4, 5, 6,      4, 6, 7,    // Back face
                  8, 9, 10,     8, 10, 11,  // Top face
                  12, 13, 14,   12, 14, 15, // Bottom face
                  16, 17, 18,   16, 18, 19, // Right face
                  20, 21, 22,   20, 22, 23  // Left face
                ]
            }
    };

    return arrays;
}


main();
