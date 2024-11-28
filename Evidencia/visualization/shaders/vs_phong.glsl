#version 300 es
in vec4 a_position;
in vec3 a_normal;

// Global Uniforms
uniform vec3 u_viewWorldPosition;
uniform vec3 u_lightWorldPosition;

// Model Uniforms
uniform mat4 u_world;
uniform mat4 u_worldInverseTransform;
uniform mat4 u_worldViewProjection;

out vec3 v_normal;
out vec3 v_cameraDirection;
out vec3 v_lightDirection;

void main() {
    gl_Position = u_worldViewProjection * a_position;

    v_normal = mat3(u_world) * a_normal;

    // Vertex position with object transformations
    vec3 transformedPosition = (u_world * a_position).xyz;

    // Get vectors to the light and to the camera
    v_lightDirection = u_lightWorldPosition - transformedPosition;
    v_cameraDirection = u_viewWorldPosition - transformedPosition;
}