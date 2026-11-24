class_name PlateBox
extends StyleBox
## A panel or button "plate" like the browser version's (Ethan, 2026-11-22): a vertical gradient (iron, bronze or gold),
## a trim line, a near-black ring round it, an optional outer glow ring (a picked tile), a light line along the top,
## a dark strip along the bottom, and optional diamond studs at the left and right ends (the home screen's buttons).

var stops: PackedColorArray = PackedColorArray([Color("3b3226"), Color("1d1710")])
var at: PackedFloat32Array = PackedFloat32Array([0.0, 1.0])
var trim: Color = Color("6e5226")
var trim_w: float = 2.0
var ring: Color = Color("120c06")
var ring_w: float = 2.0
var glow: Color = Color(0, 0, 0, 0)   # an outer ring past the dark one (a picked tile's gold)
var glow_w: float = 0.0
var top_hi: Color = Color(1.0, 0.925, 0.745, 0.15)
var top_hi_w: float = 1.0
var bottom_lo: Color = Color(0, 0, 0, 0)
var bottom_lo_w: float = 0.0
var inner: Color = Color(0, 0, 0, 0)   # a thin line just inside the trim
var inner_w: float = 1.0
var gem: Color = Color(0, 0, 0, 0)   # diamond studs at both ends
var gem_ring: Color = Color("120c06")


## cols: the gradient's colours top to bottom; pos: where each sits (0..1), or [] for evenly spread.
static func make(cols: Array, trim_c: Color, margin_x: float = 12.0, margin_y: float = 7.0, pos: Array = []) -> PlateBox:
	var p := PlateBox.new()
	p.stops = PackedColorArray(cols)
	var a := PackedFloat32Array()
	for i in cols.size():
		a.append(float(pos[i]) if pos.size() == cols.size() else float(i) / float(maxi(1, cols.size() - 1)))
	p.at = a
	p.trim = trim_c
	p.content_margin_left = margin_x
	p.content_margin_right = margin_x
	p.content_margin_top = margin_y
	p.content_margin_bottom = margin_y
	return p


func copy() -> PlateBox:
	var p: PlateBox = duplicate()
	p.stops = stops.duplicate()
	p.at = at.duplicate()
	return p


func _draw(ci: RID, rect: Rect2) -> void:
	var rs := RenderingServer
	if glow.a > 0.0 and glow_w > 0.0:
		rs.canvas_item_add_rect(ci, rect.grow(ring_w + glow_w), glow)
	if ring.a > 0.0 and ring_w > 0.0:
		rs.canvas_item_add_rect(ci, rect.grow(ring_w), ring)
	if trim_w > 0.0:
		rs.canvas_item_add_rect(ci, rect, trim)
	var r: Rect2 = rect.grow(-trim_w)
	if r.size.x <= 0.0 or r.size.y <= 0.0:
		return
	for i in stops.size() - 1:
		var y0: float = r.position.y + r.size.y * at[i]
		var y1: float = r.position.y + r.size.y * at[i + 1]
		if y1 <= y0:
			continue
		rs.canvas_item_add_polygon(ci, PackedVector2Array([Vector2(r.position.x, y0), Vector2(r.end.x, y0), Vector2(r.end.x, y1), Vector2(r.position.x, y1)]),
			PackedColorArray([stops[i], stops[i], stops[i + 1], stops[i + 1]]))
	if inner.a > 0.0 and inner_w > 0.0:
		rs.canvas_item_add_rect(ci, Rect2(r.position, Vector2(r.size.x, inner_w)), inner)
		rs.canvas_item_add_rect(ci, Rect2(Vector2(r.position.x, r.end.y - inner_w), Vector2(r.size.x, inner_w)), inner)
		rs.canvas_item_add_rect(ci, Rect2(r.position, Vector2(inner_w, r.size.y)), inner)
		rs.canvas_item_add_rect(ci, Rect2(Vector2(r.end.x - inner_w, r.position.y), Vector2(inner_w, r.size.y)), inner)
	if top_hi.a > 0.0 and top_hi_w > 0.0:
		rs.canvas_item_add_rect(ci, Rect2(r.position, Vector2(r.size.x, top_hi_w)), top_hi)
	if bottom_lo.a > 0.0 and bottom_lo_w > 0.0:
		rs.canvas_item_add_rect(ci, Rect2(Vector2(r.position.x, r.end.y - bottom_lo_w), Vector2(r.size.x, bottom_lo_w)), bottom_lo)
	if gem.a > 0.0:
		var g: float = clampf(r.size.y * 0.16, 3.0, 7.0)
		for x in [r.position.x + g * 2.2, r.end.x - g * 2.2]:
			var c := Vector2(x, r.position.y + r.size.y / 2.0)
			var gr: float = g + 1.5
			rs.canvas_item_add_polygon(ci, PackedVector2Array([c + Vector2(0, -gr), c + Vector2(gr, 0), c + Vector2(0, gr), c + Vector2(-gr, 0)]), PackedColorArray([gem_ring]))
			rs.canvas_item_add_polygon(ci, PackedVector2Array([c + Vector2(0, -g), c + Vector2(g, 0), c + Vector2(0, g), c + Vector2(-g, 0)]), PackedColorArray([gem]))
