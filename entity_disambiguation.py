import json
import numpy as np
import spacy
import requests
import jieba   
import zhconv
import logging

# 1. 基础配置
RAW_DATA_PATH = r"turing_raw_data_zhcn.txt"
NER_INPUT_PATH = r"task1_traditional_ner.json"
CLUSTERS_OUTPUT_PATH = r"task2_clusters.json"
LINKED_OUTPUT_PATH = r"task2_final_linked_entities.json"
LOG_PATH = r"entity_disambiguation.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=LOG_PATH,
    filemode='w',
    encoding='utf-8'
)

# 向量计算需要加载模型
logging.info("正在加载 Spacy 模型 zh_core_web_sm...")
nlp = spacy.load("zh_core_web_sm")

def task2_traditional_disambiguation(input_file=NER_INPUT_PATH, output_file="task2_traditional_disambig.json"):
    logging.info(">>> [任务二] 运行传统字符串匹配与就近回溯消解算法...")
    
    with open(input_file, "r", encoding="utf-8") as f:
        raw_entities = json.load(f)
        
    clusters = []  
    
    for i, ent in enumerate(raw_entities):
        word = ent["mention"]
        label = ent["label"]
        
        if label == "PRONOUN":
            for j in range(i-1, -1, -1):
                if raw_entities[j]["label"] == "PERSON":
                    closest_person = raw_entities[j]["mention"]
                    for cluster in clusters:
                        if closest_person in cluster["mentions"]:
                            if word not in cluster["mentions"]:
                                cluster["mentions"].append(word)
                            break
                    break
            continue

        found_cluster = False
        for cluster in clusters:
            if cluster["label"] != label:
                continue
            
            canonical = cluster["canonical_name"]
            if word in canonical or canonical in word:
                if len(word) > len(canonical):
                    cluster["canonical_name"] = word
                if word not in cluster["mentions"]:
                    cluster["mentions"].append(word)
                found_cluster = True
                break
                
        if not found_cluster:
            clusters.append({
                "canonical_name": word,
                "label": label,
                "mentions": [word]
            })
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(clusters, f, ensure_ascii=False, indent=2)
        
    logging.info(f"✅ 任务二完成！最终聚类出 {len(clusters)} 个标准实体。已保存至 {output_file}")


def task2_vector_disambiguation(text, input_file=NER_INPUT_PATH, output_file=CLUSTERS_OUTPUT_PATH):
    logging.info(">>> [任务二] 读取任务一结果，利用稠密向量计算语义余弦相似度...")
    
    with open(input_file, "r", encoding="utf-8") as f:
        entities_from_json = json.load(f)
        
    doc = nlp(text) 
    
    clusters = []
    SIMILARITY_THRESHOLD = 0.70  
    
    for item in entities_from_json:
        word_text = item["mention"]
        start_char = item["start"]
        end_char = item["end"]
        label = item["label"]
        
        span = doc.char_span(start_char, end_char)
        if span is None or not span.has_vector:
            continue
            
        vector = span.vector  
        
        found_cluster = False
        best_score = -1
        best_cluster = None
        
        for cluster in clusters:
            if cluster["label"] != label and label != "PRONOUN":
                continue  
                
            canonical_vector = cluster["vector"]
            similarity = np.dot(vector, canonical_vector) / (np.linalg.norm(vector) * np.linalg.norm(canonical_vector))
            
            if similarity > best_score:
                best_score = similarity
                best_cluster = cluster
                
        if best_cluster and best_score > SIMILARITY_THRESHOLD:
            if word_text not in best_cluster["mentions"]:
                best_cluster["mentions"].append(word_text)
                
            best_cluster["vector"] = (best_cluster["vector"] + vector) / 2.0
            
            if len(word_text) > len(best_cluster["canonical_name"]):
                best_cluster["canonical_name"] = word_text
                
            found_cluster = True
            
        if not found_cluster:
            clusters.append({
                "canonical_name": word_text,
                "label": "PERSON" if label == "PRONOUN" else label,
                "vector": vector, 
                "mentions": [word_text]
            })

    final_output = []
    for c in clusters:
        final_output.append({
            "canonical_name": c["canonical_name"],
            "type": c["label"],
            "mentions": c["mentions"]
        })
        
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
        
    logging.info(f"✅ 任务二完成！最终聚类出 {len(final_output)} 个实体簇。已保存至 {output_file}")


