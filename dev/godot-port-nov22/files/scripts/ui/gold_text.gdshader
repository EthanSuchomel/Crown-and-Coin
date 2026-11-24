shader_type canvas_item;
// Carved-gold lettering for the home screen's title (Ethan, 2026-11-22), as the browser's background-clip:text gradient:
// the letters' fill runs through the colour stops from y0 to y1 (label pixels); the outline and shadow stay dark.
uniform vec4 c0 : source_color = vec4(1.0, 0.965, 0.84, 1.0);
uniform vec4 c1 : source_color = vec4(0.969, 0.843, 0.486, 1.0);
uniform vec4 c2 : source_color = vec4(0.878, 0.663, 0.227, 1.0);
uniform vec4 c3 : source_color = vec4(0.659, 0.439, 0.11, 1.0);
uniform vec4 c4 : source_color = vec4(0.949, 0.784, 0.384, 1.0);
uniform float y0 = 0.0;
uniform float y1 = 100.0;
varying float ly;

void vertex() {
	ly = VERTEX.y;
}

void fragment() {
	vec4 tx = texture(TEXTURE, UV);
	float t = clamp((ly - y0) / max(1.0, y1 - y0), 0.0, 1.0);
	vec3 g = t < 0.28 ? mix(c0.rgb, c1.rgb, t / 0.28)
		: t < 0.52 ? mix(c1.rgb, c2.rgb, (t - 0.28) / 0.24)
		: t < 0.72 ? mix(c2.rgb, c3.rgb, (t - 0.52) / 0.20)
		: mix(c3.rgb, c4.rgb, (t - 0.72) / 0.28);
	// the fill is drawn white; the outline and shadow keep their own dark colour
	float fill = step(0.9, COLOR.g);
	COLOR = vec4(mix(COLOR.rgb, g, fill), tx.a * COLOR.a);
}
