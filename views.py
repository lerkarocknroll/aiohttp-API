from aiohttp import web
import pydantic
from models import Session, AdModel, CreateAdModel, UpdateAdModel, HTTPError


async def get_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info['id'])
    async with Session() as session:
        ad = await session.get(AdModel, ad_id)
        if ad is None:
            raise HTTPError(404, 'Ad not found')
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'created_at': ad.created_at.isoformat(),
            'owner': ad.owner,
        })


async def create_ad(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        raise HTTPError(400, 'Invalid JSON')

    try:
        validated = CreateAdModel(**data).model_dump()
    except pydantic.ValidationError as er:
        raise HTTPError(400, er.errors())

    async with Session() as session:
        ad = AdModel(**validated)
        session.add(ad)
        await session.commit()
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'owner': ad.owner,
        }, status=201)


async def patch_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info['id'])
    try:
        data = await request.json()
    except Exception:
        raise HTTPError(400, 'Invalid JSON')

    try:
        validated = UpdateAdModel(**data).model_dump(exclude_unset=True)
    except pydantic.ValidationError as er:
        raise HTTPError(400, er.errors())

    async with Session() as session:
        ad = await session.get(AdModel, ad_id)
        if ad is None:
            raise HTTPError(404, 'Ad not found')
        for key, value in validated.items():
            setattr(ad, key, value)
        await session.commit()
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'owner': ad.owner,
        })


async def delete_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info['id'])
    async with Session() as session:
        ad = await session.get(AdModel, ad_id)
        if ad is None:
            raise HTTPError(404, 'Ad not found')
        await session.delete(ad)
        await session.commit()
        return web.json_response({'status': 'success'})