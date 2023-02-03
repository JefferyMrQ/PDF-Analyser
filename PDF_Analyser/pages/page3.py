# -*- coding:utf-8 -*-
"""
 作者: QL
 日期: 2023年01月22日
"""
import streamlit as st
import pickle

sslist = ["issue2_add_num", "issue3_add_num", "word_add_num"]
for ss in sslist:
    if ss not in st.session_state:
        st.session_state[ss] = 0

# (part1.1) add new issues
# load database
data_path = "./data/demo.pkl"
with open(data_path, "rb") as f:
    ESGO_issue123_word_db = pickle.load(f)
    ESGO_factors = list(ESGO_issue123_word_db.keys())

ESGO = st.selectbox("Please select one factor:", ESGO_factors)

# add 2nd level issues
st.info("**If you want to add a new 2nd level issue, please click the button below.**")


def add1():
    st.session_state.issue2_add_num += 1


def delete1():
    st.session_state.issue2_add_num -= 1


def save1(issue1_new_issue23_words):
    global data_path, ESGO_issue123_word_db, ESGO
    for issue1 in issue1_new_issue23_words:
        ESGO_issue123_word_db[ESGO][issue1].update(issue1_new_issue23_words[issue1])

    with open(data_path, "wb") as f:
        pickle.dump(ESGO_issue123_word_db, f)


with st.expander("Add 2nd level issues"):
    issue123_word = ESGO_issue123_word_db[ESGO]
    issue1s = list(issue123_word.keys())

    issue1_new_issue23_words = {}
    for i in range(st.session_state.issue2_add_num):
        st.header(f"New 2nd level issue {i + 1}")
        selected_issue1 = st.selectbox("Please select 1st level issue:", issue1s,
                                       key=f"issue1_{i}_of_add_issue2")
        pre_issue2s = issue123_word[selected_issue1].keys()
        st.write(f"2nd issues of **_{selected_issue1}_** are: **_{','.join(pre_issue2s)}_**")

        # # or show issue2 + issue3 + words
        # pre_issue23_word = issue123_word[selected_issue1]
        # st.json(pre_issue23_word)

        new_issue2 = st.text_input("Add a new 2nd level issue here:",
                                   key=f"new_issue2_{i}", placeholder="issue2")
        new_issue3 = st.text_input("Add new 3rd level issues for new 2nd level issue: (separate them with English commas)",
                                   key=f"new_issue23_{i}", placeholder="issue3a,issue3b")
        new_words = st.text_input("Add new wrods for above 3rd level issues: (separate them with English commas)",
                                  key=f"new_issue23_wrods_{i}", placeholder="key word1,key word2")
        if issue1_new_issue23_words.get(selected_issue1):
            issue1_new_issue23_words[selected_issue1].update({new_issue2: (set(new_issue3.split(",")), set(new_words.split(",")))})
        else:
            issue1_new_issue23_words[selected_issue1] = {new_issue2: (set(new_issue3.split(",")), set(new_words.split(",")))}

    cola1, cola2, buffa = st.columns([1, 1, 3])
    issue23_word_add_button = cola1.button("Add", key="add1", on_click=add1)
    if st.session_state.issue2_add_num > 0:
        issue23_word_delete_button = cola2.button("Delete", key="delete1", on_click=delete1)
    buffa.button("Save", key="save1", on_click=save1, args=(issue1_new_issue23_words, ))

# add 3rd level issues
st.info("**If you want to add a new 3rd level issue, please click the button below.**")


def add2():
    st.session_state.issue3_add_num += 1


def delete2():
    st.session_state.issue3_add_num -= 1


def save2(issue12_new_issue3):
    global data_path, ESGO_issue123_word_db, ESGO
    for issue1 in issue12_new_issue3:
        for issue2 in issue12_new_issue3[issue1]:
            ESGO_issue123_word_db[ESGO][issue1][issue2][0].update(issue12_new_issue3[issue1][issue2])

    with open(data_path, "wb") as f:
        pickle.dump(ESGO_issue123_word_db, f)


with st.expander("Add 3rd level issues"):
    issue123_word = ESGO_issue123_word_db[ESGO]
    issue1s = list(issue123_word.keys())

    issue12_new_issue3 = {}
    for i in range(st.session_state.issue3_add_num):
        st.header(f"New 3rd level issue {i + 1}")
        selected_issue1 = st.selectbox("Please select 1st level issue:", issue1s,
                                       key=f"issue1_{i}_of_add_issue3")
        selected_issue2 = st.selectbox("Please select 2nd level issue:", issue123_word[selected_issue1],
                                       key=f"issue2_{i}_of_add_issue3")
        pre_issue3_word = issue123_word[selected_issue1][selected_issue2]
        st.json(pre_issue3_word)

        new_issue3 = st.text_input("Add new 3rd level issues for selected 2nd level issue: (separate them with English commas)",
                                   key=f"new_issue3_{i}", placeholder="issue3a,issue3b")
        if issue12_new_issue3.get(selected_issue1):
            if issue12_new_issue3[selected_issue1].get(selected_issue2):
                issue12_new_issue3[selected_issue1][selected_issue2].update(set(new_issue3.split(",")))
            else:
                issue12_new_issue3[selected_issue1][selected_issue2] = set(new_issue3.split(","))
        else:
            issue12_new_issue3[selected_issue1] = {selected_issue2: set(new_issue3.split(","))}

    colb1, colb2, buffb = st.columns([1, 1, 3])
    issue3_word_add_button = colb1.button("Add", key="add2", on_click=add2)
    if st.session_state.issue3_add_num > 0:
        issue3_word_delete_button = colb2.button("Delete", key="delete2", on_click=delete2)
    buffb.button("Save", key="save2", on_click=save2, args=(issue12_new_issue3,))

