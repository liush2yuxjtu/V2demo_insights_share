# Install By Copy-Paste

这个仓库已经是面向互联网分发的版本。

如果你只是想最快复现，不需要自己拼命令，直接复制下面内容即可。

## Option A: Terminal Quick Install

```bash
git clone https://github.com/liush2yuxjtu/V2demo_insights_share.git
cd V2demo_insights_share
./demos/insights-share/demo_docs/final_case/verify_without_claude_p.sh
./demos/insights-share/demo_docs/final_case/verify_with_claude_p.sh
```

你会得到两个清晰结果：

- `without`：只有 `prompt.md`，Claude 会明确说没有 insight
- `with`：安装了 `skills/insights-wiki/SKILL.md` 和第一条共享 insight 后，Claude 会给出三行结构化答案

## Option B: Claude Code Prompt

把下面整段直接贴进 Claude Code：

```text
请帮我安装并验证这个 demo。

1. git clone https://github.com/liush2yuxjtu/V2demo_insights_share.git
2. 进入仓库目录
3. 先运行：
   ./demos/insights-share/demo_docs/final_case/verify_without_claude_p.sh
4. 再运行：
   ./demos/insights-share/demo_docs/final_case/verify_with_claude_p.sh
5. 最后告诉我：
   - 两次测试是不是同一个 init prompt
   - without 的结果为什么差
   - with 的结果为什么更好
```

## Option C: Full tmux Reproduction

如果你要完整复现 Claude `/export` 会话，而不是只看 `claude -p` 输出：

```bash
git clone https://github.com/liush2yuxjtu/V2demo_insights_share.git
cd V2demo_insights_share
./demos/insights-share/demo_docs/final_case/reproduce_without_tmux.sh
./demos/insights-share/demo_docs/final_case/reproduce_with_tmux.sh
```

这会重新生成：

- `demos/insights-share/demo_docs/final_case/claude_without_client_skill_export.md`
- `demos/insights-share/demo_docs/final_case/claude_with_client_skill_export.md`

## Most Important Files

- `index.html`
- `story.md`
- `demos/insights-share/demo_docs/final_case/claude_without_client_skill_export.md`
- `demos/insights-share/demo_docs/final_case/claude_with_client_skill_export.md`
- `demos/insights-share/demo_docs/final_case/verify_without_claude_p_output.txt`
- `demos/insights-share/demo_docs/final_case/verify_with_claude_p_output.txt`
