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


def _load_lora_trigger_data(yaml_path):
    if not yaml_path:
        yaml_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "lora_triggers.yaml"
        )

    if not os.path.exists(yaml_path):
        return {}

    with open(yaml_path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if isinstance(data, dict) and "lora_triggers" in data:
        data = data.get("lora_triggers") or {}

    if not isinstance(data, dict):
        return {}

    return data


def _parse_trigger_words(raw_value):
    if isinstance(raw_value, dict):
        return [str(key) for key in raw_value.keys()]

    if isinstance(raw_value, (list, tuple)):
        return [str(item).strip() for item in raw_value if str(item).strip()]

    if isinstance(raw_value, str):
        words = []
        for line in raw_value.splitlines():
            line = line.strip()
            if not line:
                continue
            tag_value = line
            if " " in line:
                tag_value, count = line.rsplit(" ", 1)
                if not count.isdigit():
                    tag_value = line
            tag_value = tag_value.rstrip(":").strip()
            if tag_value:
                words.append(tag_value)
        return words

    return []


def _normalize_trigger_selection(trigger_words):
    if isinstance(trigger_words, str):
        items = [item.strip() for item in trigger_words.split(",")]
    elif isinstance(trigger_words, (list, tuple)):
        items = [str(item).strip() for item in trigger_words]
    else:
        items = []
    return [item for item in items if item]


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
                "image": ("IMAGE",),
                "seed": ("INT", {"default": 0, "min": 0}),
                "steps": ("INT", {"default": 20, "min": 1}),
                "cfg": ("FLOAT", {"default": 7.5, "min": 0.0}),
                "sampler_name": ("STRING", {"default": ""}),
                "scheduler": ("STRING", {"default": ""}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0}),
                "positive_prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "model_name": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("metadata",)
    FUNCTION = "read_metadata"

    def read_metadata(
        self,
        image,
        seed,
        steps,
        cfg,
        sampler_name,
        scheduler,
        denoise,
        positive_prompt,
        negative_prompt,
        model_name,
    ):
        metadata = {
            "prompt": {
                "positive": positive_prompt,
                "negative": negative_prompt,
            },
            "ksampler": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": sampler_name,
                "scheduler": scheduler,
                "denoise": denoise,
            },
            "model": model_name,
        }

        if hasattr(image, "info"):
            existing_metadata = image.info.get("comfyui_metadata")
            if existing_metadata:
                metadata["image_metadata"] = existing_metadata

        return (json.dumps(metadata, ensure_ascii=False),)


class LoraTriggerWordConditioning:
    @classmethod
    def INPUT_TYPES(cls):
        data = _load_lora_trigger_data("")
        lora_names = sorted(data.keys())
        lora_choice = lora_names or [""]
        trigger_choices = []
        if lora_names:
            trigger_choices = _parse_trigger_words(data.get(lora_names[0]))
        return {
            "required": {
                "clip": ("CLIP",),
                "lora_name": (lora_choice,),
                "trigger_words": (
                    trigger_choices,
                    {"default": [], "multi_select": True},
                ),
            },
            "optional": {
                "yaml_path": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    FUNCTION = "build_conditioning"

    def build_conditioning(self, clip, lora_name, trigger_words, yaml_path=""):
        data = _load_lora_trigger_data(yaml_path)
        available_words = _parse_trigger_words(data.get(lora_name)) if data else []
        selected = _normalize_trigger_selection(trigger_words)

        if available_words:
            available_set = {word.lower() for word in available_words}
            selected = [
                word for word in selected if word.lower() in available_set
            ] or selected

        prompt = ", ".join(selected)
        tokens = clip.tokenize(prompt)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
        return ([[cond, {"pooled_output": pooled}]],)
