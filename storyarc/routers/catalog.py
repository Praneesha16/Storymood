from fastapi import APIRouter

import catalog
from providers import registry

router = APIRouter()


@router.get("", summary="Options the app can offer, plus which providers are active")
async def get_catalog():
    """Everything the frontend needs to render its choices. Never includes API keys."""
    providers = registry.describe()
    return {**catalog.public(providers["tts"]["provider"]), "providers": providers}
