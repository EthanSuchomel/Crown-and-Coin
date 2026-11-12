# Godot port, step 12: the board view draws whichever board the game uses (8 x 8, or the 3-player 11 x 11 hexagon,
# framed to just its hexes like the browser's VB_X / VB_Y).
import sys
W = sys.argv[1]
F = W + '/scripts/ui/board_view.gd'
s = open(F, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    if s.count(a) != n: print('COUNT', s.count(a), a[:140]); sys.exit(1)
    s = s.replace(a, b)
rep('''const N := 8
''', '''var N: int:
	get: return HexGrid.SIZE   # 8, or 11 on the 3-player board
''')
rep('''func _scale() -> float:
	return minf(size.x / _grid_h(), size.y / _grid_w())


func _offset() -> Vector2:
	return (size - Vector2(_grid_h(), _grid_w()) * _scale()) / 2.0


## Where hex i's centre is on screen.
func center(i: int) -> Vector2:
	var r: int = i / N
	var c: int = i % N
	var gx: float = HM + HR + c * 1.5 * HR
	var gy: float = HM + _hh / 2.0 + r * _hh + (c & 1) * _hh / 2.0
	return _offset() + Vector2(_grid_h() - gy, _grid_w() - gx) * _scale()''', '''## The part of the board that is drawn, in board units: the whole grid on the 2-player board; on the 3-player hexagon
## just its hexes (its grid corners are empty).
var _frame_n: int = -1
var _frame: Rect2
func _frame_rect() -> Rect2:
	if _frame_n == N:
		return _frame
	_frame_n = N
	if N == 8:
		_frame = Rect2(0, 0, _grid_h(), _grid_w())
		return _frame
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for i in N * N:
		if HexGrid.is_void(i):
			continue
		var p := _grid_pos(i)
		lo = lo.min(p - Vector2(_hh / 2.0, HR))
		hi = hi.max(p + Vector2(_hh / 2.0, HR))
	_frame = Rect2(lo - Vector2(HM, HM), hi - lo + Vector2(2 * HM, 2 * HM))
	return _frame


## Hex i's centre in board units (the board is drawn turned a quarter, as in the browser).
func _grid_pos(i: int) -> Vector2:
	var r: int = i / N
	var c: int = i % N
	var gx: float = HM + HR + c * 1.5 * HR
	var gy: float = HM + _hh / 2.0 + r * _hh + (c & 1) * _hh / 2.0
	return Vector2(_grid_h() - gy, _grid_w() - gx)


func _scale() -> float:
	var f := _frame_rect()
	return minf(size.x / f.size.x, size.y / f.size.y)


func _offset() -> Vector2:
	var f := _frame_rect()
	return (size - f.size * _scale()) / 2.0 - f.position * _scale()


## Where hex i's centre is on screen.
func center(i: int) -> Vector2:
	return _offset() + _grid_pos(i) * _scale()''')
open(F, 'w', encoding='utf-8').write(s); print('view3 ok')