# add words
st.info("**If you want to add new words to some issues, please click the button below.**")


def add3():
    st.session_state.word_add_num += 1


def delete3():
    st.session_state.word_add_num -= 1


def save3(issue123_new_words):
    global data_path, ESGO_issue123_word_db, ESGO
    for issue1 in issue123_new_words:
        for issue2 in issue123_new_words[issue1]:
            ESGO_issue123_word_db[ESGO][issue1][issue2][1].update(issue123_new_words[issue1][issue2])

    with open(data_path, "wb") as f:
        pickle.dump(ESGO_issue123_word_db, f)

with st.expander("Add words"):
    issue123_word = ESGO_issue123_word_db[ESGO]
    issue1s = list(issue123_word.keys())

    issue123_new_words = {}
    for i in range(st.session_state.word_add_num):
        st.header(f"New Words {i + 1}")
        selected_issue1 = st.selectbox("Please select 1st level issue:", issue1s,
                                       key=f"issue1_{i}_of_add_words")
        selected_issue2 = st.selectbox("Please select 2nd level issue:", issue123_word[selected_issue1],
                                       key=f"issue2_{i}_of_add_words")
        pre_issue3_word = issue123_word[selected_issue1][selected_issue2]
        st.json(pre_issue3_word)

        new_words = st.text_input("Add new words for selected 2nd level issue: (separate them with English commas)",
                                  key=f"new_words_{i}", placeholder="word1,word2")

        if issue123_new_words.get(selected_issue1):
            if issue123_new_words[selected_issue1].get(selected_issue2):
                issue123_new_words[selected_issue1][selected_issue2].update(set(new_words.split(",")))
            else:
                issue123_new_words[selected_issue1][selected_issue2] = set(new_words.split(","))
        else:
            issue123_new_words[selected_issue1] = {selected_issue2: set(new_words.split(","))}

    colc1, colc2, buffc = st.columns([1, 1, 3])
    word_add_button = colc1.button("Add", key="add3", on_click=add3)
    if st.session_state.word_add_num > 0:
        word_delete_button = colc2.button("Delete", key="delete3", on_click=delete3)
    buffc.button("Save", key="save3", on_click=save3, args=(issue123_new_words,))

# (part1.1) add new issues
# # load database
# with open("./data/demo.pkl", "rb") as f:
#     issue_word_db = pickle.load(f)
#     issues = list(issue_word_db.keys())

# st.info("**If you want to add a new issue, please click the button below.**")
#
# def add1():
#     st.session_state.issue_add_num += 1
#
# def delete1():
#     st.session_state.issue_add_num -= 1
#
# with st.expander("Add issues"):
#     for i in range(st.session_state.issue_add_num):
#         st.header(f"New Issue {i + 1}")
#         # coli1, coli2 = st.columns([3, 1])
#         # coli1.text_input("Add a new issue here:", key=f"info1_{i}", placeholder="an issue")
#         # coli1.text_input("Add related words: (separate them with english commas)", key=f"info2_{i}", placeholder="key w ord 1,key word 2")
#         st.text_input("Add a new issue here:", key=f"info1_{i}", placeholder="an issue")
#         st.text_input("Add related words: (separate them with english commas)", key=f"info2_{i}", placeholder="key word 1,key word 2")
#
#     col1, col2, buff1 = st.columns([1, 1, 3])
#     add_issue_word_button = col1.button("Add issue", key="add_issue_word_button", on_click=add1)
#     if st.session_state.issue_add_num > 0:
#         issue_word_delete_button = col2.button("Delete one", key="delete_issue_word_button", on_click=delete1)
#     buff1.button("Save", key="save1")
#
# st.info("**If you want to add new words to some issues, please click the button below.**")
#
# def add2():
#     st.session_state.word_add_num += 1
#
# def delete2():
#     st.session_state.word_add_num -= 1
#
# with st.expander("Add words"):
#     for i in range(st.session_state.word_add_num):
#         st.header(f"New Words {i + 1}")
#         st.selectbox("Select an issue here:", issues, key=f"info3_{i}")
#         st.text_input("Add related words: (separate them with english commas)", key=f"info4_{i}", placeholder="key word 1,key word 2")
#
#     col3, col4, buff2 = st.columns([1, 1, 3])
#     add_word_button = col3.button("Add words", key="add_word_button", on_click=add2)
#     if st.session_state.word_add_num > 0:
#         word_delete_button = col4.button("Delete one", key="delete_word_button", on_click=delete2)
#     buff2.button("Save", key="save2")