def generate_candidates_from_wikidata(mention):
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": mention,
        "language": "zh",      
        "uselang": "zh",
        "format": "json",
        "limit": 5             
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status() 
        
        data = response.json()
        candidates = []
        for item in data.get("search", []):
            label_simp = zhconv.convert(item.get("label", ""), 'zh-cn')
            desc_simp = zhconv.convert(item.get("description", ""), 'zh-cn')
            candidates.append({
                "id": item.get("id"), 
                "label": label_simp, 
                "description": desc_simp 
            })
        return candidates
    except Exception as e:
        logging.error(f"   [API 请求失败]: {e}")
        return []


def disambiguate_and_link(mentions, context_text):
    logging.info(">>> 启动 [带有共指消解前置的实体链接] 流水线...\n")
    
    context_words = set(jieba.lcut(context_text))
    linked_results = []
    
    for i, ent in enumerate(mentions):
        mention = ent["mention"]
        label = ent["label"]
        query_word = mention
        
        logging.info(f"🔍 正在处理文本提及词: 【{mention}】")
        
        if label == "PRONOUN" and mention in ["他", "她", "它"]:
            logging.info(f"这是一个代词，跳过")
            continue

        candidates = generate_candidates_from_wikidata(query_word)
        
        if not candidates:
            logging.info(f"   [未找到候选] 将 '{query_word}' 标记为 NIL (无链接实体)\n")
            continue
            
        logging.info(f"   找到 {len(candidates)} 个关于 '{query_word}' 的候选实体，计算相似度...")
        
        best_candidate = None
        max_score = -1
        
        for cand in candidates:
            cand_desc = cand["label"] + " " + cand["description"]
            desc_words = set(jieba.lcut(cand_desc))
            overlap_score = len(context_words.intersection(desc_words))
            
            surface_score = 0
            if query_word == cand["label"]:
                surface_score = 100 
            elif query_word in cand["label"] or cand["label"] in query_word:
                surface_score = 10  
            
            total_score = overlap_score + surface_score

            logging.info(f"      -> 候选 [{cand['id']}] {cand['label']} | 得分: {total_score}")
            
            if total_score > max_score:
                max_score = total_score
                best_candidate = cand
                
        if best_candidate:
            linked_results.append({
                "original_mention": mention,         
                "resolved_query": query_word,       
                "linked_id": best_candidate["id"],
                "canonical_name": best_candidate["label"],
            })
            logging.info(f"   ✅ 链接成功！将提及词【{mention}】链接至全球图谱节点: {best_candidate['label']} ({best_candidate['id']})\n")
    return linked_results


def save_to_json(data, filename=LINKED_OUTPUT_PATH):
    logging.info(f"💾 正在将抽取和消歧结果序列化保存至本地...")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"保存成功：【{filename}】")
    except Exception as e:
        logging.error(f"❌ 保存失败: {e}")

if __name__ == "__main__":
    # 1. 读取原始文本（提供上下文）
    with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()
        
    # 2. 读取任务一提取出的实体列表
    with open(NER_INPUT_PATH, "r", encoding="utf-8") as f:
        extracted_entities = json.load(f)
        
    # 3. 执行实体链接与消歧
    final_data = disambiguate_and_link(extracted_entities, raw_text)
    
    # 4. 保存最终结果
    save_to_json(final_data)
    print(f"实体消歧与链接完成，结果已保存至: {LINKED_OUTPUT_PATH}")