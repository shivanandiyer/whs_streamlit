import streamlit as st

if 'top2vec_model' not in st.session_state or st.session_state.top2vec_model == False:
    #st.session_state.top2vec_model = False

    st.write('Please run Top2Vec model first before looking at this page')

else:
    top2vec_model = st.session_state.top2vec_model
    df_working = st.session_state['df_working']

    st.write('find simlar words')

    if 'keywords_similar' not in st.session_state:
        st.session_state.keywords_similar = False


    keywords_similar = st.text_input('Find similar keyword')#.to_list()
    keywords_similar_button =  st.button('Search for keyword')

    if keywords_similar_button:
        st.session_state.keywords_similar = keywords_similar
        st.write('Searching for', keywords_similar)

        try:
            words, word_scores = top2vec_model.similar_words(keywords=[keywords_similar], keywords_neg=[], num_words=20)

            for word, score in zip(words, word_scores):
                st.write(f"{word} {score}")
        except:
            st.write(f"Keyword: {keywords_similar} hasn't been learnt by the model, please try another keyword")
