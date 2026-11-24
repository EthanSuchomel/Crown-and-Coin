// The open sea behind the map (Ethan, 2026-11-23: no more dark void round the board). Fixed to the board, so it
// pans and zooms with the map, and slowly moving.
shader_type canvas_item;

uniform vec2 rect_px = vec2(100.0);   // the board's size, pixels
uniform vec2 off = vec2(0.0);         // where the board's grid starts, pixels
uniform float u = 1.0;                // pixels per board unit
uniform sampler2D noise_tex : repeat_enable, filter_linear;

void fragment() {
	vec2 pos = (UV * rect_px - off) / max(u, 0.001);
	float t = TIME * 0.02;
	float n = texture(noise_tex, pos / 150.0 + vec2(t, t * 0.6)).r;
	float n2 = texture(noise_tex, pos / 47.0 - vec2(t * 1.6, t)).r;
	vec3 c = mix(vec3(0.02, 0.24, 0.45), vec3(0.04, 0.33, 0.56), smoothstep(0.3, 0.8, n * 0.6 + n2 * 0.4));
	c += vec3(0.85, 0.95, 1.0) * smoothstep(0.80, 0.88, n2) * smoothstep(0.45, 0.7, n) * 0.22;   // glints
	COLOR = vec4(c, 1.0);
}
