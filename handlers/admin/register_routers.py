from .running_tests import r_test
from .create_test import admin_router
from .archive import arch
from .stats import stater


def register_admin_handlers(dp):
    dp.include_router(admin_router)
    dp.include_router(r_test)
    dp.include_router(arch)
    dp.include_router(stater)