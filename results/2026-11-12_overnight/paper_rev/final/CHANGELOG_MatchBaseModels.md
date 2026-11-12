# 最新完成稿: Match base models

正文6页, 全文27页。

1. 在Lessons from deployment第一条加入:

\textbf{Match base models.} A configuration advantage that appeared against baselines on a different model (both-order wins on 16/20 tasks) was not retained with model-label-matched baselines (Full $-$ Expert Prompt: $-$0.19, 95\% CI [$-$0.55, 0.16]); configuration-level comparisons should hold the base model fixed.

2. 28处正文和表格的数值负号统一为数学负号$-$; 数字未改, 日期/模型名/范围连字符/Listing原样保留。

3. 按授权压缩4.5第一段以保持正文6页:

修改前: The 20 Full records with elapsed-time metadata have a median of 52.05\,s and a mean of 54.41\,s. These descriptive timings characterize those records; comparable baseline timing is unavailable.

修改后: Full latency (20 records): median 52.05\,s, mean 54.41\,s; comparable baseline timing unavailable.

4. 将数学负号恢复为普通字符、删除新增条目并还原耗时段落后, main.tex与I011副本逐字相同; 其他内容未改。原论文项目未改。
