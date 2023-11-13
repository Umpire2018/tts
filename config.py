from dynaconf import Dynaconf
from azure.cognitiveservices.speech import SpeechConfig

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.toml', '.secrets.toml'],
)

speech_config = SpeechConfig(subscription=settings.subscription_key, region=settings.service_region)
