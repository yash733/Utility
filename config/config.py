from configparser import ConfigParser
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

class Config:
    config_info = ConfigParser()
    config_path = f'{os.getcwd()}/config/config.ini'
    with open(config_path, encoding='utf-8') as f:
        config_info.read_file(f)

    @classmethod
    def get_llm(cls):
        return cls.config_info['DEFAULT'].get('LLM').split(', ')
    
    @classmethod
    def get_groq_model(cls):
        return cls.config_info['DEFAULT'].get('LLM_GROQ').split(', ')
    
    @classmethod
    def get_ollama_model(cls):
        return cls.config_info['DEFAULT'].get('LLM_OLLAMA').split(', ')
    
    @classmethod
    def get_options(cls):
        return cls.config_info['DEFAULT'].get('OPTIONS').split(', ')