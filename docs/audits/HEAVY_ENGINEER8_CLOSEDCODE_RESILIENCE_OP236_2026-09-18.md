# HE8 Operation Resilience — Op236

Status: GREEN / native provider tool-call compatibility proved
Operation: HEAVY-ENGINEER8-CLOSEDCODE-OP236.probe-provider-native-tool-call-compatibility
Relay status: OK
Exit code: 0

Repository:
- branch: closedcode/android-cleanroom-opencode-mobile-20260916
- fast-forwarded local tree to f242b720b476ecd8a26ed571e3707752735313ce
- final worktree clean

NVIDIA:
- exact model: nvidia/nemotron-3-ultra-550b-a55b
- nonstream HTTP 200
- finish_reason=tool_calls
- native function call returned:
  - name=closedcode_probe
  - arguments={"value":"PROBE_OK"}
- capability=GREEN

Z.AI:
- exact model: glm-4.7-flash
- nonstream HTTP 200
- finish_reason=tool_calls
- native function call returned:
  - name=closedcode_probe
  - arguments={"value":"PROBE_OK"}
- capability=GREEN

Overall:
- TOOL_CALL_PROBE_OVERALL=GREEN
- no text-command convention is required for a ClosedCode-native agent loop
- both provider paths support standard function/tool calling compatible with a structured tool loop

Protected/live boundaries:
- no GPT-Termux-Relay mutation
- no live OpenCode runtime replacement

Next bounded target:
Implement a ClosedCode-native agent loop backed by the already-proved workspace and Termux capabilities. Qualify it first against a disposable scratch workspace before routing Android provider turns through it.
