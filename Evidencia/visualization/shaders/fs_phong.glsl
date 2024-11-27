#version 300 es
precision highp float;

in vec3 v_normal;
in vec3 v_lightDirection;
in vec3 v_cameraDirection;

uniform vec4 u_ambientLight;
uniform vec4 u_diffuseLight;
uniform vec4 u_specularLight;

// Model uniforms
uniform vec4 u_ambientColor;
uniform vec4 u_diffuseColor;
uniform vec4 u_specularColor;
uniform float u_shininess;

out vec4 outColor;

void main() {
    // Ambient lighting component
    vec4 ambient = u_ambientLight * u_ambientColor;

    // Diffuse light component
    vec4 diffuse = vec4(0, 0, 0, 1);
    vec3 v_n = normalize(v_normal);
    vec3 v_l = normalize(v_lightDirection);
    vec3 v_c = normalize(v_cameraDirection);

    float lambert = dot(v_n, v_l);

    if (lambert > 0.0) {
        diffuse = u_diffuseLight * u_diffuseColor * lambert;
    }
    // Specular light component
    vec4 specular = vec4(0, 0, 0, 1);
    vec3 v_par = v_n * dot(v_n, v_l);
    vec3 v_per = v_n - v_par;
    vec3 v_ref = v_par - v_per;
    float spec = dot(v_c, v_ref);

    if (spec > 0.0){
        specular = u_specularLight * u_specularColor * pow(spec, u_shininess);
 
    }

    outColor = ambient + diffuse + specular;
}