from aiohttp import web
from views import register, login, get_ads_list, get_ad, create_ad, patch_ad, delete_ad  # ИЗМЕНЕНО: добавлен get_ads_list

routes = web.RouteTableDef()

routes.post('/register')(register)
routes.post('/login')(login)
routes.get('/advertisements')(get_ads_list)           # ИЗМЕНЕНО: новый маршрут для списка
routes.get('/advertisements/{id:\d+}/')(get_ad)
routes.post('/advertisements')(create_ad)
routes.patch('/advertisements/{id:\d+}/')(patch_ad)
routes.delete('/advertisements/{id:\d+}/')(delete_ad)

async def root(request):
    return web.Response(text='Server is running')

routes.get('/')(root)
