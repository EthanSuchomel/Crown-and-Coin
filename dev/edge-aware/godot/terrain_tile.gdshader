// Edge-aware terrain tile (Ethan, 2026-11-17: forests, mountains and water "mesh together" when next to each other).
// One soft terrain tile, faded side by side by what its neighbour on that side is:
//   mode 0: grass, a castle or the map edge: fade out as the plain soft tile does
//   mode 1: the same terrain: forests fade well before their grassy rim (a ragged line; the canopy bridge under them
//           fills the join); mountains and lakes cross-fade over the shared edge (lakes are joined by the water bridge)
//   mode 2: another terrain (forest, mountain, water): fade over a wider band, so the two overlap with no grass between
shader_type canvas_item;

uniform int modes[6];                 // per side, in edge order (edge k faces neighbour slot k)
uniform int kind = 0;                 // 0 forest, 1 mountain, 2 water
uniform vec2 size_units = vec2(34.8, 40.3);   // the tile's drawn size, in board units
uniform float hr = 18.0;              // hex radius, board units
uniform sampler2D noise_tex : repeat_enable, filter_linear;
uniform vec2 seed = vec2(0.0);
uniform bool underlay = false;      // the solid layer under the joins: the tile out to every edge it shares with its own terrain

float fade(float lo, float hi, float v) { return 1.0 - smoothstep(lo, hi, v); }   // 1 inside lo, 0 past hi

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	vec2 p = (UV - 0.5) * size_units;
	float apo = hr * 0.8660254;
	float n = (texture(noise_tex, UV * 0.9 + seed).r - 0.5) * 2.0;
	if (underlay) {
		float dmax = -1.0; int kmax = 0;
		for (int k = 0; k < 6; k++) {
			float m = (float(k) + 0.5) * PI / 3.0;
			float dk = dot(p, vec2(-sin(m), -cos(m))) / apo;
			if (dk > dmax) { dmax = dk; kmax = k; }
		}
		COLOR = vec4(c.rgb, (modes[kmax] == 1 && dmax <= 1.0) ? 1.0 : 0.0);
	} else {
	float a = 1.0;
	for (int k = 0; k < 6; k++) {
		float m = (float(k) + 0.5) * PI / 3.0;
		vec2 nk = vec2(-sin(m), -cos(m));
		float dk = dot(p, nk) / apo;
		float d = dk + (kind == 1 ? 0.06 : 0.03) * n;
		int md = modes[k];
		if (md == 1 && kind == 0) {
			float n2 = (texture(noise_tex, UV * 1.3 + seed + vec2(0.37, 0.11) * float(k + 1)).r - 0.5) * 2.0;
			a = min(a, fade(0.58, 0.84, dk + 0.16 * n2));
		} else if (md == 1) {
			a = min(a, fade(0.90, 1.10, d));
		} else if (md == 2) {
			a = min(a, fade(0.92, 1.14, d));
		} else {
			a = min(a, fade(kind == 1 ? 0.88 : 0.968, 1.10, d));
		}
	}
	COLOR = vec4(c.rgb, a);
	}
}
