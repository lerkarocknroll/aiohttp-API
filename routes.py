from aiohttp import web
from views import get_ad, create_ad, patch_ad, delete_ad

async def root(request):
    return web.Response(text="Server is running")

routes.get('/')(root)

routes = web.RouteTableDef()

routes.get('/advertisements/{id:\d+}/')(get_ad)
routes.post('/advertisements')(create_ad)
routes.patch('/advertisements/{id:\d+}/')(patch_ad)
routes.delete('/advertisements/{id:\d+}/')(delete_ad)
