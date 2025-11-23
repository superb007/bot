from .results import res
from .check_answers import user_router
from .onboarding import onboarding_router

def register_user_handlers(dp):
    dp.include_router(user_router)
    dp.include_router(res)
    dp.include_router(onboarding_router)