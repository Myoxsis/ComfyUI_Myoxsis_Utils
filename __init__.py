from aiohttp import web
from server import PromptServer

from .nodes import (
    LoraTriggerWordConditioning,
    ReadImageMetadata,
    SaveImageWithMetadata,
    _build_trigger_map,
    _load_lora_trigger_data,
)

WEB_DIRECTORY = "./web"


@PromptServer.instance.routes.get("/myoxsis-utils/lora-triggers")
async def get_lora_triggers(request):
    trigger_data = _load_lora_trigger_data()
    return web.json_response(_build_trigger_map(trigger_data))

NODE_CLASS_MAPPINGS = {
    "SaveImageWithMetadata": SaveImageWithMetadata,
    "ReadImageMetadata": ReadImageMetadata,
    "LoraTriggerWordConditioning": LoraTriggerWordConditioning,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageWithMetadata": "Save Image (Metadata)",
    "ReadImageMetadata": "Read Image Metadata",
    "LoraTriggerWordConditioning": "LoRA Trigger Conditioning",
}
