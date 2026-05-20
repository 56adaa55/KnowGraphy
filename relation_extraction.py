import json
import re
from openai import OpenAI

# 1. 初始化大模型客户端 (这里以支持 OpenAI API 格式的模型为例)
# 如果使用 OpenAI，填入原始 api_key。
# 如果使用国内大模型（如 DeepSeek, 通义千问），请修改 base_url 和 api_key。
client = OpenAI(
    api_key="your-api-key-here", 
    base_url="https://api.openai.com/v1" # 替换为你的大模型 API 地址
)

def clean_json_response(response_text):
    """
    清洗大模型返回的文本，防止其带有 ```json 和 ``` 标记导致解析失败
    """
    response_text = response_text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    
    if response_text.endswith("```"):
        response_text = response_text[:-3]
        
    return response_text.strip()

def extract_relations(text, entities):
    """
    调用 LLM 进行关系抽取
    """
    
    system_prompt = """你是一个专业的知识图谱和信息抽取专家。你的任务是根据给定的“原始文本”和“实体列表”，抽取实体之间的语义关系。

【抽取规则】
1. head（头实体）和 tail（尾实体）必须严格使用实体列表中提供的 `canonical_name`。
2. 关系名称（relation）应当简明扼要，如：外文名、国籍、职业、出生地等。
3. 严格基于原文事实，不要脑补原文中未提及的关系。
4. 严格输出合法的 JSON 数组，格式如下，不要包含任何多余文本：
[
  {
    "head": "实体1的canonical_name",
    "relation": "关系名",
    "tail": "实体2的canonical_name"
  }
]"""

    # 将实体列表转为美化的 JSON 字符串以便 LLM 阅读
    entities_str = json.dumps(entities, ensure_ascii=False, indent=2)

    user_prompt = f"""【原始文本】
{text}

【实体列表】
{entities_str}

【请输出关系抽取结果 JSON】"""

    try:
        # 调用大模型
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 替换为你使用的模型名称，如 deepseek-chat, qwen-plus 等
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1, # 关系抽取属于确定性任务，temperature 尽量设低
            max_tokens=1024
        )

        # 获取并清洗结果
        raw_result = response.choices[0].message.content
        cleaned_json = clean_json_response(raw_result)
        
        # 解析 JSON
        relations = json.loads(cleaned_json)
        return relations

    except json.JSONDecodeError as e:
        print(f"JSON解析失败，模型原始输出为: {raw_result}")
        return []
    except Exception as e:
        print(f"API请求失败: {e}")
        return []

# ================= 测试运行 =================
if __name__ == "__main__":
    # 假设这是你的原文内容
    with open("turing_raw_data_zhcn.txt", "r", encoding="utf-8") as f:
        sample_text = f.read()

    with open("new_NER.json", "r", encoding="utf-8") as f:
        sample_entities = json.load(f)  

    print("正在调用模型进行抽取...")
    extracted_relations = extract_relations(sample_text, sample_entities)
    
    print("\n【抽取结果】:")
    print(json.dumps(extracted_relations, ensure_ascii=False, indent=2))