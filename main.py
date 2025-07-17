import streamlit as st
import requests
import json


global_var=''


def get_request():
    response = requests.get('http://127.0.0.1:5000')
    print(response.json())
    response=response.json()

    # global_var=response['RESPONSE']
    return response['RESPONSE']


def get_request_prompt(prompt):
    response = requests.post('http://127.0.0.1:5000/prompt',data={'prompt':prompt})
    # print(response.json())
    # response=response.json()

    # global_var=response['RESPONSE']
    # return response['RESPONSE']
    # return 'rand'


def main():
    st.title('Chat GPT clone')

    prompt = st.chat_input("Ask Something")
    print('PROMPT',prompt)
    if prompt:
        res=get_request_prompt(prompt)
        st.write(res)



if __name__ == "__main__":
    main()
