#version 330 core
out vec2 v_local;
out vec4 v_color;
out float v_alpha;
uniform vec2 u_resolution;
uniform vec2 u_origin; // top-left pixels
uniform float u_age;
uniform float u_duration;
uniform vec4 u_color;
uniform float u_intensity;
uniform int u_preset; // 0 fire, 1 shield, 2 heal, 3..9 elements, 10 physical
uniform int u_particle_count;

float hash1(float n) { return fract(sin(n * 127.1 + 311.7) * 43758.5453123); }
vec2 quadCorner(int id) {
    if (id == 0) return vec2(-1.0, -1.0);
    if (id == 1) return vec2( 1.0, -1.0);
    if (id == 2) return vec2( 1.0,  1.0);
    if (id == 3) return vec2(-1.0, -1.0);
    if (id == 4) return vec2( 1.0,  1.0);
    return vec2(-1.0, 1.0);
}
void main() {
    float id = float(gl_InstanceID);
    float r1 = hash1(id + 1.0);
    float r2 = hash1(id + 19.3);
    float r3 = hash1(id + 71.7);
    float delay = r1 * min(0.20, u_duration * 0.22);
    float age = u_age - delay;
    float life = u_duration * mix(0.48, 0.98, r2);
    vec2 origin = u_origin;
    vec2 pos = origin;
    float size = mix(2.0, 4.5, r3);
    float alpha = 0.0;
    vec3 rgb = u_color.rgb;

    if (age >= 0.0 && age <= life) {
        float q = clamp(age / max(life, 0.001), 0.0, 1.0);
        alpha = (1.0 - smoothstep(0.72, 1.0, q)) * u_intensity;
        if (u_preset == 0) { // fire: embers rise; red -> orange -> yellow
            pos += vec2((r2 - 0.5) * 52.0 + sin(age * 8.0 + id) * 5.0,
                        16.0 - age * mix(72.0, 118.0, r3));
            rgb = mix(vec3(1.0, 0.12, 0.025), vec3(1.0, 0.88, 0.18), smoothstep(0.10, 0.82, q));
            size *= 1.0 - 0.28 * q;
        } else if (u_preset == 1) { // kinetic shield: orbiting elliptical outline
            float theta = (id / float(max(u_particle_count, 1))) * 6.2831853 + u_age * 1.45;
            pos += vec2(cos(theta) * 25.0, sin(theta) * 47.0);
            alpha *= 0.55 + 0.45 * sin(theta * 3.0 + u_age * 15.0) * sin(theta * 3.0 + u_age * 15.0);
            size = mix(2.4, 4.4, r3);
        } else if (u_preset == 2) { // heal: bright ascending spiral
            float theta = id * 2.399963 + age * 5.2;
            float radius = 4.0 + 15.0 * q + 4.0 * sin(id + u_age * 7.0);
            pos += vec2(cos(theta) * radius, sin(theta) * radius - age * 34.0);
            rgb = mix(u_color.rgb, vec3(0.72, 1.0, 0.82), 0.45 + 0.35 * sin(theta));
            size *= 1.15;
        } else { // all other elements: radial shards / spark bursts in their color
            float theta = r1 * 6.2831853 + r3 * 0.7;
            float velocity = mix(24.0, 82.0, r2);
            float radius = 5.0 + age * velocity;
            pos += vec2(cos(theta) * radius, sin(theta) * radius - age * (u_preset == 4 ? 12.0 : 0.0));
            alpha *= (1.0 - q * 0.25);
            size *= 1.0 - 0.35 * q;
        }
    }
    vec2 corner = quadCorner(gl_VertexID);
    vec2 pixel = pos + corner * size;
    vec2 ndc = vec2(pixel.x / u_resolution.x * 2.0 - 1.0,
                     1.0 - pixel.y / u_resolution.y * 2.0);
    gl_Position = vec4(ndc, 0.0, 1.0);
    v_local = corner;
    v_color = vec4(rgb, u_color.a);
    v_alpha = clamp(alpha, 0.0, 1.0);
}
