# 项目文件说明

本项目主要用于中文文本的命名实体识别（NER）、实体消歧、实体链接以及最终的知识图谱可视化展示。各文件及其对应作用如下：

- **README.md**：本项目的说明文档。
- **turing_raw_data_zhcn.txt**：原始输入的中文自然语言文本数据。
- **traditional_1_2.py**：核心处理脚本，包含任务一（命名实体识别抽取）和任务二（共指消解、基于 Wikidata 的实体链接与消歧）的逻辑。
- **traditional_ner_disambig.log**：运行上述 `traditional_1_2.py` 脚本时生成的运行日志文件。
- **task1_traditional_ner.json**：任务一生成的初步命名实体识别（NER）抽取结果。
- **task2_traditional_disambig.json**：任务二通过传统字符串匹配与就近回溯算法生成的消歧/聚类结果。
- **task2_clusters.json**：任务二利用词向量余弦相似度计算得出的实体聚类结果。
- **task2_final_linked_entities.json**：任务二经过 Wikidata API 匹配后最终成功链接和消歧的实体结果。
- **turing_final_graph_ready.json**：用于生成知识图谱的最终输入实体数据文件。
- **visualize.py**：数据可视化脚本，负责读取最终处理好的实体关系并生成图谱。
- **turing_knowledge_graph.html**：通过可视化脚本生成的知识图谱前端展示网页。
