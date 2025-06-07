#!/usr/bin/env python3
import json
import os
from typing import Dict, Any

def read_json_file(file_path: str) -> Dict[str, str]:
    """读取JSON文件并返回其内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def replace_placeholders(text: str) -> str:
    """将 {0} 替换为 %1$@，{1} 替换为 %2$@，依此类推"""
    import re
    def repl(match):
        idx = int(match.group(1)) + 1
        return f"%{idx}$@"
    return re.sub(r'\{(\d+)\}', repl, text)

def replace_key_placeholders(text: str) -> str:
    """将 key 中的 {n} 替换为 %@"""
    import re
    return re.sub(r'\{(\d+)\}', '%@', text)

def replace_json_key(text: str) -> str:
    """将JSON key中的%1$@替换为%@"""
    import re
    return re.sub(r'%(\d+)\$@', '%@', text)

def create_xcstrings_content(source_lang: str, translations: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """创建xcstrings格式的内容"""
    result = {
        "sourceLanguage": source_lang,
        "strings": {},
        "version": "1.0"
    }
    
    # 获取所有语言的键
    all_keys = set()
    for lang_data in translations.values():
        all_keys.update(lang_data.keys())
    
    # 为每个键创建对应的字符串条目
    for key in all_keys:
        # 获取源语言的文本
        source_text = translations[source_lang].get(key, "")
        source_text_replaced = replace_placeholders(source_text)
        
        # 创建字符串条目
        string_entry = {
            "comment": key,
            "localizations": {
                source_lang: {
                    "stringUnit": {
                        "state": "new",
                        "value": source_text_replaced
                    }
                }
            }
        }
        
        # 添加其他语言的翻译
        for lang, lang_data in translations.items():
            if lang != source_lang and key in lang_data:
                value_replaced = replace_placeholders(lang_data[key])
                string_entry["localizations"][lang] = {
                    "stringUnit": {
                        "state": "translated",
                        "value": value_replaced
                    }
                }
        
        # 将条目添加到结果中，使用%@作为JSON key
        json_key = replace_json_key(source_text_replaced)
        result["strings"][json_key] = string_entry
    
    return result

def main():
    # 定义语言文件映射
    lang_files = {
        "en": "en.json",
        "ja": "ja.json",
        "zh-Hans": "zh-Hans.json"
    }
    
    # 读取所有翻译文件
    translations = {}
    for lang, file_name in lang_files.items():
        if os.path.exists(file_name):
            translations[lang] = read_json_file(file_name)
    
    # 创建xcstrings内容
    xcstrings_content = create_xcstrings_content("en", translations)
    
    # 写入输出文件
    with open("Localizable.xcstrings", 'w', encoding='utf-8') as f:
        json.dump(xcstrings_content, f, ensure_ascii=False, indent=2)
    
    print("合并完成！输出文件：Localizable.xcstrings")

if __name__ == "__main__":
    main() 