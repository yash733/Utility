from configparser import ConfigParser
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

def job_desc():
    # Extract data
    config = ConfigParser()
    path = f'{os.getcwd()}\config\\test_run_data.ini'
    with open(path, encoding='utf-8') as f:
        config.read_file(f)
    
    return config['JOBDESC'].get('job_description')