# feedback-loop

输入一条完整的模型执行轨迹，输出针对这条轨迹、有证据支持的反馈。

轨迹保留任务、规则、模型行为、工具返回与最终输出。每个反馈点说明问题、位置、证据、解释和可执行的建议。证据不足时，明确说明缺少的信息。

## 当前实验

[Counsel 十条轨迹实验](experiments/counsel-10/README.md)包含：

- 5 条数据分析轨迹和 5 条零售客服轨迹，保留原始 JSON 和便于阅读的消息视图。
- 共用的[反馈提示词](experiments/counsel-10/prompt.txt)与逐条候选反馈。
- 独立保存的数据集人工元评价，以及候选反馈的逐项审阅记录。
- 数据来源、固定版本、抽样规则、内容哈希与引用核验脚本。

这是对“从一条轨迹生成有依据的反馈”的小规模探索。审阅记录由模型辅助完成，数据集的人工元评价作为对照；这里的候选反馈不是人工标准答案。建议尚未在原任务环境执行验证。

## 查看和核验

需要 Python 3.10 或以上，仅使用标准库。

```powershell
python scripts/check_counsel_experiment.py
```

该命令检查输入哈希、逐字证据引用、记录完整性及候选反馈是否与冻结版本一致。反馈在语义上是否正确，需要结合原始轨迹和审阅记录判断。

重新获取同一版本的数据样本：

```powershell
python scripts/prepare_counsel_sample.py
```

数据来自 [AtlaAI/Counsel](https://huggingface.co/datasets/AtlaAI/counsel)，固定版本为 `97801e8a9dfece812225035815c100a9ff21f5a4`。上游数据卡声明 MIT 许可，原数据卡保存在实验的 `reference/` 目录中。这些是模型在基准任务中的执行记录。
