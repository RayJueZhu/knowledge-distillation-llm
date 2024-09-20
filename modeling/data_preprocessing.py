import json
import pandas as pd
import requests
import time
import os
from dotenv import find_dotenv, dotenv_values


def load_data(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
        
        # Split the data by newlines and load each JSON object
        json_objects = []
        for line in data.splitlines():
            if line.strip():  # Skip empty lines
                try:
                    json_object = json.loads(line)
                    json_objects.append(json_object)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON on line: {line}. Error: {e}")

    return json_objects

def load_and_save_files_from_github(owner, repo, path='', branch='main', token=None):
    """
    Load all files from a GitHub repository at a given path and save them locally.

    :param owner: GitHub username or organization
    :param repo: Repository name
    :param path: Path to the directory in the repository (default is root)
    :param branch: Branch name (default is 'main')
    :param token: GitHub token for authentication (if needed)
    """
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}'
    headers = {}
    
    if token:
        headers['Authorization'] = f'token {token}'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        contents = response.json()
        
        # Ensure the data directory exists
        os.makedirs('data', exist_ok=True)
        
        for item in contents:
            file_name = item['name']
            file_path = item['path']
            
            # If the item is a file, download it
            if item['type'] == 'file':
                download_url = item['download_url']
                file_response = requests.get(download_url)
                
                if file_response.status_code == 200:
                    # Save the file in the "data" directory
                    with open(os.path.join('data', file_name), 'wb') as f:
                        f.write(file_response.content)
                    print(f"Downloaded and saved: {file_name}")
                else:
                    print(f"Failed to download {file_name}: {file_response.status_code}")
            elif item['type'] == 'dir':
                # Recursively load files from subdirectories
                load_and_save_files_from_github(owner, repo, item['path'], branch, token)
    else:
        print(f"Error: {response.status_code} - {response.json().get('message')}")

def get_files(json_objects, token=None):
    for my_json in json_objects:
        try:
            (owner_name, repo_name) = my_json["repo"]["name"].split("/")
            time.sleep(5)
            load_and_save_files_from_github(owner_name, repo_name, token=token)
        except KeyError as e:
            print(f"Missing key in JSON object: {e}")

if __name__ == "__main__":
    config = dotenv_values(find_dotenv())
    # token = config["GITHUB_ACCESS_TOKEN"] # Replace with your actual token
    """json_object = load_data("d181745f-03a2-4273-a8fd-a00c4b279c66.jsonl")
    print("First")
    print(json_object[0])
    get_files(json_object, token=token)"""
