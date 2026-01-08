import json
import os
from datetime import datetime

import numpy as np
import yaml
from PIL import Image
from PIL.PngImagePlugin import PngInfo


def _tensor_to_pil(image_tensor):
    if hasattr(image_tensor, "cpu"):
        image_tensor = image_tensor.cpu()
    if hasattr(image_tensor, "numpy"):
        image_tensor = image_tensor.numpy()
    if image_tensor.ndim == 4:
        image_tensor = image_tensor[0]
    image_array = np.clip(image_tensor * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(image_array)


class SaveImageWithMetadata:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0}),
                "steps": ("INT", {"default": 20, "min": 1}),
                "cfg": ("FLOAT", {"default": 7.5, "min": 0.0}),
                "sampler_name": ("STRING", {"default": ""}),
                "scheduler": ("STRING", {"default": ""}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0}),
                "output_dir": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "file_paths")
    FUNCTION = "save_images"
    OUTPUT_NODE = True

    def save_images(
        self,
        images,
        prompt,
        seed,
        steps,
        cfg,
        sampler_name,
        scheduler,
        denoise,
        output_dir,
    ):
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)

        metadata = {
            "prompt": prompt,
            "ksampler": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "denoise": denoise,
            },
        }
        metadata_json = json.dumps(metadata, ensure_ascii=False)
        pnginfo = PngInfo()
        pnginfo.add_text("comfyui_metadata", metadata_json)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_paths = []
        for index, image in enumerate(images):
            pil_image = _tensor_to_pil(image)
            filename = f"comfyui_{timestamp}_{index}.png"
            file_path = os.path.join(output_dir, filename)
            pil_image.save(file_path, pnginfo=pnginfo)
            file_paths.append(file_path)

        return (images, json.dumps(file_paths))


class ReadImageMetadata:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_path": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("metadata",)
    FUNCTION = "read_metadata"

    def read_metadata(self, image_path):
        if not image_path:
            return ("",)
        with Image.open(image_path) as image:
            metadata = image.info.get("comfyui_metadata")
            if metadata is None:
                metadata = json.dumps(image.info, ensure_ascii=False)
        return (metadata,)


class FindLoraTriggerWord:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora_name": ("STRING", {"default": ""}),
            },
            "optional": {
                "yaml_path": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("trigger_word", "found")
    FUNCTION = "find_trigger"

    def find_trigger(self, lora_name, yaml_path=""):
        if not lora_name:
            return ("", False)

        if not yaml_path:
            yaml_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "lora_triggers.yaml"
            )

        if not os.path.exists(yaml_path):
            return ("", False)

        with open(yaml_path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        if isinstance(data, dict) and "lora_triggers" in data:
            data = data.get("lora_triggers") or {}

        if not isinstance(data, dict):
            return ("", False)

        trigger_word = data.get(lora_name)
        if not trigger_word:
            return ("", False)

        return (str(trigger_word), True)
