import streamlit as st
import os
import json

# Set the path to the image file
user_icon_path = "image/user_icon.png"  # User Icon Path
bot_icon_path = "image/bot_icon.png"    # BOT icon path


st.title("Review Chat History")
st.markdown("**Select an item to view the conversation content.**")

# Set the path to the data directory
data_directory = 'pages/data'

# Get a list of .json files in data_directory and remove the file extension
file_list = [file[:-5] for file in os.listdir(data_directory) if file.endswith('.json')]

with st.container():
    if "show_db" not in st.session_state:
        st.session_state.show_db = file_list[0]

    # Set the list of JSON files without the extension as selection options
    st.session_state.show_db = st.selectbox(
        'Please select',
        file_list)

    st.write(st.session_state.show_db)

    # Read the selected file by adding the file extension
    with open(os.path.join(data_directory, st.session_state.show_db + '.json'), 'r') as f:
        data_loaded = json.load(f)
        st.session_state["his_messages"] = data_loaded


for message in st.session_state["his_messages"]:

    if message["role"] != "system":
        # Create columns for images and text
        cols = st.columns([1, 24])

        with cols[0]:  # 画像の列
            if message["role"] == "user":
                st.image(user_icon_path, width=30) # Show user's image
            else:
                st.image(bot_icon_path, width=30)  # Show bot images

        with cols[1]:  # Columns of text
            # Display colon separated from text
            st.markdown(f": {message['content']}", unsafe_allow_html=True)


# Delete button at the bottom of the page
if st.button('Delete Selected History'):
    file_to_delete = os.path.join(data_directory, st.session_state.show_db + '.json')

    # Check if file exists before trying to delete
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)
        st.success(f'File {st.session_state.show_db} deleted successfully.')

        # Update the file list and session state after deletion
        file_list = [file[:-5] for file in os.listdir(data_directory) if file.endswith('.json')]
        st.session_state.show_db = file_list[0] if file_list else None
    else:
        st.error('File not found.')