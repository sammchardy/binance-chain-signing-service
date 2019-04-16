from typing import Dict, List, Optional
from pydantic import BaseSettings, SecretStr

from binance_chain.environment import BinanceEnvironment
from binance_chain.wallet import Wallet
from binance_chain.http import AsyncHttpApiClient

from api.constants.constants import WalletPermission


class UserWalletSettings(BaseSettings):
    wallet_name: str
    permissions: List[WalletPermission]


class UserSettings(BaseSettings):
    username: str
    password_hash: SecretStr
    wallet_permissions: List[UserWalletSettings]

    def get_wallet_info(self, wallet_name: Optional[str] = None):
        config = ServiceConfig()
        wallets = []
        for w_name, wallet in config.wallets.items():
            if wallet_name and w_name != wallet_name:
                continue
            wc: Dict = wallet.asdict()

            # work out permissions
            wc['permissions'] = list(set(wc['permissions']).intersection(set(self.get_wallet_permissions(w_name))))
            if len(wc['permissions']):
                wallets.append(wc)
        return wallets

    def get_wallet_permissions(self, wallet_name) -> List[WalletPermission]:
        for wallet in self.wallet_permissions:
            if wallet.wallet_name != wallet_name:
                continue
            return wallet.permissions
        return []

    def has_wallet_permission(self, wallet_name: str, permission: WalletPermission) -> bool:
        return permission in self.get_wallet_permissions(wallet_name)


class WalletSettings(BaseSettings):
    private_key: SecretStr
    name: str
    env_name: str = 'PROD'
    env: Optional[BinanceEnvironment] = None
    ip_whitelist: Optional[List[str]]
    permissions: List[WalletPermission]


class Settings(BaseSettings):
    wallets: List[WalletSettings]
    users: List[UserSettings]
    secret_key: SecretStr = 'secret_key'
    access_token_expiry_minutes: int = 100080


class WalletConfig:
    def __init__(self, wallet_settings: WalletSettings):

        self._settings = wallet_settings

        w_env = BinanceEnvironment.get_production_env()
        if wallet_settings.env_name == 'TESTNET':
            w_env = BinanceEnvironment.get_testnet_env()

        self._wallet = Wallet(private_key=wallet_settings.private_key.get_secret_value(), env=w_env)

        self._http_client: Optional[AsyncHttpApiClient] = None

    def ip_authorised(self, ip_address: str):
        if not self.ip_whitelist:
            return True
        if len(self.ip_whitelist) and self.ip_whitelist[0] == '*':
            return True
        return ip_address in self.ip_whitelist

    def has_permission(self, permission: WalletPermission):
        return permission in self.permissions

    def asdict(self) -> Dict:
        return {
            'name': self.name,
            'permissions': self.permissions,
            'env': self._settings.env_name,
            'address': self._wallet.address,
            'public_key': self._wallet.public_key_hex
        }

    @property
    def name(self):
        return self._settings.name

    @property
    def ip_whitelist(self):
        return self._settings.ip_whitelist

    @property
    def permissions(self):
        return self._settings.permissions

    @property
    def env(self):
        return self._wallet.env

    @property
    def wallet(self):
        return self._wallet

    @property
    async def http_client(self) -> AsyncHttpApiClient:
        if not self._http_client:
            self._http_client = await AsyncHttpApiClient.create(env=self.env)

        return self._http_client

    async def broadcast_msg(self, hex_data: str, sync: bool = False):
        http_client = await self.http_client
        await http_client.broadcast_hex_msg(hex_data, sync=sync)


class ServiceConfig:
    instance = None

    class __ServiceConfig:
        def __init__(self):
            self._settings: Optional[Settings] = None
            self._wallets: Optional[Dict[str, WalletConfig]] = None

        def initialise_config(self, config: Dict):
            self._settings = Settings(**config)

            self._wallets: Dict[str, WalletConfig] = {w.name: WalletConfig(w) for w in self._settings.wallets}

        async def get_wallet(self, wallet_name: Optional[str] = None, initialise=True) -> Optional[WalletConfig]:
            if not wallet_name:
                return None

            wallet = self._wallets.get(wallet_name, None)
            if not wallet:
                return None

            if initialise:
                wallet.wallet.initialise_wallet()
            return wallet

        @property
        def settings(self) -> Settings:
            return self._settings

        @property
        def wallets(self) -> Dict[str, WalletConfig]:
            return self._wallets

        @property
        def users(self) -> List[UserSettings]:
            return self._settings.users

    def __init__(self):
        if not ServiceConfig.instance:
            ServiceConfig.instance = ServiceConfig.__ServiceConfig()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    @classmethod
    def initialise_config(cls, config: Dict):
        ServiceConfig.instance.initialise_config(config)
