# I-003: ADV20重新评分, 付费调用前冻结

唯一judge模型ID: anthropic/claude-opus-5.5, 通过已有OpenRouter key. 不更换模型, 不重新生成Raw/Expert Prompt/Full答案. 20题 × 3条件rubric共60次, 两个Full基线pair各20题 × 正反顺序共80次, 共140个主要请求.

原样调用收到的llm_judge.py build_rubric_prompt / build_pairwise_prompt, 与论文Listing1/2对应; rubric不截断输出, pairwise沿用原函数每份输出前3000字符. 不添加条件标签、评价暗示或新rubric. JSON解析只移除包住整个返回的最外层```json/```代码围栏, 不提取内部子串或手工填值. max_tokens1024沿用原judge helper. Claude目录不支持temperature, 请求不传, 服务端实际值unknown. 不启用工具或额外reasoning设置.

预算: 官方目录2026-11-12查询结果CLAUDE_MODEL_CATALOG_I003.json, 最保守输入费率含1小时cache写价取0.000008 USD/token, 输出0.00002 USD/token. 用每个实际prompt的UTF8字节数+2048个协议封装token作为保守输入额度, 输出额度1024, 计算140次主要调用预算上界11.200208美元, 不是实际账单或研究结果估计. 低于I-003的15美元门槛. 全部调用连重试按此上界累计不超过15; 每个解析失败最多额外2次, 仅在为其余主要调用保留预算后仍有余量时重试. 没有回执的实际费用写unknown. 不充值.

每次保存原始请求JSON与原始响应字节, JSONL逐次保留成功/失败/解析原因/时间/模型ID及返回model/usage. 每份原输出UTF8 SHA256、pair可见前3000字符hash、完整prompt和request body hash都记录. 源文件hash与请求对应, 不复用旧评分.

统计: overall为原5个通用维度算术平均, family-specific两维另列. Full减两基线逐题差、mean/10000次按题bootstrap95%CI/高低平, seed20261112. 若评分缺失, 不补值, 使用完整配对题并报告分母. Pairwise逐题同时列Full在A和B的结果; 两次Full赢、两次基线赢、两次tie、tie混合/相互矛盾、每个顺序的选A比例及位置一致率. 失败不当tie. 不改统计以追求正结果.

旧Full评分按I-003标为代理输出的审计记录, 不用于修订稿任何Full结论. 新judge成功后才用新ADV统计; 如果不完成或跳过, 删除修订稿LLM-judge比较, 在报告说明待用户决定. 与SkillsBench的串行Profy运行可以并行, 此judge进程自身串行.
