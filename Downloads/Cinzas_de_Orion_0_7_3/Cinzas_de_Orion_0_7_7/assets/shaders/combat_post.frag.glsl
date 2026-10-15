#version 330 core
in vec2 v_uv;
out vec4 fragColor;
uniform sampler2D u_scene;
uniform vec2 u_resolution;
uniform int u_light_count;
uniform vec4 u_light_pos_radius[8]; // x,y pixels, radius pixels, intensity
uniform vec4 u_light_color[8];      // rgb 0..1, unused alpha
uniform int u_shock_enabled;
uniform vec2 u_shock_origin;         // top-left canvas pixel coordinates
uniform float u_shock_age;
uniform float u_shock_duration;
uniform float u_shock_intensity;
uniform float u_chromatic_intensity;

vec4 sceneAt(vec2 uv) {
    return texture(u_scene, clamp(uv, vec2(0.001), vec2(0.999)));
}
void main() {
    vec2 uv = v_uv;
    vec2 pixel = vec2(uv.x * u_resolution.x, (1.0 - uv.y) * u_resolution.y);
    vec2 sampleUV = uv;

    // Expanding screen-space refraction ring, enabled for critical/supreme hits.
    if (u_shock_enabled == 1 && u_shock_duration > 0.0) {
        float t = clamp(u_shock_age / u_shock_duration, 0.0, 1.0);
        vec2 delta = pixel - u_shock_origin;
        float distPx = length(delta);
        vec2 radial = distPx > 0.001 ? delta / distPx : vec2(0.0, 0.0);
        float ringRadius = t * min(u_resolution.x, u_resolution.y) * 0.58;
        float ringEnvelope = exp(-abs(distPx - ringRadius) * 0.055);
        float wave = sin((distPx - ringRadius) * 0.17) * ringEnvelope;
        float decay = (1.0 - t) * (0.35 + 0.65 * sin(3.14159265 * t));
        vec2 radialUV = vec2(radial.x, -radial.y); // UV Y points upward, screen Y downward.
        vec2 refraction = radialUV * wave * u_shock_intensity * 8.0 * decay / u_resolution;
        sampleUV += refraction;
    }

    vec4 base;
    if (u_shock_enabled == 1 && u_chromatic_intensity > 0.0) {
        vec2 delta = pixel - u_shock_origin;
        float d = max(length(delta), 1.0);
        vec2 radialUV = vec2(delta.x, -delta.y) / d / u_resolution;
        float t = clamp(u_shock_age / max(u_shock_duration, 0.001), 0.0, 1.0);
        float chroma = u_chromatic_intensity * 0.0018 * (1.0 - t) * exp(-abs(d - t * min(u_resolution.x, u_resolution.y) * 0.58) * 0.025);
        vec4 rSample = sceneAt(sampleUV + radialUV * chroma);
        vec4 gSample = sceneAt(sampleUV);
        vec4 bSample = sceneAt(sampleUV - radialUV * chroma);
        base = vec4(rSample.r, gSample.g, bSample.b, gSample.a);
    } else {
        base = sceneAt(sampleUV);
    }

    // Screen-space point lights: distance attenuation lights the hit sprite and
    // the surrounding arena without touching sprite art or game attributes.
    vec3 illumination = vec3(0.0);
    for (int i = 0; i < 8; ++i) {
        if (i >= u_light_count) break;
        vec4 light = u_light_pos_radius[i];
        // Keep the lighting pass off the compact combat HUD; the arena is the
        // only area lit by the technique, while shockwave remains full-screen.
        if (pixel.x < 270.0 || pixel.x > 1180.0 || pixel.y < 108.0 || pixel.y > 675.0) continue;
        float d = distance(pixel, light.xy);
        float radius = max(light.z, 1.0);
        float atten = max(0.0, 1.0 - d / radius);
        atten = atten * atten / (1.0 + (d * d) / (radius * radius * 0.42));
        illumination += u_light_color[i].rgb * atten * light.w;
    }
    fragColor = vec4(clamp(base.rgb + illumination, 0.0, 1.0), base.a);
}
