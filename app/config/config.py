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

            print(f"created wallets: {self._wallets}")

        async def get_wallet(self, wallet_name: Optional[str] = None, initialise=True) -> Optional[WalletConfig]:
            if not wallet_name:
                print('no wallet name')
                return None

            wallet = self._wallets.get(wallet_name, None)
            print(f'got wallet: {wallet}')
            if not wallet:
                return None

            print(f'got wallet.wallet: {wallet.wallet}')
            if initialise:
                wallet.wallet.initialise_wallet()
            print('returning wallet')
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
