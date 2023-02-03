# -*- coding:utf-8 -*-
"""
 作者: QL
 日期: 2023年01月19日
"""
# Import from standard library
import os
import time
import pickle
import string
import numpy as np
from typing import NoReturn

# Import from 3rd party libraries
import pandas as pd
import streamlit as st
import requests
import pdfplumber
from PyPDF2 import PdfReader
import nltk
from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer
from nltk import MWETokenizer
from nltk.tokenize import sent_tokenize
from nltk.corpus import wordnet

# initialize st.session_state (note: all pages in the web share the same st.session_state, so you can not use 'if not st.session_state')
sslist = ["num", "local_file_num"]
for ss in sslist:
    if ss not in st.session_state:
        st.session_state[ss] = 0

# load database
# Environment
with open("./data/demo.pkl", "rb") as f:
    ESGO_issue123_word_db = pickle.load(f)
    ESGO_factors = list(ESGO_issue123_word_db.keys())

with open("./data/code_time_link.pkl", "rb") as f:
    code_time_name_link = pickle.load(f)  # {(code, time): (name, link), (code, time): (name, link), ...}
    code_time_lst = list(code_time_name_link.keys())  # [(code, time), (code, time), ...]
    code_set = set(map(lambda x: x[0], code_time_lst))  # unique codes


def sort_with_first_letter(lst: list):
    """
    对list的元素依据英文首字母排序
    :param lst: 待排序列表
    :return: sorted_lst
    """
    sorted_lst = lst.copy()
    sorted_lst.sort(key=lambda x: str.lower(x[0]))
    return sorted_lst


def get_issue3s(selected_issue1, issue123_word):
    selected_issue23_word = issue123_word[selected_issue1]
    issue3s = [i for s in list(map(lambda x: x[0], selected_issue23_word.values())) for i in s]
    return issue3s


def get_words(selected_issue1, selected_issue3, issue123_word):
    issue23_word = issue123_word[selected_issue1]
    for val in issue23_word.values():
        if selected_issue3 in val[0]:
            return val[1]


# (part1) select issues
st.header("(Part1) Select issues")
ESGO = st.selectbox("Please select one factor:", ESGO_factors)

selected_issue13_dict = {}
if ESGO:
    issue123_word = ESGO_issue123_word_db[ESGO]
    issue1s = list(issue123_word.keys())
    selected_issue1s = st.multiselect("Please select 1st level issue:", issue1s, key="E_first_level_issue")
    if selected_issue1s:
        for selected_issue1 in selected_issue1s:
            issue123_word = ESGO_issue123_word_db[ESGO]
            issue3s = get_issue3s(selected_issue1, issue123_word)
            selected_issue3s = st.multiselect(f"Please select {selected_issue1}'s 3rd level issues:", issue3s, key=f"selected_issue3s_of_{selected_issue1}")
            selected_issue13_dict[selected_issue1] = selected_issue3s


# # if we want to prioritize the issues, the following comment might be a solution
# a = np.array([2, 3, 1, 3])
# b = np.array(['issue2', 'issue0', 'issue1', 'issue3'])
# issues = b[np.argsort(a)]
# selected_issues = st.multiselect("Please choose issues:", issues, help="You can select just by click or enter some letters to quicken your selecting process")

# (part2) select related words according to selected issues
st.header("(Part2) Select words")
selected_issue13_word_dict = {}
if selected_issue13_dict:
    for selected_issue1 in selected_issue13_dict.keys():
        selected_issue13_word_dict[selected_issue1] = {}
        with st.expander(f"{selected_issue1}"):
             for selected_issue3 in selected_issue13_dict[selected_issue1]:
                 issue123_word = ESGO_issue123_word_db[ESGO]
                 words = get_words(selected_issue1, selected_issue3, issue123_word)
                 selected_words = st.multiselect(f"Please select {selected_issue3}'s related words:", words, key=f"selected_words_of_{selected_issue1}_and_{selected_issue3}")
                 selected_issue13_word_dict[selected_issue1][selected_issue3] = selected_words

    # selected_issues_words = {}
    # for i, issue in enumerate(selected_issues):
    #     st.subheader(f"{i + 1}{issue}")
    #     selected_words = st.multiselect("Please choose words:", issue_word_db[issue])
    #     selected_issues_words[issue] = selected_words

