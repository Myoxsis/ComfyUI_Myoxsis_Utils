app.registerExtension({
  name: "ComfyUI_Myoxsis_Utils.LoraTriggerUI",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData?.name !== "LoraTriggerWordConditioning") {
      return;
    }

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      onNodeCreated?.apply(this, arguments);

      const loraWidget = this.widgets?.find((widget) => widget.name === "lora_name");
      const triggerWidget = this.widgets?.find(
        (widget) => widget.name === "trigger_words"
      );
      const yamlWidget = this.widgets?.find((widget) => widget.name === "yaml_path");

      if (!loraWidget || !triggerWidget) {
        return;
      }

      const updateTriggerOptions = async () => {
        const selectedLora = loraWidget.value ?? "";
        const yamlPath = yamlWidget?.value ?? "";
        const url = new URL("/myoxsis-utils/lora-triggers", window.location.origin);
        if (yamlPath) {
          url.searchParams.set("yaml_path", yamlPath);
        }

        let triggerMap = {};
        try {
          const response = await fetch(url.toString());
          if (!response.ok) {
            return;
          }
          triggerMap = (await response.json()) || {};
        } catch (error) {
          console.warn("Failed to load LoRA trigger words", error);
          return;
        }

        const triggerWords = triggerMap[selectedLora] || [];
        triggerWidget.options ??= {};
        triggerWidget.options.config ??= {};
        triggerWidget.options.config.multi_select = true;
        triggerWidget.options.values = triggerWords;

        const current = Array.isArray(triggerWidget.value)
          ? triggerWidget.value
          : triggerWidget.value
          ? [triggerWidget.value]
          : [];
        const allowed = new Set(triggerWords);
        triggerWidget.value = current.filter((item) => allowed.has(item));

        this.setDirtyCanvas(true, true);
      };

      loraWidget.callback = updateTriggerOptions;
      if (yamlWidget) {
        yamlWidget.callback = updateTriggerOptions;
      }
      updateTriggerOptions();
    };
  },
});
