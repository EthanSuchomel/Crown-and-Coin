"""Ethan, 2026-11-23: the baked ground (terrain_bake.gd) came out wrong when it was made a few seconds into the game:
the edge-aware forest/mountain/water tiles missing and the joins in the wrong places (the river on The great divide gone).
The picture was taken from a SubViewport drawn only once (UPDATE_ONCE), sometimes before the new shader settings
(each tile's sides, the joins' segments) had reached the graphics card. Now the viewport draws every frame while the
picture is made, and the picture is taken after 4 frames.
Usage: python3 p9_bake_render.py PROJ"""
import sys
sys.path.insert(0, __file__.rsplit('/', 2)[0] + '/godot-port-nov22')
from common import F
f = F(sys.argv[1] + '/scripts/ui/terrain_bake.gd')
f.rep('''    vp.render_target_update_mode = SubViewport.UPDATE_ONCE''', '''    vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS   # drawn every frame while it's made (UPDATE_ONCE could be too early)''')
f.rep('''    await RenderingServer.frame_post_draw
    await RenderingServer.frame_post_draw
    var img''', '''    for w in 4:
        await RenderingServer.frame_post_draw
    var img''')
f.save()
print('ok')
