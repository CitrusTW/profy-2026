# I-003 Claude输出截断, 请求编号修正

模型ID固定anthropic/claude-opus-5.5, 原Listing prompt未改. 预注册max_tokens1024沿用原Moonshot helper, 但已有两个Full rubric任务(ADV_002、ADV_004)均三次finish_reason=length, 未解析成功. 例如ADV_002首调用completion_tokens1024, 其中reasoning_tokens862, JSON只有376字符后被截断. 原始请求和返回全部保留, 没有从半截JSON取分、没有手填.

其他已完成请求仍按预注册继续, 不擅自改模型/输出预算. 当前所有账单有回执, I00315美元上限与保守预算预留继续生效.

建议允许一个统一的rubric修正批次: 同一个Claude ID、同一prompt/字段/解析, 20×3全部rubric重新打分, 所有条件统一max_tokens4096; 不只挑Full失败题重打, 也不择优合并两批. 旧rubric批次完整留档, 新批次作为唯一rubric来源. Pairwise如全部成功则保留原80次, 因为是另一种prompt和独立结果. 本次重做60个rubric的目录价保守预算上界为8.054640美元, 是源prompt字节额度+输出上限计算, 不是实际费用估计. 只有旧已回执支出加新批次预算上界<=15时才启动; 否则不跑, 报告缺失并按I003删掉LLM比较结论. 不充值.

请明确是否允许这个参数修正批次; 在收到编号指令前不改变已注册max_tokens. 截断是执行失败, 不根据评分高低挑模型或分数.
