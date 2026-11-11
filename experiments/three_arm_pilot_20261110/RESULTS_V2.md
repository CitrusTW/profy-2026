# 修正版三组小实验: 实际结果

三组执行检查: 通过.
开发题是SkillsBench的pdf-excel-diff: 核对员工PDF和Excel. 测试题是invoice-fraud-detection: 核对发票、供应商和采购订单. 三组用同一个Profy gpt-6.1-sol, 各自使用独立session.
这是本助手新增的skill更新研究原型. 不是袋袋原生evolution, 也没有测试跨expert归因. 测试题此前已经跑过, 不称全新未见任务; 更新器不接收测试答案或评分反馈.

| 阶段/组别 | 原整题strict | 原pytest通过/总数 | 客户端秒数 | 工具调用 |
| --- | --- | --- | --- | --- |
| 开发题: 原skill | 1 | 11/11 | 243.115 | 17 |
| 开发题: 首个候选(弃用) | 1 | 11/11 | 215.500 | 14 |
| 开发题: 通用候选(采用) | 1 | 11/11 | 189.372 | 15 |
| no-skills | 0 | 1/2 | 62.763 | 6 |
| with-skills | 0 | 1/2 | 102.475 | 22 |
| with-skills-cognilife-method | 0 | 1/2 | 161.520 | 19 |

整题strict是整份输出通过=1、没通过=0. pytest包含文件存在和整份内容等测试, 通过项比例不是字段准确率. 客户端秒数含任务运行和文件回传, 不含上传.

## 新版skill有没有真的进入第三组

采用检查结果: 通过, 新版已在测试前冻结.
新版是根据公开开发题和开发运行统计生成的一份通用记录核对说明, 替换expense-record-reconciliation/SKILL.md. 更新器没有阅读私有原skill正文; 原skill只在本地用于体积比较. 因此这里测的是有开发检查的候选替换原型, 不能称为袋袋原生完整学习机制.
表中的首个候选在开发阶段弃用: 它写入了开发题专用文件名, 因而不进入正式测试. 通用候选才是纠正后做开发复测并采用的版本. 原skill没有因此重跑. 纠正在测试启动前完成, 未向更新器提供测试反馈.
检查同时核对了上传包里只改目标skill、与旧版哈希不同、原生read返回包含新版全文、bash计算的实际文件SHA256一致. 它能证明新版被加载和读取, 不能单独证明模型每一步都遵循它.

## no-skills有没有夹带skill

共用经验只保留公开开发题面和运行统计. 检查附件中没有expert.zip, 原生调用中没有skill工具或skill文件读取. 这表示没有提供本项目expert包或片段; 平台基础指令仍存在, 不把它叫作完全没有任何平台基础skill的裸模型.

## 原输出哪里没通过

以下只对保存下来的JSON作离线诊断, 没改答案、没放宽原评分.

- no-skills: 参考答案标记50页有问题, 输出50页, 漏报0页, 多报0页; 全字段精确比对差异计数为{"po_number": 5}.
- with-skills: 参考答案标记50页有问题, 输出50页, 漏报0页, 多报0页; 全字段精确比对差异计数为{"po_number": 5}.
- with-skills-cognilife-method: 参考答案标记50页有问题, 输出50页, 漏报0页, 多报0页; 全字段精确比对差异计数为{"po_number": 5}.

差异例子: 第4页的po_number, 输出是"PO-INVALID", 参考答案是null. po_number就是采购订单号.

## 这次实际说明什么

原整题strict: no-skills=0, with-skills=0, with-skills-cognilife-method=0.
更新后组与初始skill组的整题通过情况相同. 本题没有观察到整题得分提升, 不把新版加载成功写成方法效果提升.
三组输出的SHA256完全相同, 即交付JSON的字节也相同.
测试任务客户端耗时: 初始skill组102.475秒、更新后组161.520秒. 本次更新后组耗时更长, 只报告这一次观察, 不据此推广为稳定性能差异.
开发题原测试通过数没有下降; skill文档从1191减至1105 UTF-8字节, 减少7.2%. 这是文档体积变化, 不是已证明的调用费用或执行效率提升.

## 费用和调用量

Profy任务6次, OpenRouter请求2次. OpenRouter返回费用合计0.0013296 USD. Profy货币账单未知, 不填0.

| 阶段/组别 | prompt tokens事件合计 | completion tokens事件合计 |
| --- | --- | --- |
| dev_before | 389080 | 2922 |
| dev_candidate | 302697 | 2566 |
| dev_candidate_revised | 197261 | 2382 |
| no-skills | 111862 | 1985 |
| with-skills | 309344 | 4072 |
| with-skills-cognilife-method | 457197 | 3588 |

token数是原生usage.token事件逐项求和, 不是已核对的货币账单. 完整运行日志、原始输出和原grader保存在本地, 代码仓库只保存本助手代码、说明和不含原文的数字摘要.

## 怎么下结论

这轮只比较同一道测试题的三次运行. 即使有分差, 也只能报告这个任务的观察, 不能推出普遍提升、长期学习或跨expert有效. 三组得分相同也不能证明方法普遍无效. 是否值得扩大任务量要按真实结果判断.

没有修改论文或提交OpenReview.

## 执行检查明细

- shared_experience_allowlist_only: True
- common_experience_has_no_raw_tool_result_field: True
- all_three_test_outputs_scored: True
- no_skills_no_expert_zip_uploaded: True
- no_skills_no_skill_tool_call: True
- no_skills_no_skill_file_read: True
- same_public_only_experience_for_three_arms: True
- same_original_task_files_in_three_arms: True
- only_target_skill_changed_in_bundle: True
- updated_skill_hash_differs: True
- update_accepted_before_test: True
- with_skills_initial_skill_read_and_hash_verified: True
- third_arm_updated_skill_read_and_hash_verified: True
- sessions_unique: True

初始开发与弃用候选的执行commit: 0d9d8754e1f3bb7681ddea85a0cbbc5d489269c2.
纠正后执行代码commit: 8a7b51f81cd2cf5cf82a46462af6c164b90c3912.
纠正后pilot.py SHA256: 2a2455dc512cef2b49cfebcfe57c5c41ea954bb70f9cf9ef55fbc1776051ad80.
