from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import SecretStr

__all__ = ["config"]


class WriteSettings(BaseSettings):
    # Better instead str (string) use SecretStr
    # for conditional data, for example, tokens, bot token
    BOT_TOKEN: SecretStr
    GA_IDS: SecretStr

    # Beginning with second version pydantic, setting class set through model_config
    # In this case will use file .env, who will be read
    # with encoding UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


class Settings(WriteSettings):
    @property
    def bot_token(self):
        return self.BOT_TOKEN.get_secret_value()

    @property
    def ga_ids(self):
        return tuple(map(int, self.GA_IDS.get_secret_value().split(',')))


# When import it is being created object with value from .env file
config = Settings()
