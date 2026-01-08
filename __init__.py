from .nodes import (
    FindLoraTriggerWord,
    LoraTriggerWordConditioning,
    ReadImageMetadata,
    SaveImageWithMetadata,
)

NODE_CLASS_MAPPINGS = {
    "SaveImageWithMetadata": SaveImageWithMetadata,
    "ReadImageMetadata": ReadImageMetadata,
    "FindLoraTriggerWord": FindLoraTriggerWord,
    "LoraTriggerWordConditioning": LoraTriggerWordConditioning,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageWithMetadata": "Save Image (Metadata)",
    "ReadImageMetadata": "Read Image Metadata",
    "FindLoraTriggerWord": "Find LoRA Trigger Word",
    "LoraTriggerWordConditioning": "LoRA Trigger Conditioning",
}
