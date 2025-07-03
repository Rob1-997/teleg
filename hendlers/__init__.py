from aiogram import Router

from .admin import router as admin_router
from .hendler import router as reg_router
from .support_admin import router as support_admin_router
from .support_user import router as support_user_router
from .edit_profile import router as profile_router
from .search import router as search_router
from .chat import router as chat_router
from .blocks import router as blocks_router
from .language import router as language_router
from .messages import router as messages_router


# Один объект, в котором собраны все маршруты
all_routers = Router()
all_routers.include_router(admin_router)
all_routers.include_router(reg_router)
all_routers.include_router(support_admin_router)
all_routers.include_router(support_user_router)
all_routers.include_router(profile_router)
all_routers.include_router(search_router)
all_routers.include_router(chat_router)
all_routers.include_router(blocks_router)
all_routers.include_router(language_router)
all_routers.include_router(messages_router)


# Чтобы import * работал
__all__ = ("all_routers",)