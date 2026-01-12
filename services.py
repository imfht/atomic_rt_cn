import os
import json
import requests
import yaml
from datetime import datetime
from openai import OpenAI

class AtomicRedTeamService:
    """Service for fetching and processing Atomic Red Team data"""
    
    def __init__(self, repo_base_url):
        self.repo_base_url = repo_base_url
        self.techniques_index_url = f"{repo_base_url}/atomics/Indexes/Indexes-Markdown/index.md"
    
    def fetch_technique_list(self):
        """Fetch list of available techniques from Atomic Red Team"""
        try:
            # For demo purposes, return a sample list
            # In production, this would parse the actual index
            return [
                'T1003', 'T1005', 'T1007', 'T1012', 'T1016',
                'T1018', 'T1021', 'T1027', 'T1036', 'T1047',
                'T1053', 'T1055', 'T1056', 'T1059', 'T1068',
                'T1070', 'T1071', 'T1078', 'T1082', 'T1083',
                'T1087', 'T1090', 'T1091', 'T1092', 'T1095',
                'T1098', 'T1105', 'T1106', 'T1110', 'T1112',
                'T1113', 'T1115', 'T1119', 'T1120', 'T1123',
                'T1124', 'T1127', 'T1129', 'T1132', 'T1133',
                'T1134', 'T1135', 'T1136', 'T1137', 'T1140',
                'T1176', 'T1185', 'T1190', 'T1195', 'T1197'
            ]
        except Exception as e:
            print(f"Error fetching technique list: {e}")
            return []
    
    def fetch_technique_data(self, technique_id):
        """Fetch detailed data for a specific technique"""
        try:
            # Construct URL for technique YAML file
            url = f"{self.repo_base_url}/atomics/{technique_id}/{technique_id}.yaml"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = yaml.safe_load(response.text)
                return data
            else:
                return None
        except Exception as e:
            print(f"Error fetching technique {technique_id}: {e}")
            return None
    
    def parse_technique_data(self, data):
        """Parse technique data into structured format"""
        if not data:
            return None
        
        technique_info = {
            'technique_id': data.get('attack_technique', ''),
            'name': data.get('display_name', ''),
            'description': '',
            'tactic': '',
            'platform': '',
            'atomic_tests': []
        }
        
        # Extract atomic tests
        atomic_tests = data.get('atomic_tests', [])
        for idx, test in enumerate(atomic_tests):
            test_info = {
                'test_number': idx + 1,
                'name': test.get('name', ''),
                'description': test.get('description', ''),
                'supported_platforms': ', '.join(test.get('supported_platforms', [])),
                'executor': test.get('executor', {}).get('name', ''),
                'command': test.get('executor', {}).get('command', '')
            }
            technique_info['atomic_tests'].append(test_info)
        
        technique_info['raw_data'] = json.dumps(data, ensure_ascii=False)
        return technique_info


class LLMService:
    """Service for integrating with LLM API"""
    
    def __init__(self, api_key, api_base=None, model='gpt-3.5-turbo'):
        self.api_key = api_key
        self.model = model
        self.client = None
        
        # Only initialize client if API key is configured
        if api_key and api_key != 'your-openai-api-key' and api_key.strip():
            try:
                if api_base:
                    self.client = OpenAI(api_key=api_key, base_url=api_base)
                else:
                    self.client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def analyze_technique(self, technique_data):
        """Use LLM to analyze and summarize attack technique"""
        if not self.client:
            # Return mock data if API key is not configured or client failed to initialize
            return {
                'summary': f"这是关于 {technique_data.get('name', 'unknown')} 攻击技术的概要。",
                'analysis': f"该技术 ({technique_data.get('technique_id', '')}) 的详细分析需要配置 LLM API。"
            }
        
        try:
            prompt = f"""请分析以下网络攻击技术，并提供中文摘要和分析：

技术ID: {technique_data.get('technique_id', '')}
技术名称: {technique_data.get('name', '')}
描述: {technique_data.get('description', '')}

请提供：
1. 技术摘要（100字以内）
2. 详细分析（包括攻击原理、潜在影响、防御建议）
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个网络安全专家，专门分析攻击技术。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Split summary and analysis
            parts = content.split('\n\n', 1)
            summary = parts[0] if len(parts) > 0 else content
            analysis = parts[1] if len(parts) > 1 else content
            
            return {
                'summary': summary,
                'analysis': analysis
            }
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return {
                'summary': f"技术 {technique_data.get('technique_id', '')}: {technique_data.get('name', '')}",
                'analysis': f"LLM 分析失败: {str(e)}"
            }
    
    def batch_analyze_techniques(self, techniques_data):
        """Analyze multiple techniques using LLM"""
        results = []
        for technique in techniques_data:
            result = self.analyze_technique(technique)
            results.append({
                'technique_id': technique.get('technique_id'),
                'summary': result['summary'],
                'analysis': result['analysis']
            })
        return results
