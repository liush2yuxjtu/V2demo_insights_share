# Claude `/export` Examples

这份文件记录了当前仓库里一条真实跑通的 `tmux + Claude Code + /export` 导出链路，不是伪造示例。

## 已实际执行的环境

- 仓库路径：`/Users/m1/projects/V2demo_insights_share`
- `tmux`：`tmux 3.6a`
- `claude`：`Claude Code v2.1.104`
- tmux 会话名：`insights_export_demo`

## 实际执行过的命令

### 1. 创建 tmux 会话并启动 Claude Code

```bash
tmux new-session -d -s insights_export_demo -c /Users/m1/projects/V2demo_insights_share 'claude'
```

### 2. 在 Claude 会话里直接执行第一次 `/export`

```bash
tmux send-keys -t insights_export_demo:0 '/export demos/insights-share/demo_docs/export_examples/claude_session_export.md' Enter
```

这一步已经成功，tmux 屏幕里能看到：

```text
❯ /export
demos/insights-share/demo_docs/export_examples/claude_session_export.md
  ⎿  Conversation exported to: /Users/m1/projects/V2demo_insights_share/demos/insights-share/demo_docs/export_examples/claude_session_export.md
```

### 3. 在同一个 Claude 会话里再发一个真实问题

```bash
tmux send-keys -t insights_export_demo:0 'Summarize the current repo in one short sentence.' Enter
```

Claude 返回的核心内容是：

```text
A knowledge-sharing wiki system with retrieval, evaluation, and CLI tools for managing and accessing structured insights.
```

### 4. 再次执行 `/export`，导出带实际问答内容的会话

```bash
tmux send-keys -t insights_export_demo:0 '/export demos/insights-share/demo_docs/export_examples/claude_session_after_prompt_export.md' Enter
```

tmux 屏幕里能看到：

```text
❯ /export demos/insights-share/demo_docs/export_examples/claude_session_after_prompt_export.md
  ⎿  Conversation exported to:
     /Users/m1/projects/V2demo_insights_share/demos/insights-share/demo_docs/export_examples/claude_session_after_prompt_export.md
```

## 保留下来的实际导出文件

- Claude 首次导出：
  [claude_session_export.md](/Users/m1/projects/V2demo_insights_share/demos/insights-share/demo_docs/export_examples/claude_session_export.md)
- Claude 二次导出，包含真实问答：
  [claude_session_after_prompt_export.md](/Users/m1/projects/V2demo_insights_share/demos/insights-share/demo_docs/export_examples/claude_session_after_prompt_export.md)
- tmux 第一次屏幕抓取：
  [tmux_capture.txt](/Users/m1/projects/V2demo_insights_share/demos/insights-share/demo_docs/export_examples/tmux_capture.txt)
- tmux 第二次屏幕抓取，包含问答和第二次 `/export`：
  [tmux_capture_after_prompt.txt](/Users/m1/projects/V2demo_insights_share/demos/insights-share/demo_docs/export_examples/tmux_capture_after_prompt.txt)

## 你自己复跑时最短命令

如果你只是想自己再做一遍：

```bash
tmux attach -t insights_export_demo
```

进入后直接在 Claude Code 里输入：

```text
/export demos/insights-share/demo_docs/export_examples/my_export.md
```

或者如果想完全从头开始：

```bash
tmux kill-session -t insights_export_demo
tmux new-session -d -s insights_export_demo -c /Users/m1/projects/V2demo_insights_share 'claude'
tmux attach -t insights_export_demo
```

## 结论

这件事已经在当前仓库中真实跑通：

1. `tmux` 会话已创建。
2. `claude` 交互会话已启动。
3. `/export` slash command 已在 Claude 会话内成功执行两次。
4. 导出文件已经落盘到 `demos/insights-share/demo_docs/export_examples/`。
