from aiohttp import web
from views import register, login, get_ad, create_ad, patch_ad, delete_ad

routes = web.RouteTableDef()

routes.post('/register')(register)
routes.post('/login')(login)
routes.get('/advertisements/{id:\d+}/')(get_ad)
routes.post('/advertisements')(create_ad)
routes.patch('/advertisements/{id:\d+}/')(patch_ad)
routes.delete('/advertisements/{id:\d+}/')(delete_ad)

async def root(request):
    return web.Response(text='Server is running')

routes.get('/')(root)
