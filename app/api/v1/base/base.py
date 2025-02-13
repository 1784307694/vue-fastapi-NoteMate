from datetime import datetime, timedelta, timezone
import random
import aiohttp

from fastapi import APIRouter, Depends, File, UploadFile
from redis import Redis

from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth, RedisControl
from app.models.admin import Api, Menu, Role, User
from app.schemas.base import Fail, Success
from app.schemas.login import *
from app.schemas.users import BaseUserCreate, UpdateBaseUserInfo, UpdatePassword
from app.core.config import settings
from app.utils.jwt import create_access_token
from app.utils.password import get_password_hash, verify_password
from app.utils.email import send_email
from app.utils.redis import RedisUtils
from app.utils.redis_cache import RedisCache


router = APIRouter()

@router.post("/create", summary="创建用户")
async def create_user(
    user_in: BaseUserCreate,
    redis: Redis = Depends(RedisControl.get_redis)
):
    """创建新用户
    
    创建用户并分配角色
    
    Args:
        user_in: 用户创建模型, 包含:
            - 基本信息(用户名、邮箱等)
            - 角色ID列表
            
    Returns:
        Success/Fail: 创建成功或失败的响应对象
            - 如果邮箱已存在, 返回400错误
            - 创建成功返回成功消息
            
    Note:
        创建用户后会自动更新用户的角色关系
    """
    # 检查手机号是否已存在
    if user_in.phone:
        user = await user_controller.get_by_phone(user_in.phone)
    # 检查用户名是否已存在
    if user_in.username:
        user = await user_controller.get_by_username(user_in.username)
    # 检查邮箱是否已存在
    if user_in.email:
        user = await user_controller.get_by_email(user_in.email)
    if user:
        return Fail(code=400, msg="系统中已存在用户")
    
    # 检查验证码是否正确
    if user_in.code:
        code = await RedisUtils.cache_get(redis, user_in.email)
        if str(code) != str(user_in.code):  # 转换为字符串进行比较
            return Fail(code=400, msg="验证码错误")
    # 创建用户
    role_ids = []
    role = await Role.filter(name="普通用户").first()
    role_ids.append(role.id)
    new_user = await user_controller.create_user(obj_in=user_in)
    # 更新用户角色
    await RedisUtils.cache_delete(redis, user_in.email)
    await user_controller.update_roles(new_user, role_ids)
    
    # 清除相关缓存
    await RedisCache.clear_user_cache(redis, new_user.id)
    return Success(msg="创建成功")


@router.post("/access_token", summary="获取token")
async def login_access_token(credentials: CredentialsSchema):
    user: User = await user_controller.authenticate(credentials)
    await user_controller.update_last_login(user.id)
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + access_token_expires

    data = JWTOut(
        access_token=create_access_token(
            data=JWTPayload(
                user_id=user.id,
                username=user.username,
                is_superuser=user.is_superuser,
                exp=expire,
            )
        ),
        username=user.username,
    )
    return Success(data=data.model_dump())


@router.get("/userinfo", summary="查看用户信息", dependencies=[DependAuth])
async def get_userinfo():
    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get(id=user_id)
    data = await user_obj.to_dict(exclude_fields=["password"])
    return Success(data=data)


@router.get("/usermenu", summary="查看用户菜单", dependencies=[DependAuth])
async def get_user_menu(redis: Redis = Depends(RedisControl.get_redis)):
    user_id = CTX_USER_ID.get()
    
    # 先尝试从缓存获取
    cached_menus = await RedisCache.get_user_menus(redis, user_id)
    if cached_menus:
        return Success(data=cached_menus)
    
    # 缓存未命中，从数据库查询
    user_obj = await User.filter(id=user_id).first()
    menus: list[Menu] = []
    if user_obj.is_superuser:
        menus = await Menu.all()
    else:
        role_objs: list[Role] = await user_obj.roles
        for role_obj in role_objs:
            menu = await role_obj.menus
            menus.extend(menu)
        menus = list(set(menus))
        
    parent_menus: list[Menu] = []
    for menu in menus:
        if menu.parent_id == 0:
            parent_menus.append(menu)
            
    res = []
    for parent_menu in parent_menus:
        parent_menu_dict = await parent_menu.to_dict()
        parent_menu_dict["children"] = []
        for menu in menus:
            if menu.parent_id == parent_menu.id:
                parent_menu_dict["children"].append(await menu.to_dict())
        res.append(parent_menu_dict)
    
    # 写入缓存
    await RedisCache.set_user_menus(redis, user_id, res)
    return Success(data=res)


