from .nodes import LoraTriggerWordConditioning, ReadImageMetadata, SaveImageWithMetadata

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