# (part3) select company and year for ESG reports
st.header("(Part3) Company & Year")


def add1():
    st.session_state.num += 1


def delete1():
    st.session_state.num -= 1


def add2():
    st.session_state.local_file_num += 1


def delete2():
    st.session_state.local_file_num -= 1


@st.cache
def load_online_pdf(pdf_link: str, stock_code: str, time: str) -> str:
    """
    save online pdf to a temporary local  pdf file
    :param local_pdf: saved pdf file name
    :param pdf_link: online pdf's url link
    :return: local temporary pdf path
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
    proxies = None
    url_params = {'headers': headers, 'proxies': proxies}

    response = requests.get(pdf_link, **url_params)

    # 写入临时文件再进行解析
    # if os.path.exists(local_pdf):
    #     pass
    # else:
    #     with open(local_pdf, 'wb') as f:
    #         f.write(response.content)
    #
    #     pdf_path = os.path.abspath(local_pdf)
    #     return pdf_path

    local_pdf = f'~temp{stock_code}_{time}~.pdf'
    with open(local_pdf, 'wb') as f:
        f.write(response.content)

    pdf_path = os.path.abspath(local_pdf)
    return pdf_path


def delete_temp_pdf(pdf_path: str) -> NoReturn:
    """
    delete temporary pdf file
    :param pdf_path: local path of temporary pdf file
    :return: no return
    """
    try:
        os.remove(pdf_path)
    except Exception as e:
        pass


stkcd_time_pdf = []
with st.expander("Select Company & Year"):
    for i in range(st.session_state.num):
        col1, col2 = st.columns([1.5, 1.5])
        # stock_code = col1.text_input("Stock Code", key=f"stock_code{i}", label_visibility="collapsed", placeholder="Stock Code: 00001.HK")
        stock_code = col1.selectbox("Stock Code", code_set, key=f"stock_code{i}")
        # release_time = col2.text_input("Release Time", label_visibility="collapsed", placeholder="Year: 2020")
        if stock_code in code_set:
            time_lst = list(filter(None, map(lambda x: x[1] if x[0] == stock_code else None, code_time_lst)))
            release_time = col2.selectbox("Release Time", time_lst, key=f"release_time{i}")
            if release_time:
                # get name and link, and then save pdf to local path
                name = code_time_name_link[(stock_code, release_time)][0]
                link = code_time_name_link[(stock_code, release_time)][1]
                # 这里local_pdf要设计个逻辑，不能让它们反复跑这个好吧
                # local_pdf = f'~temp{stock_code}_{name}~.pdf'
                col1.markdown(f"Report name:&nbsp;[{name}]({link})")
                time = col2.text_input("Report Time", key=f"report_time1{i}", placeholder="2021")
                if time:
                    pdf_path = load_online_pdf(link, stock_code, time)
                # save user input info
                if time:
                    info = (stock_code, time, pdf_path)
                    if info not in stkcd_time_pdf:
                        stkcd_time_pdf.append(info)
    for i in range(st.session_state.local_file_num):
        coli1, coli2 = st.columns([1.5, 1.5])
        stock_code = coli1.text_input("Stock Code", key=f"stock_code_local{i}", placeholder="00001.HK")
        # release_time = coli2.text_input("Release Time", key=f"release_time_local{i}", placeholder="01/01/2023")
        # name = coli2.text_input("Report Name", key=f"name{i}", placeholder="长和2021年ESG报告")
        time = coli2.text_input("Report Time", key=f"report_time2{i}", placeholder="2021")

        # coli3, coli4, buffi1 = st.columns([1, 1, 4])
        # use_url_link = coli3.button("Use url link", key=f"use_url_link{i}")
        # local_file = coli4.button("Local file", key=f"local_file{i}")
        #
        # if use_url_link:
        #     exec(f"st.session_state.local_file{i} = 0")
        #     pdf_link = st.text_input("PDF url link", key=f"pdf_link{i}")
        #     if pdf_link:
        #         pdf_path = load_online_pdf(pdf_link)
        # elif local_file:
        #     exec(f"st.session_state.use_url_link{i} = 0")
        #     pdf_path = st.file_uploader("load pdf", key=f"pdf{i}", help="load pdf here", label_visibility="collapsed")

        if stock_code and time:
            use_url_link = st.checkbox("Use url link", key=f"use_url_link{i}")
            if use_url_link:
                pdf_link = st.text_input("PDF url link", key=f"pdf_link{i}")
                if pdf_link:
                    pdf_path = load_online_pdf(pdf_link, stock_code, time)
                    # save user input info
                    info = (stock_code, time, pdf_path)
                    stkcd_time_pdf.append(info)
            else:
                pdf_path = st.file_uploader("load pdf", key=f"pdf{i}", help="load pdf here", label_visibility="collapsed")
                # save user input info
                if pdf_path:
                    info = (stock_code, "(local)" + time, pdf_path)
                    stkcd_time_pdf.append(info)
        ## (NOTE!!) 这里要判断大表中有没有这个股票代码和年份。如果没有，下面要添加报告获取方式，比如文件下载，或者链接输入

    col3, col4, buff1, col5, col6, buff2 = st.columns([0.7, 0.5, 2.7, 1.5, 1, 1.3])
    st.info("If the database doesn't contain your report infomation, please turn to page 3 and add new stock, release time, report name and report link.")
    button_add1 = col3.button("➕", key="add_button1", on_click=add1)
    button_add2 = col5.button("Add local file", key="add_button2", on_click=add2)
    if st.session_state.num > 0:
        button_delete1 = col4.button("➖", key="delete_button1", on_click=delete1)
    if st.session_state.local_file_num > 0:
        button_delete2 = col6.button("Delete", key="delete_button2", on_click=delete2)
        # button_check = col5.button("Check", key="check_button", on_click=check)

# with st.form("1"):
#     submit_button = st.form_submit_button("Submit")
#     if submit_button:
#         for i in range(st.session_state.num):
#             exec(f"st.write(st.session_state.info_{i})")

# (part4) Searching Range
st.header("(Part4) Select Searching Range")


def get_outline_text(outline_dicts):
    outline_text = []
    for outline_dict in outline_dicts:
        if isinstance(outline_dict, dict):
            outline_text.append(outline_dict['/Title'])
        else:
            get_outline_text(outline_dict)
    return outline_text


def cursor_to_page(pdf, pages=None, result=None, num_pages=None):
    if result is None:
        result = {}
    if pages is None:
        num_pages = []
        pages = pdf.trailer["/Root"].get_object()["/Pages"].get_object()
    t = pages["/Type"]
    if t == "/Pages":
        for page in pages["/Kids"]:
            result[page.idnum] = len(num_pages)
            cursor_to_page(pdf, page.get_object(), result, num_pages)
    elif t == "/Page":
        num_pages.append(1)
    return result


def get_outline_pages(f):
    pdf = PdfReader(f)
    outline_dict = pdf.outline
    outline_list = get_outline_text(outline_dict)

    pg_id_num_map = cursor_to_page(pdf)
    pg_num = []
    for i in range(len(outline_list)):
        if type(outline_dict[i]) == list:
            continue
        else:
            pg_num.append(pg_id_num_map[outline_dict[i].page.idnum] + 1)

    # 章节名可能会包含markdown语法，要处理，这里只处理了一个，有其他情况再追加处理
    for i in range(len(outline_list)):
        if "." in outline_list[i]:
            outline_list[i] = "\.".join(outline_list[i].split("."))

    for chapter in outline_list:
        st.checkbox(chapter, key=f"{stkcd}_{time}_{chapter}")

    selected_chapter = []
    for chapter in outline_list:
        if st.session_state[f"{stkcd}_{time}_{chapter}"] == True:
            selected_chapter.append(1)
        else:
            selected_chapter.append(0)

    outline_page = list(zip(outline_list, selected_chapter, pg_num))

    with pdfplumber.open(f) as temp_pdf:
        tot_page = len(temp_pdf.pages)

    if outline_list:
        pg_range_id = []
        for i, (chapter, selected, page) in enumerate(outline_page):
            if selected == 1:
                if i == len(outline_page) - 1:
                    start_pg_id = page - 1
                    end_pg_id = tot_page - 1
                else:
                    start_pg_id = page - 1
                    end_pg_id = outline_page[i + 1][2] - 1  # 第一个-1是python索引
                pages_id = list(range(start_pg_id, end_pg_id))  # 不包含上界
                pg_range_id.extend(pages_id)
    else:
        pg_range_id = list(range(tot_page))
    return pg_range_id


stkcd_time_pdf_pages = []
if stkcd_time_pdf:
    with st.expander("Select Searching Range"):
        for i, (stkcd, time, pdf_path) in enumerate(stkcd_time_pdf):
            outline_page = None

            if "(local)" not in time:
                st.write(f"{stkcd}_{time}")
                with open(pdf_path, 'rb') as f:
                    pg_range_id = get_outline_pages(f)
            else:
                time = time[7:]
                st.write(f"{stkcd}_{time}")
                f = pdf_path
                pg_range_id = get_outline_pages(f)

            if pg_range_id:
                stkcd_time_pdf_pages.append((stkcd, time, pdf_path, pg_range_id))


# (Part5) Word-Frequency Analysis
def get_word_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def find_sents(original_temp_txt, word):
    """
    find sentences that contain certain words in one page
    :param temp_txt: text of one page
    :param word: key word
    :return: matched sentences
    """
    # all sentences in this page
    sents = sent_tokenize(original_temp_txt)
    # sentences matched
    selected_sent = []
    for sent in sents:
        if word in sent.lower():
            selected_sent.append("..." + sent + "...")

    return selected_sent


st.header("(Part5) Word-Frequency Analysis")
orientation = st.radio("Type of Result Display:", ("Stock Code Oriented", "Third Level Issue Oriented", "Text Form Display"))
analyse = st.button("Analyse")
if analyse:
    if selected_issue13_word_dict:
        with st.spinner('Wait for it...'):
            selected_issue1s = list(selected_issue13_word_dict.keys())
            tabs = st.tabs(selected_issue1s)
            for i, tab in enumerate(tabs):
                with tab:
                    issue1 = selected_issue1s[i]
                    selected_issue3_word_dict = selected_issue13_word_dict[issue1]
                    d = {}
                    for issue3 in selected_issue3_word_dict:
                        words = selected_issue3_word_dict[issue3]
                        words = list(map(lambda x: x.lower(), words))
                        with st.expander(f"Analysis of **_{issue3}_**"):
                            word_count_pg_sen_dict = {}  # (Stock Code Oriented)
                            stkcd_time_count_pg_sen_dict = {}  # (Third Level Issue Oriented)
                            for stkcd, time, pdf_path, pg_range_id in stkcd_time_pdf_pages:
                                with pdfplumber.open(pdf_path) as pdf:
                                    words_count_dict = {}  # -> {word: count -> int}
                                    page_sentence_dict = {}  # -> {word: (pages -> list, sentences -> list)}
                                    for pg_id in pg_range_id:
                                        # Get content of current pages
                                        original_temp_txt = pdf.pages[pg_id].extract_text()
                                        temp_txt = original_temp_txt.lower()

                                        # Cut words
                                        customized_phrases = []
                                        for word in words:
                                            temp_word = word.split(" ")
                                            if len(temp_word) > 1:
                                                customized_phrases.append(temp_word)
                                        tokenizer = MWETokenizer(customized_phrases, separator=' ')
                                        wordlist = tokenizer.tokenize(nltk.word_tokenize(temp_txt))
                                        filtered = [w for w in wordlist if w not in stopwords.words('english')]

                                        # Save count, pages and sentences
                                        for word in words:
                                            # word count
                                            word_num = filtered.count(word)
                                            words_count_dict[word] = words_count_dict.get(word, 0) + word_num

                                            # pages and sentences
                                            if word_num != 0:
                                                # sentence = "sentence"
                                                sents = find_sents(original_temp_txt, word)
                                                pg_num = [pg_id + 1] * len(sents)
                                                if page_sentence_dict.get(word):
                                                    pre_data = page_sentence_dict[word]
                                                    pre_pg = pre_data[0]
                                                    pre_sen = pre_data[1]
                                                    new_pg = pg_num
                                                    new_sen = sents
                                                    new_data = (pre_pg + new_pg, pre_sen + new_sen)
                                                    page_sentence_dict[word] = new_data
                                                else:
                                                    page_sentence_dict[word] = (pg_num, sents)
                                            else:
                                                if not page_sentence_dict.get(word):
                                                    page_sentence_dict[word] = ([], [])

                                    # (Stock Code Oriented) Save 'word_count_pg_sen_dict' -> (stkcd, time): [(word -> str, count -> int, pages -> list, sentences -> list), (...), ...]
                                    word_count_pg_sen_dict[(stkcd, time)] = list(zip(words_count_dict.keys(),
                                                                                     words_count_dict.values(),
                                                                                     list(map(lambda x: x[0], page_sentence_dict.values())),
                                                                                     list(map(lambda x: x[1], page_sentence_dict.values()))))

                                    # (Third Level Issue Oriented) Save 'stkcd_time_count_pg_sen_dict' -> word: [(stkcd -> str, time -> str, count -> int, pages -> list, sentences -> list), (...), ...]
                                    for word in words:
                                        if stkcd_time_count_pg_sen_dict.get(word):
                                            pre_data = stkcd_time_count_pg_sen_dict[word]
                                            new_data = pre_data + [(stkcd, time, words_count_dict[word], *page_sentence_dict[word])]
                                            stkcd_time_count_pg_sen_dict[word] = new_data
                                        else:
                                            stkcd_time_count_pg_sen_dict[word] = [(stkcd, time, words_count_dict[word], *page_sentence_dict[word])]

                            if orientation == "Stock Code Oriented":
                                for stkcd, time in word_count_pg_sen_dict:
                                    st.write(f"**_{stkcd}-{time}_**")
                                    one_stkcd_time_analysis_list = word_count_pg_sen_dict[(stkcd, time)]
                                    one_analysis_result = {}
                                    for word, count, pg_nums, sentences in one_stkcd_time_analysis_list:
                                        one_analysis_result[f"{word} count"] = pd.Series([str(count)])
                                        one_analysis_result[f"{word} page"] = pd.Series(list(map(lambda x: str(x), pg_nums)))
                                        one_analysis_result[f"{word} sentence"] = pd.Series(sentences)

                                    df_analysis = pd.DataFrame(one_analysis_result)
                                    st.write(df_analysis)

                            elif orientation == "Third Level Issue Oriented":
                                for word in stkcd_time_count_pg_sen_dict:
                                    st.write(f"**_{word}_**")
                                    one_word_analysis_list = stkcd_time_count_pg_sen_dict[word]
                                    one_analysis_result = {}
                                    for stkcd, time, count, pg_nums, sentences in one_word_analysis_list:
                                        one_analysis_result[f"{stkcd}-{time} info"] = pd.Series([stkcd, time, count])
                                        one_analysis_result[f"{stkcd}-{time} page"] = pd.Series(list(map(lambda x: str(x), pg_nums)))
                                        one_analysis_result[f"{stkcd}-{time} sentence"] = pd.Series(sentences)

                                    df_analysis = pd.DataFrame(one_analysis_result)
                                    st.write(df_analysis)

                            elif orientation == "Text Form Display":
                                for word in stkcd_time_count_pg_sen_dict:
                                    st.subheader(f"{word}")
                                    one_word_analysis_list = stkcd_time_count_pg_sen_dict[word]
                                    for stkcd, time, count, pg_nums, sentences in one_word_analysis_list:
                                        st.write(f"**_{stkcd}-{time}: {count}_**")
                                        for j in range(len(pg_nums)):
                                            st.markdown(f"P{pg_nums[j]}")
                                            sentence = sentences[j]
                                            sent_lst = sentence.lower().split(word)
                                            stop = []
                                            for k in range(len(sent_lst) - 1):
                                                if stop:
                                                    stop.append([stop[k - 1][1] + len(sent_lst[k]), stop[k - 1][1] + len(sent_lst[k]) + len(word)])
                                                else:
                                                    stop.append([len(sent_lst[k]), len(sent_lst[k]) + len(word)])
                                            highlight_sent = ''
                                            for k in range(len(stop)):
                                                start_stop = stop[k][0]
                                                end_stop = stop[k][1]
                                                if k == 0:
                                                    if len(stop) == 1:
                                                        highlight_sent += sentence[: start_stop] + '<span style="background-color:rgb(255,255,0,0.5)">' + sentence[start_stop: end_stop] + '</span>' + sentence[end_stop:]
                                                    else:
                                                        next_start_stop = stop[k + 1][0]
                                                        highlight_sent += sentence[: start_stop] + '<span style="background-color:rgb(255,255,0,0.5)">' + sentence[start_stop: end_stop] + '</span>' + sentence[end_stop: next_start_stop]
                                                elif k == len(stop) - 1:
                                                    highlight_sent += '<span style="background-color:rgb(255,255,0,0.5)">' + sentence[start_stop: end_stop] + '</span>' + sentence[end_stop:]
                                                else:
                                                    next_start_stop = stop[k + 1][0]
                                                    highlight_sent += '<span style="background-color:rgb(255,255,0,0.5)">' + sentence[start_stop: end_stop] + '</span>' + sentence[end_stop: next_start_stop]


                                            st.markdown(f"{highlight_sent}", unsafe_allow_html=True)
                                            # st.markdown('<span style="background-color:rgb(255,255,0,0.5)">highlight 3</span>', unsafe_allow_html=True)
        st.success("Done!")

                    # for word in words:
                    #     d[(issue1, issue3)] = {word: df}


                                # for word in words_count_dict:
                                #     stkcd_time_count_dict[(stkcd, time, word)] = words_count_dict[word]

                                    # # 是否需要词性还原？
                                    # refiltered = nltk.pos_tag(filtered)
                                    # word_dict = {}
                                    # lemmas_sent = []
                                    # for wordtag in refiltered:
                                    #     wordnet_pos = get_word_pos(wordtag[1]) or wordnet.NOUN
                                    #     word = wnl.lemmatize(wordtag[0], pos=wordnet_pos)
                                    #     lemmas_sent.append(word)  # 词形还原
                                    #     word_dict[word] = word_dict.get(word, 0) + 1




        # for issue1 in selected_issue13_word_dict:
        #     with st.expander(f"Analysis of **_{issue1}_**"):
        #         selected_issue3_word_dict = selected_issue13_word_dict[issue1]
        #         for issue3 in selected_issue3_word_dict:
        #             st.write(f"{issue1}-{issue3}")
        #             words = selected_issue3_word_dict[issue3]

            # with st.expander(f"Analysis of **_{issue1}_**"):
            #     selected_issue3_word_dict = selected_issue13_word_dict[issue1]
            #     for issue3 in selected_issue3_word_dict:
            #         st.write(f"{issue1}-{issue3}")
            #         words = selected_issue3_word_dict[issue3]

