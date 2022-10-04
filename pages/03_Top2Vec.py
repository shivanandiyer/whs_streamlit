import streamlit as st
import pandas as pd
from top2vec import Top2Vec
st.set_option('deprecation.showPyplotGlobalUse', False)

st.header('Top2Vec')

# test

#st.write('testing df_working sessison state')
if "df_working" not in st.session_state:
    st.write('Please upload a json file in previous page')
else:

    df_working = st.session_state['df_working']
    proceed_button_t2v =  st.button('Proceed with Top2Vec')

    if ['proceed_button_t2v'] not in st.session_state:
        st.session_state.proceed_button_t2v = False

    if proceed_button_t2v:
        st.session_state.proceed_button_t2v = True
        with st.spinner(text="In progress... This can take a few minutes"):

            # = Top2Vec(df_working.Data.values.tolist()) #,embedding_model = sentence_model
            if 'top2vec_model' not in st.session_state:
                st.session_state.top2vec_model = False

            top2vec_model = Top2Vec(df_working.Data.values.tolist())
            st.session_state.top2vec_model = top2vec_model
        #global top2vec_model

        if st.session_state.top2vec_model is not False and st.session_state.proceed_button_t2v == True:

            if 'top2vec_topic_nums' not in st.session_state:
                st.session_state['top2vec_topic_nums'] = False

            top2vec_topic_sizes, top2vec_topic_nums = top2vec_model.get_topic_sizes()

            st.session_state['top2vec_topic_nums'] = top2vec_topic_nums
            top2vec_topic_nums_series = pd.Series(top2vec_topic_nums,name = 'topic_id')
            top2vec_topic_sizes_series = pd.Series(top2vec_topic_sizes,name = 'topic size')

            st.write('top2vec_topic_sizes_series')
            st.write(top2vec_topic_sizes_series)
