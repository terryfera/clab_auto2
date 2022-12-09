import streamlit as st
import subprocess
import json
from tinydb import TinyDB, Query
import config
from pathlib import Path
import validators
import requests
from git import Repo
import os

db = TinyDB("labs.json")
Labs = Query()


def get_db_labs():
    '''
    Get all lab entries from database and return a list of their names
    '''
    all_labs = db.all()
    lab_list = []

    for lab in all_labs:
        lab_list.append(lab['name'])

    return lab_list


def db_add_lab(lab_details):
    return db.insert(lab_details)


def db_update_lab():

    return


def db_del_lab(lab_name):
    return db.remove(Labs.name == lab_name)


def clone_lab(local_folder, git_url):
    labs_parent_dir = config.appRoot + config.labRoot
    lab_path = Path(labs_parent_dir + "/" + local_folder)
    repo_git = Path(labs_parent_dir + "/" + local_folder + ".git")
    if lab_path.is_dir():
        st.error("Warning Path already exists, checking for existing git repo")
        if repo_git.is_file():
            st.error(
                "Git repo already in this directory, delete it before trying again")
        else:
            st.write(f"Cloning repo from {git_url}")
            try:
                Repo.clone_from(git_url, lab_path)
            except:
                st.error(Exception)
    else:
        st.write(f"Making directory {lab_path}")
        try:
            os.mkdir(lab_path)
        except:
            st.error(Exception)
        st.write(f"Cloning repo from {git_url}")
        try:
            Repo.clone_from(git_url, lab_path)
        except:
            st.error(Exception)


def check_lab_path(lab_path):
    '''
    Check if the path entered in the lab details is valid
    Pulls the appRoot and labRoot folders from the users
    config file
    Return True if valid, False if not valid
    '''
    labs_parent_dir = config.appRoot + config.labRoot
    lab_full_path = f"{labs_parent_dir}/{lab_path}/"
    lab_path_check = Path(lab_full_path)
    if lab_path_check.is_dir():
        return True
    else:
        return False


def search_lab_details(lab_name):
    return db.search(Labs.name == lab_name)


def all_lab_details():
    return db.all()


def clab_function(lab_function, lab_option):
    '''
    Interact with containerlab binary and return output to application
    '''
    lab_details = db.search(Labs.name == lab_option)[0]
    labs_parent_dir = config.appRoot + config.labRoot
    lab_full_path = f"{labs_parent_dir}/{lab_details['localLabFolder']}/{lab_details['labFile']}"
    lab_path_check = Path(lab_full_path)
    if lab_path_check.is_file():
        return subprocess.run(['sudo', 'containerlab', lab_function, '-t', lab_full_path], text=True, check=True, capture_output=True)
    else:
        return lab_full_path


def git_check(git_url):
    '''
    Use requests library to check if entered Git URL is valid
    '''
    response = requests.get(git_url)
    if response.status_code == 200:
        return True
    else:
        return False


def validate_url(url):
    '''
    Validate URL format only
    '''
    return validators.url(url)


def get_running_labs():
    output = subprocess.run(['sudo', 'containerlab', 'inspect', '--all',
                            '-f', 'json'], text=True, check=True, capture_output=True)
    running_labs = json.loads(output.stdout)
    return running_labs


def format_md_table():
    table_style = """
    <style>
    table:nth-of-type(1) {
        display:table;
        width:100%;
    }
    table:nth-of-type(1) th:nth-of-type(2) {
        width:65%;
    }
    </style>
    """
    return table_style


def running_lab_status(status):
    if status.lower() == "running":
        status_markdown = f"""<span style="color:green">{status}</span>"""
    else:
        status_markdown = f"""<span style="color:red">{status}</span>"""

    return status_markdown


def connect_to_device(dev_option):

    hostname = dev_option
    port = 22
    user = 'arista'
    passwd = 'arista'

    try:
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=user, password=passwd)
        while True:
            try:
                cmd = input(f'{hostname} - $> ')
                if cmd == 'exit':
                    break
                stdin, stdout, stderr = client.exec_command(cmd)
                return st.code(stdout)
                print(stdout.read().decode())
            except KeyboardInterrupt:
                break
        client.close()
    except Exception as err:
        print(std(err))