@router.get("/userapi", summary="查看用户API", dependencies=[DependAuth])
async def get_user_api(redis: Redis = Depends(RedisControl.get_redis)):
    user_id = CTX_USER_ID.get()
    
    # 先尝试从缓存获取
    permissions = await RedisCache.get_user_permissions(redis, user_id)
    if permissions:
        return Success(data=permissions)
    
    # 缓存未命中，从数据库查询
    user_obj = await User.filter(id=user_id).first()
    if user_obj.is_superuser:
        api_objs: list[Api] = await Api.all()
        apis = [api.method.lower() + api.path for api in api_objs]
    else:
        role_objs: list[Role] = await user_obj.roles
        apis = []
        for role_obj in role_objs:
            api_objs: list[Api] = await role_obj.apis
            apis.extend([api.method.lower() + api.path for api in api_objs])
        apis = list(set(apis))
    
    # 写入缓存
    await RedisCache.set_user_permissions(redis, user_id, apis)
    return Success(data=apis)


@router.post("/updateUserInfo", summary="修改用户信息", dependencies=[DependAuth])
async def update_user_info(req_in: UpdateBaseUserInfo, redis: Redis = Depends(RedisControl.get_redis)):
    user_id = CTX_USER_ID.get()
    user = await user_controller.get(user_id)
    if req_in.email:
        user.email = req_in.email
    if req_in.phone:
        user.phone = req_in.phone
    if req_in.username:
        user.username = req_in.username
    await user.save()
    
    # 清除用户相关缓存
    await RedisCache.clear_user_cache(redis, user_id)
    return Success(msg="修改成功")


@router.post("/update_password", summary="修改密码")
async def update_user_password(req_in: UpdatePassword, redis: Redis = Depends(RedisControl.get_redis)):
    user = await user_controller.get_by_email(req_in.email)
    if not user:
        return Fail(msg="邮箱未注册")
    code = await RedisUtils.cache_get(redis, req_in.email)
    if str(code) != str(req_in.code):
        return Fail(msg="验证码错误")
    user.password = get_password_hash(req_in.password)
    await user.save()
    
    # 清除验证码和用户相关缓存
    await RedisUtils.cache_delete(redis, req_in.email)
    await RedisCache.clear_user_cache(redis, user.id)
    return Success(msg="修改成功")


@router.get("/send_email_code", summary="发送邮件验证码")
async def send_email_code(email: str,redis: Redis = Depends(RedisControl.get_redis)):
    # 检查邮箱是否存在
    user = await user_controller.get_by_email(email)
    # 检查redis是否已存在验证码
    if await RedisUtils.cache_get(redis, email):
        return Fail(msg="邮件发送过于频繁")
    code = random.randint(100000, 999999)
    print(code)
    await send_email(email, "[验证码]", f"您的验证码是：{code}")
    # 存储验证码到Redis
    store_success = await RedisUtils.cache_set(redis, email, str(code), expire=60 * 10)  # 确保存储为字符串
    if not store_success:
        return Fail(msg="验证码存储失败")
    return Success(msg="邮件发送成功")


@router.post("/upload/image", summary="上传图片", dependencies=[DependAuth])
async def upload_image(file: UploadFile = File(...)):
    """上传图片到Hello图床
    
    Args:
        file: 要上传的图片文件
        
    Returns:
        Success: 上传成功响应
            - url: 图片URL
            - thumbnail_url: 缩略图URL
            - markdown: Markdown格式链接
            - delete_url: 删除URL
    """
    if not file.content_type.startswith('image/'):
        return Fail(msg="只能上传图片文件")
        
    try:
        # 读取文件内容
        content = await file.read()
        
        # 准备上传到图床
        async with aiohttp.ClientSession() as session:
            # 构建multipart表单
            data = aiohttp.FormData()
            data.add_field(
                'file',  # 必须使用file作为字段名
                content,
                filename=file.filename,
                content_type=file.content_type
            )
            
            # 发送上传请求
            headers = {
                'Authorization': 'Bearer 961|bL8fhCRyMkA3tYAS6OkmdPtxL6L6cYIKB9AP2IrT',
                'Accept': 'application/json',  # 必须设置为application/json
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            try:
                async with session.post(
                    'https://www.helloimg.com/api/v1/upload',  # API基础URL + /upload
                    data=data,
                    headers=headers
                ) as response:
                    response_text = await response.text()
                    print(f"Response status: {response.status}")
                    print(f"Response text: {response_text}")
                    
                    if response.status != 200:
                        return Fail(msg=f"上传失败: HTTP {response.status} - {response_text}")
                    
                    try:
                        result = await response.json()
                    except Exception as e:
                        return Fail(msg=f"解析响应失败: {response_text}")
                    
                    if isinstance(result, dict):
                        if not result.get('status'):
                            return Fail(msg=result.get('message', '上传失败'))
                        
                        data = result.get('data', {})
                        links = data.get('links', {})
                        if isinstance(links, dict):
                            return Success(data={
                                'url': links.get('url'),
                                'thumbnail_url': links.get('thumbnail_url'),
                                'markdown': links.get('markdown'),
                                'delete_url': links.get('delete_url')
                            })
                    
                    return Fail(msg=f"无效的响应格式: {result}")
                    
            except aiohttp.ClientError as e:
                return Fail(msg=f"网络请求失败: {str(e)}")
                
    except Exception as e:
        return Fail(msg=f"上传失败: {str(e)}")
    finally:
        await file.close()








