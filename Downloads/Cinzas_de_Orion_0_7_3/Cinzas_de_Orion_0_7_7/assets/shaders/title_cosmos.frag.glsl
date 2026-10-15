#version 330 core
uniform sampler2D u_ui;
uniform vec2 u_resolution;
uniform float u_time;
in vec2 v_uv;
out vec4 fragColor;

float hash21(vec2 p) {
    p = fract(p * vec2(234.56, 789.12));
    p += dot(p, p + 34.56);
    return fract(p.x * p.y);
}

vec4 renderPlanet(vec2 uv, vec2 center, float radius, vec3 colDark, vec3 colLit, vec3 rimCol, vec3 lightDir, float time) {
    vec2 d = (uv - center) / radius;
    float r2 = dot(d, d);
    if (r2 > 1.0) {
        float dist = sqrt(r2) - 1.0;
        float atmo = exp(-dist * 9.5) * 0.42;
        return vec4(rimCol * atmo, atmo);
    }
    float z = sqrt(max(0.0, 1.0 - r2));
    vec3 normal = normalize(vec3(d.x, d.y, z));
    float ndotl = clamp(dot(normal, normalize(lightDir)), 0.0, 1.0);
    float bands = 0.92 + 0.08 * sin(d.y * 16.0 + d.x * 3.5 + time * 0.15);
    vec3 sphereGrad = mix(colDark, colLit, pow(ndotl, 0.82)) * bands;
    float rim = pow(1.0 - z, 2.75) * (0.35 + 0.65 * ndotl);
    vec3 finalCol = sphereGrad + rimCol * rim * 0.95;
    float edgeAlpha = smoothstep(1.0, 0.975, sqrt(r2));
    return vec4(clamp(finalCol, 0.0, 1.0), edgeAlpha);
}

void main() {
    float aspect = u_resolution.x / max(1.0, u_resolution.y);
    vec2 uv = vec2(v_uv.x * aspect, v_uv.y);
    vec3 bg = mix(vec3(0.018, 0.028, 0.055), vec3(0.045, 0.075, 0.115), smoothstep(0.0, 1.0, 1.0 - v_uv.y));
    float nebula = 0.5 + 0.5 * sin(uv.x * 2.4 + uv.y * 1.8 + u_time * 0.12);
    bg += vec3(0.015, 0.045, 0.065) * nebula * 0.45;

    vec3 stars = vec3(0.0);
    for (int layer = 1; layer <= 2; layer++) {
        float scale = (layer == 1) ? 46.0 : 88.0;
        vec2 grid = floor(uv * scale + float(layer) * 19.7);
        vec2 f = fract(uv * scale + float(layer) * 19.7) - 0.5;
        float rnd = hash21(grid);
        if (rnd > 0.81) {
            vec2 starOffset = (vec2(fract(rnd * 13.7), fract(rnd * 29.3)) - 0.5) * 0.55;
            float dist = length(f - starOffset);
            float speed = 1.8 + fract(rnd * 43.1) * 4.5;
            float phase = rnd * 6.28318;
            float twinkle = 0.30 + 0.70 * (0.5 + 0.5 * sin(u_time * speed + phase));
            float core = smoothstep(0.16 / float(layer), 0.0, dist) * twinkle;
            vec3 starCol = mix(vec3(0.70, 0.90, 1.0), vec3(1.0, 0.88, 0.68), fract(rnd * 7.3));
            stars += starCol * core;
        }
    }

    vec3 color = bg + stars;
    vec3 lightDir = normalize(vec3(-0.65, 0.48, 0.58));
    vec4 mainPlanet = renderPlanet(uv, vec2(0.50 * aspect, 0.48), 0.22, vec3(0.07, 0.11, 0.17), vec3(0.76, 0.52, 0.33), vec3(0.38, 0.92, 0.96), lightDir, u_time);
    color = mix(color, mainPlanet.rgb, mainPlanet.a);
    vec4 secondPlanet = renderPlanet(uv, vec2(0.77 * aspect, 0.66), 0.075, vec3(0.08, 0.05, 0.12), vec3(0.58, 0.25, 0.28), vec3(0.98, 0.68, 0.36), lightDir, u_time);
    color = mix(color, secondPlanet.rgb, secondPlanet.a);
    vec4 moonPlanet = renderPlanet(uv, vec2(0.23 * aspect, 0.30), 0.048, vec3(0.05, 0.10, 0.15), vec3(0.38, 0.64, 0.78), vec3(0.55, 0.95, 1.00), lightDir, u_time);
    color = mix(color, moonPlanet.rgb, moonPlanet.a);

    vec4 ui = texture(u_ui, v_uv);
    if (v_uv.y < 0.26) {
        float pulseText = 0.28 + 0.72 * (0.5 + 0.5 * sin(u_time * 3.0));
        ui.a *= pulseText;
        ui.rgb += vec3(0.10, 0.28, 0.32) * pulseText * ui.a;
    }
    color = mix(color, ui.rgb, ui.a);
    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
