from core.utils import SharedAPIRootRouter
from voucher.rest import *

# SharedAPIRootRouter is automatically imported in global urls config
router = SharedAPIRootRouter()
router.register(r'voucher/cards', CardViewSet, base_name='voucher_cards')
router.register(r'voucher/wallets', WalletViewSet, base_name='voucher_wallets')
router.register(r'voucher/users', UserViewSet, base_name='voucher_users')
router.register(r'voucher/worklogs', WorkLogViewSet)
router.register(r'voucher/uselogs', UseLogViewSet)
