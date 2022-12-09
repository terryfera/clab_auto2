import streamlit as st
import utils
import json
import config
from pathlib import Path
from tinydb import TinyDB, Query


if "load_state" not in st.session_state:
    st.session_state.load_state = False


def add_lab_validation(add_result):
    if type(add_result) is int:
        st.success('Lab Added Successfully', icon="✅")
    elif type(add_result) is Exception:
        st.error('Lab load failed', icon="🚨")
    else:
        st.error(
            f'Did not expect that... result was: {add_result}')


def load_page():
    installed_labs, add_lab, update_lab, delete_lab = st.tabs(
        ['Installed Labs', 'Add Lab', 'Update Lab', 'Delete Lab'])

    with installed_labs:
        st.header('Installed Labs')

        option = st.selectbox(
            'Currently installed labs',
            utils.get_db_labs()
        )

        st.write(
            "Select a lab to view it's details, or use the checkbox below to see all labs")

        all_labs = st.checkbox('Get All Labs')

        if st.button('Get Lab Details'):
            if all_labs == True:
                lab_details = utils.all_lab_details()
            else:
                lab_details = utils.search_lab_details(option)

            for lab in lab_details:
                with st.container():
                    lab_table = f"""
                    |  |  |
                    | --- |--- |
                    | **Lab Name** | {lab['name']} |
                    | **Description** | {lab['description']} |
                    | **Author** | {lab['author']} |
                    | **Git Enabled** | {lab['git']} |
                    | **Local Folder** | {lab['localLabFolder']} |
                    | **Lab File** | {lab['labFile']} |
                    | **Git Repo** | {lab['gitRepo']} |
                    """
                    st.markdown(utils.format_md_table(),
                                unsafe_allow_html=True)
                    st.markdown(lab_table)
                    st.write("---")

    with add_lab:
        st.header('Add Lab')

        with st.form("Add New Lab"):

            lab_name = st.text_input('Lab Name')
            lab_shortname = lab_name.lower()
            description = st.text_area('Description')
            author = st.text_input('Author')
            git_enabled = st.checkbox('Use Git Repo?')
            git_url = st.text_input('Git URL')
            local_folder = st.text_input('Local Folder')
            lab_file = st.text_input('Lab File Name')

            lab_details_json = {
                "name": lab_name,
                "shortname": lab_shortname,
                "author": author,
                "git": git_enabled,
                "localLabFolder": local_folder,
                "labFile": lab_file,
                "gitRepo": git_url,
                "description": description
            }

            submitted = st.form_submit_button("Submit")

            if submitted:
                lab_exists = utils.search_lab_details(lab_name)
                lab_path_exists = utils.check_lab_path(local_folder)
                url_status = utils.validate_url(git_url)
                git_status = utils.git_check(git_url)

                if len(lab_exists) > 0:
                    st.error(
                        f'Lab with name {lab_name} already exists, select another name')
                elif lab_path_exists is True:
                    st.error(
                        f'Lab with path {local_folder} already exists, select another folder')
                elif git_enabled is True and url_status is False:
                    st.error(f'Git URL is not a valid URL, please try again')
                elif git_enabled is True and url_status is True:
                    if git_status is False:
                        st.error(f'Git repo does not exist or is unreachable')
                    elif git_status is True:
                        add_result = utils.db_add_lab(lab_details_json)
                        add_lab_validation(add_result)
                        clone_lab_result = utils.clone_lab(
                            local_folder, git_url)

                else:
                    add_result = utils.db_add_lab(lab_details_json)
                    add_lab_validation(add_result)

    with update_lab:
        st.write('Update Lab')

    with delete_lab:
        st.header('Delete Lab')
        
        delete_option = st.selectbox(
            'All Labs',
            utils.get_db_labs()
        )

        st.write(
            "Select a lab to delete")

        confirm_check = st.checkbox('Confirm Delete')

        if st.button('Delete Selected Lab'):
            if delete_option and confirm_check is True:
                lab_del_result = utils.db_del_lab(delete_option)
                if len(lab_del_result) >= 1:
                    st.write('Deleted lab succesfully')
                    st.code(f'Deleted db entry {lab_del_result}')
                elif type(lab_del_result) is Exception:
                    st.error('Lab delete failed', icon="🚨")
                else:
                    st.error(
                        f'Did not expect that... result was: {lab_del_result}')
            elif delete_option is None:
                st.write('Please select an option')
            elif delete_option and confirm_check is False:
                st.write('Please confirm deletion')
            else:
                st.write('not sure')



if __name__ == "__main__":
    load_page()
