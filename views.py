from aiohttp import web
import pydantic
from models import Session, UserModel, AdModel, CreateUserModel, LoginUserModel, CreateAdModel, UpdateAdModel, HTTPError
from auth import hash_password, check_password, create_access_token, decode_token
from sqlalchemy import select
from sqlalchemy.orm import selectinload  # ИЗМЕНЕНО: добавлен импорт для загрузки

async def register(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        raise HTTPError(400, 'Invalid JSON')

    try:
        validated = CreateUserModel(**data).model_dump()
    except pydantic.ValidationError as er:
        raise HTTPError(400, er.errors())

    async with Session() as session:
        existing = await session.execute(select(UserModel).where(UserModel.username == validated['username']))
        if existing.scalar_one_or_none():
            raise HTTPError(409, 'Username already exists')

        user = UserModel(
            username=validated['username'],
            password_hash=hash_password(validated['password'])
        )
        session.add(user)
        await session.commit()
        return web.json_response({'id': user.id, 'username': user.username}, status=201)


async def login(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        raise HTTPError(400, 'Invalid JSON')

    try:
        validated = LoginUserModel(**data).model_dump()
    except pydantic.ValidationError as er:
        raise HTTPError(400, er.errors())

    async with Session() as session:
        user = await session.execute(select(UserModel).where(UserModel.username == validated['username']))
        user = user.scalar_one_or_none()
        if not user or not check_password(validated['password'], user.password_hash):
            raise HTTPError(401, 'Invalid username or password')

        token = create_access_token({'sub': user.id, 'username': user.username})
        return web.json_response({'access_token': token, 'token_type': 'bearer'})


async def get_current_user(request: web.Request) -> int:
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPError(401, 'Missing or invalid token')
    token = auth_header[7:]
    try:
        payload = decode_token(token)
        user_id = payload.get('sub')
        if not user_id:
            raise HTTPError(401, 'Invalid token')
        return int(user_id)
    except Exception:
        raise HTTPError(401, 'Invalid token')


# ИЗМЕНЕНО: функция для получения списка объявлений (новый эндпоинт)
async def get_ads_list(request: web.Request) -> web.Response:
    async with Session() as session:
        # Загружаем объявления вместе с пользователем (для owner)
        query = select(AdModel).options(selectinload(AdModel.user))
        result = await session.execute(query)
        ads = result.scalars().all()
        if not ads:
            return web.json_response(status=204)  # пустой список → 204 No Content
        ads_data = [
            {
                'id': ad.id,
                'title': ad.title,
                'description': ad.description,
                'created_at': ad.created_at.isoformat(),
                'owner': ad.user.username
            }
            for ad in ads
        ]
        return web.json_response(ads_data, status=200)


async def get_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info['id'])
    async with Session() as session:
        # ИЗМЕНЕНО: теперь используем select с selectinload, чтобы загрузить user
        query = select(AdModel).where(AdModel.id == ad_id).options(selectinload(AdModel.user))
        result = await session.execute(query)
        ad = result.scalar_one_or_none()
        if ad is None:
            raise HTTPError(404, 'Ad not found')
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'created_at': ad.created_at.isoformat(),
            'owner': ad.user.username
        })


async def create_ad(request: web.Request) -> web.Response:
    user_id = await get_current_user(request)

    try:
        data = await request.json()
    except Exception:
        raise HTTPError(400, 'Invalid JSON')

    try:
        validated = CreateAdModel(**data).model_dump()
    except pydantic.ValidationError as er:
        raise HTTPError(400, er.errors())

    async with Session() as session:
        ad = AdModel(user_id=user_id, **validated)
        session.add(ad)
        await session.commit()
        await session.refresh(ad, ['user'])  # загружаем связанного пользователя
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'owner': ad.user.username
        }, status=201)


async def patch_ad(request: web.Request) -> web.Response:
    user_id = await get_current_user(request)
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
        if ad.user_id != user_id:
            raise HTTPError(403, 'You can only update your own ads')

        for key, value in validated.items():
            setattr(ad, key, value)
        await session.commit()
        await session.refresh(ad, ['user'])
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'owner': ad.user.username
        })


# ИЗМЕНЕНО: теперь возвращает 204 No Content без тела
async def delete_ad(request: web.Request) -> web.Response:
    user_id = await get_current_user(request)
    ad_id = int(request.match_info['id'])

    async with Session() as session:
        ad = await session.get(AdModel, ad_id)
        if ad is None:
            raise HTTPError(404, 'Ad not found')
        if ad.user_id != user_id:
            raise HTTPError(403, 'You can only delete your own ads')

        await session.delete(ad)
        await session.commit()
        return web.Response(status=204)  # <-- изменено
