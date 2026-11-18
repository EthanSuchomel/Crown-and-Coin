// Joins neighbouring hexes of one terrain (Ethan, 2026-11-17): a patch of the tile's own middle, mirrored to fill, laid
// centre to centre across each shared edge (a soft capsule), and over the corner where three of them meet.
// Forests: drawn under the tiles (their rims fade early on joined sides). Lakes: drawn over them, across the beaches.
shader_type canvas_item;

uniform vec4 segs[160];               // xy -> zw: the two hex centres, board units
uniform int nseg = 0;
uniform vec2 corners[96];             // a corner shared by three hexes of this terrain, board units
uniform int ncorn = 0;
uniform float wid = 8.3;              // capsule half-width, board units
uniform float hr = 18.0;
uniform vec2 rect_units = vec2(100.0);   // the whole layer, board units
uniform sampler2D patch_tex : filter_linear;
uniform float patch_units = 19.4;     // the patch's size on the board, board units
uniform sampler2D noise_tex : repeat_enable, filter_linear;

float fade(float lo, float hi, float v) { return 1.0 - smoothstep(lo, hi, v); }

void fragment() {
	vec2 pos = UV * rect_units;
	float m = 0.0;
	for (int i = 0; i < nseg; i++) {
		vec2 a = segs[i].xy, b = segs[i].zw, ab = b - a;
		float s = clamp(dot(pos - a, ab) / dot(ab, ab), 0.0, 1.0);
		m = max(m, fade(wid * 0.62, wid, length(pos - (a + s * ab))));
	}
	for (int i = 0; i < ncorn; i++) {
		m = max(m, fade(hr * 0.30, hr * 0.52, length(pos - corners[i])));
	}
	if (m > 0.0 && m < 1.0) {
		float wob = (texture(noise_tex, pos / 120.0).r - 0.5) * 2.0;
		m = clamp(m + 0.12 * wob, 0.0, 1.0);
	}
	vec2 q = mod(pos / patch_units, 2.0);
	q = min(q, 2.0 - q);   // mirrored repeat
	COLOR = vec4(texture(patch_tex, q).rgb, m);
}
