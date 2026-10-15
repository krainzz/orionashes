// ============================================================================
// particle.vert — GLSL 330 core | ModernGL
// Recebe um vértice por partícula (instancing-friendly: quad em strip) e projeta
// em screen-space (pixels, Y invertido para casar com pygame).
// A curva de vida (size/alpha/color) é avaliada no fragmento; aqui apenas o
// tamanho base interpolado linearmente entre os keyframes de escala.
// ============================================================================
#version 330 core

// Layout por vértice (17 floats): corner(2) pos(2) size rot life kind colA(4) colB(4) seed
layout (location = 0) in vec2 in_corner;   // canto do quad (-1..1)
layout (location = 1) in vec2 in_pos;      // posição em pixels (espaço pygame)
layout (location = 2) in float in_size;    // raio atual em pixels
layout (location = 3) in float in_rot;     // rotação em radianos
layout (location = 4) in float in_life;    // 0 -> recém-nascida, 1 -> morrendo
layout (location = 5) in float in_kind;    // id visual (ver vfx_manager.KIND)
layout (location = 6) in vec4 in_color_a;  // cor no nascimento (linear-ish HDR)
layout (location = 7) in vec4 in_color_b;  // cor na morte
layout (location = 8) in float in_seed;    // seed p/ ruído procedural no frag

uniform vec2  u_viewport;   // (W, H) em pixels
uniform vec2  u_shake;      // offset de câmera (screen shake) em px
uniform float u_time;       // tempo global (s)

out vec2  v_local;          // coordenada local do sprite (-1..1)
out float v_life;
out float v_kind;
out vec4  v_color_a;
out vec4  v_color_b;
out float v_seed;
out float v_time;

void main() {
    v_local  = in_corner;
    v_life   = in_life;
    v_kind   = in_kind;
    v_color_a = in_color_a;
    v_color_b = in_color_b;
    v_seed   = in_seed;
    v_time   = u_time;

    // billboard rotacionado: aplica rotação da partícula ao canto do quad
    float cs = cos(in_rot), sn = sin(in_rot);
    vec2 c = vec2(in_corner.x * cs - in_corner.y * sn,
                  in_corner.x * sn + in_corner.y * cs);
    vec2 px = in_pos + c * in_size + u_shake;

    // pixels -> NDC (Y para cima no GL, mas pygame tem Y para baixo: invertemos)
    vec2 ndc = (px / u_viewport) * 2.0 - 1.0;
    gl_Position = vec4(ndc.x, -ndc.y, 0.0, 1.0);
}
