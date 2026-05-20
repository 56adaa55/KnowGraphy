import json
import spacy
import logging

# 1. 基础配置
RAW_DATA_PATH = r"turing_raw_data_zhcn.txt"
NER_OUTPUT_PATH = r"task1_traditional_ner.json"
LOG_PATH = r"entity_extraction.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_PATH,
    filemode='w',
    encoding='utf-8'
)

# 2. 加载模型
logging.info("正在加载 Spacy 模型 zh_core_web_sm...")
nlp = spacy.load("zh_core_web_sm")

def task1_traditional_ner(text, output_file=NER_OUTPUT_PATH):
    logging.info(">>> [任务一] 运行传统基于 CNN/BiLSTM-CRF 的序列标注...")
    doc = nlp(text)
    
    raw_entities = []
    
    for ent in doc.ents:
        raw_entities.append({
            "mention": ent.text,
            "label": ent.label_, # PERSON, ORG, GPE 等
            "start": ent.start_char,
            "end": ent.end_char
        })
        
    for token in doc:
        if token.pos_ == "PRON" and token.text in ["他", "她"]:
            raw_entities.append({
                "mention": token.text,
                "label": "PRONOUN",
                "start": token.idx,
                "end": token.idx + len(token.text)
            })
            
    raw_entities = sorted(raw_entities, key=lambda x: x["start"])
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(raw_entities, f, ensure_ascii=False, indent=2)
        
    logging.info(f"✅ 任务一完成！共抽出 {len(raw_entities)} 个表层实体。已保存至 {output_file}")
    return output_file

if __name__ == "__main__":
    # 读取原始文本
    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()
        
    # 执行实体抽取并保存
    ner_file = task1_traditional_ner(raw_text)
    print(f"实体抽取完成，结果已保存至: {ner_file}")