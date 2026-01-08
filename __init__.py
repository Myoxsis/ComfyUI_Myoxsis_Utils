from .nodes import ReadImageMetadata, SaveImageWithMetadata

NODE_CLASS_MAPPINGS = {
    "SaveImageWithMetadata": SaveImageWithMetadata,
    "ReadImageMetadata": ReadImageMetadata,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageWithMetadata": "Save Image (Metadata)",
    "ReadImageMetadata": "Read Image Metadata",
}
