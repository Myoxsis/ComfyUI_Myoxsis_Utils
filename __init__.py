from .nodes import FindLoraTriggerWord, ReadImageMetadata, SaveImageWithMetadata

NODE_CLASS_MAPPINGS = {
    "SaveImageWithMetadata": SaveImageWithMetadata,
    "ReadImageMetadata": ReadImageMetadata,
    "FindLoraTriggerWord": FindLoraTriggerWord,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageWithMetadata": "Save Image (Metadata)",
    "ReadImageMetadata": "Read Image Metadata",
    "FindLoraTriggerWord": "Find LoRA Trigger Word",
}
