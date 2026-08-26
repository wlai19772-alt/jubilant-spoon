Prompt 文件使用说明

1. 存放位置：所有 prompt 文本放在 `prompts/` 目录。
2. 文件命名：每个 prompt 使用 `name.txt` 存放文本，例如 `script_generation.txt`。
3. 占位符：可以在 prompt 中使用 `{var}` 形式的占位符，调用时通过变量字典替换。
   - 示例：在 prompt 中写入 `原始文本：{script}`，加载时传入 `{"script": "内容"}` 即可替换。
4. 元数据（可选）：如果需要为 prompt 添加说明、版本等元数据，可创建 `{name}.meta.json`，例如 `script_generation.meta.json`，内容为 JSON 格式：
   {
     "description": "用于剧本生成的 prompt",
     "version": "1.0"
   }
5. 可视化与版本控制：Prompt 文本为纯文本文件，便于使用 git 管理与多人协作。

注意：Prompt 的语法应避免未成对的大括号，如果必须使用大括号请用替代符号或在调用替换前进行转义处理。