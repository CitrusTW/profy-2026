# 先做一个三组小实验

这份代码想先把一件事做完整: 一个AI拿着原来的做事说明练习, 从真实执行里提出修改, 检查修改后有没有变差, 然后拿另一道题考试.

这里是本次新写的研究原型, 参考论文§3.4的候选修改、检查、再启用思路. 它不是袋袋原生evolution, 也不是已经证明有效的论文完整方法. 这次不测跨expert归因.

## 三组分别拿什么

| 名字 | 拿到什么 |
| --- | --- |
| no-skills | 原题和相同开发经验, 不给本项目expert包 |
| with-skills | 同样原题和经验, 再给收到的初始expert包 |
| with-skills-cognilife-method | 同一起点, 再运行本次实际更新原型; 通过检查才使用新版skill |

这里no-skills只表示没有本项目expert包. 袋袋平台本身仍提供基础指令和工具; 空skills参数不保证云端没有其他基础skill. 代码记录可见skill工具调用, 不把看不到的内部状态写成已清空.

三组都用Profy API的gpt-6.1-sol, 每次开自己的session/sandbox. 同一expert identifier作为运行入口. 初始包选收到的01-财务报销管家, 保留原文件, 不改Soul或身份.

## 练习题和考试题

- 练习: SkillsBench的pdf-excel-diff. 核对旧PDF员工记录和新Excel记录.
- 考试: SkillsBench的invoice-fraud-detection. 核对发票、供应商和采购订单.

它们都是文件核对, 但不是同一道题. 这只是一次跨任务小跑, 不能据此说已经验证所有财务工作或长期学习. 练习任务虽然处理员工记录, 用的是财务包可复用的记录核对做法, 不把它写成真实财务生产样本.

考试题的答案、隐藏测试、原评分反馈不会进入更新. 三组考试都能读取同一份原始开发经验, 避免把多给一份经验当成方法进步.

## 第三组真的做了什么

1. 原expert做一次练习, 保存真实工具结果和输出.
2. OpenRouter的openai/gpt-4.1-mini只看公开开发题题面、通过/失败数量、耗时和工具调用次数, 提一个通用工作步骤候选. 私有expert原文、工具结果原文和答案不发给OpenRouter. 原skill只在本机用于体积比较;候选名称在本机填入.
3. 候选再做一次同样练习, 用原pytest评分.
4. 原型只在两项都成立时采用: 开发测试通过数量不下降; skill的UTF-8文件字节数减少.
5. 保存决定和版本后, 才开始三组考试.

这里的字节数只是一种明确的文档体积指标, 不是模型token数, 也不保证更省钱或更快. 时间和真实usage另外记录. 如果候选没通过, 第三组按规则保留旧版, 报告会直接写没有采用新skill, 不假装学习成功.

这不只是写一个prompt后直接叫Full: 代码实际执行了候选前后练习、原评分、采用检查和冻结后的新题测试. 但它仍是新增研究实现, 不冒称复现了产品全部机制.

## 怎么运行

专家包、benchmark和keys都在仓库外面. 这份仓库不提供、也不上传这些文件.

```bash
python -m unittest -v test_pilot.py
python pilot.py --workspace /path/to/CogniLife --out /path/to/local-results --dev-inputs /path/to/pdf-excel-inputs --keys-file /path/to/private-keys.md
```

上面的第二条只是显示配置, 不读key、不调用模型. 确认后在末尾加`--run`才会付费执行. 本轮用户已要求自动运行, 实际启动记录留在结果目录.

所需输入是现有SkillsBench任务目录、收到的expert目录、练习题Dockerfile指定的两份原输入. 评分使用原pytest, 只映射本地路径, 不改断言. 当前研究机器已有pytest和rapidfuzz;评分进程从现有临时环境读取. 换机器运行时需要相同依赖, 不用租GPU.

## 费用和停止

最多5次Profy任务调用: 2次练习, 3次考试; 最多1次OpenRouter修改请求. 每次Profy任务900秒超时, 超时会请求停止. 不自动重试, 不为高分追加调用. 三组考试最多同时跑2个. 总Profy货币账单取不到时写未知, 不写USD0; OpenRouter费用以返回的usage为准.

## 到哪里看结果

结果在`--out`指定的本地目录: summary.json是总结果, gate.json是候选是否采用, 各组result.json有原评分、耗时、输出hash. 原文件、第三方评分代码和完整日志不提交到这个仓库. 仓库只保留本助手写的代码、说明和不含原文的结果摘要.

原程序的strict分数是整道任务通过=1、没通过=0. pytest通过项数只是诊断, 不是字段准确率. 一个考试task只能提供一次小样例证据, 不做显著性或广泛泛化结论.

## 代码来源

pilot.py和test_pilot.py是本次新写. archive/只保存此前本助手写过、未用于论文的研究脚本. 不含袋袋源码、expert文件、benchmark题面/附件/答案、官方grader或他人代码. 相关来源只写外部路径和出处, 不把内容复制进来.
