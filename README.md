# ComfyUI Myoxsis Utils

Custom ComfyUI nodes focused on metadata handling and LoRA trigger helpers.

## Features

- **SaveImageWithMetadata**: Saves images to disk with embedded ComfyUI metadata.
- **ReadImageMetadata**: Builds a structured JSON summary for prompts, sampler settings, and model info.
- **FindLoraTriggerWord**: Looks up a trigger word for a LoRA name from a YAML file.
- **LoraTriggerWordConditioning**: Builds conditioning tokens from selected trigger words.

## Installation

1. Clone this repository into your ComfyUI `custom_nodes` directory.
2. Restart ComfyUI.

## LoRA trigger configuration

The default trigger list is read from `lora_triggers.yaml` in this repository. You can also pass a custom YAML path to the relevant nodes.

Expected YAML formats:

```yaml
lora_triggers:
  my_lora: "trigger words"
  another_lora:
    - trigger
    - word
```

or

```yaml
my_lora: "trigger words"
another_lora:
  - trigger
  - word
```
