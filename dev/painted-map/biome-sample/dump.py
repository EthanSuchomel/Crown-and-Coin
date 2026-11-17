import asyncio,sys,json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':800})
        await pg.goto('file:///home/claude/crown-and-coin/index.html'); await pg.wait_for_timeout(1200)
        await pg.click('[data-scr="start"]'); await pg.wait_for_timeout(300); await pg.click('[data-scr="go"]'); await pg.wait_for_timeout(800)
        await pg.evaluate("newGame('dinos',{np:3,opps:['robots','mammals'],quiet:true}); render();"); await pg.wait_for_timeout(500)
        d=await pg.evaluate("JSON.stringify({vb:document.querySelector('#map').getAttribute('viewBox'),HR,tiles:S.tiles.map((t,i)=>{const[cx,cy]=hexCenter(i);return {i,cx,cy,terrain:t.terrain,forest:!!t.forest,fern:!!t.fern,castle:!!t.castle,home:S.homes.includes(i)}}), forest:FOREST_ART.map(a=>a.uri), fern:FERN_ART.map(a=>a.uri)})")
        open('/home/claude/work/board.json','w').write(d); await b.close()
asyncio.run(main())
