// The coast round every map (Ethan, 2026-11-23: "a water/beach border so that there is no more dark void around it",
// and the map's edges cleaned up): drawn into the baked ground over the grass. dist_tex holds, for every point, how
// far it is from the land's edge (board units: below 0 on land, above 0 at sea), blurred so the shore is smooth
// rather than following each hex's edges. Sand covers the outer rim of the land, then wet sand, a line of surf,
// shallow water, and the open sea (the ocean behind the board shows through).
shader_type canvas_item;

uniform sampler2D dist_tex : filter_linear;
uniform vec2 full_units = vec2(100.0);    // the whole layer, board units
uniform float lo = -20.0;                 // dist_tex 0 and 1, board units
uniform float hi = 40.0;
uniform sampler2D noise_tex : repeat_enable, filter_linear;
uniform bool top = false;                 // the pass over the terrain tiles: only off the land, so tiles on the shore
                                          // don't poke out over the beach and sea with their hex corners

const vec3 SAND = vec3(0.86, 0.77, 0.52);
const vec3 WET = vec3(0.66, 0.58, 0.39);
const vec3 SHALLOW = vec3(0.09, 0.57, 0.69);
const vec3 MID = vec3(0.02, 0.33, 0.56);
const vec3 FOAM = vec3(0.90, 0.96, 0.94);

void fragment() {
	vec2 pos = UV * full_units;
	float d = mix(lo, hi, texture(dist_tex, UV).r);
	float n = (texture(noise_tex, pos / 64.0).r - 0.5) * 2.0;
	float n2 = (texture(noise_tex, pos / 19.0 + vec2(0.37, 0.61)).r - 0.5) * 2.0;
	d += n * 2.4 + n2 * 0.7;   // a ragged, natural shoreline
	float a = smoothstep(-5.2, -3.4, d) * (1.0 - smoothstep(12.0, 24.0, d));
	if (top) {
		a *= smoothstep(0.6, 2.2, d);
	}
	if (a <= 0.0) {
		COLOR = vec4(0.0);
	} else {
		vec3 c = SAND * (0.95 + 0.07 * n2);
		c = mix(c, WET, smoothstep(1.6, 3.6, d));
		vec3 w = mix(SHALLOW, MID, smoothstep(4.5, 13.0, d));
		float foam = (1.0 - smoothstep(0.0, 1.3, abs(d - 4.6))) * (0.55 + 0.45 * n2);
		foam += (1.0 - smoothstep(0.0, 0.8, abs(d - 7.4 - n * 1.5))) * 0.22;   // a second, fainter wave line
		w = mix(w, FOAM, clamp(foam, 0.0, 1.0) * 0.75);
		c = mix(c, w, smoothstep(3.7, 4.4, d));
		COLOR = vec4(c, a);
	}
}
