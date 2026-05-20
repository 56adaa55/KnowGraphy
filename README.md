# 项目文件说明

本项目主要构建了一个完整的知识图谱信息抽取流水线，包含中文文本的命名实体识别（NER）、实体消歧与链接、基于大模型（LLM）的关系抽取，以及最终的知识图谱可视化展示。各文件及其对应作用如下：

## 📄 原始数据与文档
- **README.md**：本项目的说明文档。
- **turing_raw_data_zhcn.txt**：原始输入的中文自然语言文本数据（以艾伦·图灵的相关介绍为例）。

## ⚙️ 核心处理脚本
- **entity_extraction.py**：【任务一】实体抽取脚本。利用 Spacy 序列标注模型进行初步的命名实体识别（NER）。
- **entity_disambiguation.py**：【任务二】实体消歧与链接脚本。负责共指消解、稠密向量相似度计算，以及基于 Wikidata API 的全球知识图谱链接。
- **relation_extraction.py**：【任务三】关系抽取脚本。调用大型语言模型（LLM），结合原文和消歧后的标准实体列表，抽取实体间的语义关系。
- **visualize.py**：数据可视化脚本。负责读取最终处理好的实体与关系三元组，利用可视化库生成交互式知识图谱。

## 💾 过程产物与数据文件
- **task1_traditional_ner.json**：任务一生成的初步命名实体识别（NER）表层实体结果。
- **task2_traditional_disambig.json**：任务二通过传统字符串匹配与就近回溯算法生成的消歧/聚类中间结果。
- **task2_clusters.json**：任务二利用词向量余弦相似度计算得出的实体聚类结果。
- **task2_final_linked_entities.json**：任务二经过 Wikidata API 匹配后，最终成功链接的实体结果。
- **task3.json**：经过实体消歧之后生成的标准实体列表，作为输入送进大模型进行关系抽取（任务三）的数据文件。
- **turing_final_graph_ready.json**：包含最终的实体节点与关系边，用于输入给 `visualize.py` 生成知识图谱的最终数据文件。

## 📊 日志与展示成果
- **traditional_ner_disambig.log**：运行抽取与消歧脚本时生成的运行日志文件（记录了 API 请求和算法处理细节）。
- **turing_knowledge_graph.html**：通过可视化脚本生成的知识图谱前端展示网页（直接在浏览器中打开即可查看交互图谱）。
