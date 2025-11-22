from .results import res
from .check_answers import user_router

def register_user_handlers(dp):
    dp.include_router(user_router)
    dp.include_router(res)