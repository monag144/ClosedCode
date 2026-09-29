from pathlib import Path

path = Path("apps/closedcode-android/src/com/monag/closedcode/mobile/ClosedCodeApi.java")
text = path.read_text()

line = '                body.put("autonomy", autonomy == null ? "ask" : autonomy);\n'
model_line = '                body.put("model", modelId);\n'
agent_marker = '    public void streamAgentPrompt(\n'

count = text.count(line)
if count != 1:
    raise RuntimeError(f"expected exactly one misplaced autonomy line, found {count}")

agent_start = text.find(agent_marker)
if agent_start < 0:
    raise RuntimeError("streamAgentPrompt marker not found")

# Remove the one misplaced occurrence wherever it currently is.
text = text.replace(line, "", 1)

# Insert only inside streamAgentPrompt, immediately after that method's model field.
model_pos = text.find(model_line, agent_start)
if model_pos < 0:
    raise RuntimeError("agent model body field not found")
insert_pos = model_pos + len(model_line)
text = text[:insert_pos] + line + text[insert_pos:]

# Strong postconditions.
if text.count(line) != 1:
    raise RuntimeError("autonomy line count is not exactly one after repair")
agent_start = text.find(agent_marker)
autonomy_pos = text.find(line, agent_start)
if autonomy_pos < 0:
    raise RuntimeError("autonomy field was not inserted in streamAgentPrompt")
provider_start = text.find("    public void streamProviderPrompt(\n")
if provider_start >= 0 and provider_start < agent_start:
    provider_region = text[provider_start:agent_start]
    if line in provider_region:
        raise RuntimeError("autonomy field remains in streamProviderPrompt")

path.write_text(text)
print("ANDROID_AUTONOMY_PLACEMENT_REPAIR=GREEN")
