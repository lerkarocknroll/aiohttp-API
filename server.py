from aiohttp import web
from routes import routes
from models import init_db, HTTPError


@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except HTTPError as e:
        return web.json_response({'message': e.message}, status=e.status_code)
    except Exception:
        return web.json_response({'message': 'Internal server error'}, status=500)


async def app_factory():
    await init_db()
    app = web.Application(middlewares=[error_middleware])
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    web.run_app(app_factory(), host='0.0.0.0', port=8000)