from unidecode import unidecode
import json
import tempfile
from Skills_Detection.Skill_Extractor import SkillExtractor
from Skills_Detection.GeneralParameter import SKILL_DB
from Skills_Detection.Resume_Extractor import PDFSkillsExtractor

import pickle
import streamlit as st

import Job_Recommender
from Network_Builder import *
import LSA



st.set_page_config(page_title='The Ultimate Jobs Recommender', page_icon=None,
    layout="centered", initial_sidebar_state="auto", menu_items=None)

st.header('The Ultimate Jobs Recommender')
page = st.sidebar.radio('Choose Your Page',
    options=['Input Resume', 'Your Information', 'Recommended for you', 'Search'], index = 0)

alpha = st.sidebar.slider('Damping Probability', min_value=0., max_value=1., value=0.5, step=0.1)
st.sidebar.markdown("""The larger the damping probability, the more personalized the results are to you. 
                    """)

@st.cache(allow_output_mutation  = True)
# @st.cache_data
def load_recommender():
    graphpath =  r'E:\C\ICT\Graduation_Research_1\Code\MyAI_Recruitment\Data\NetworkDB\graph.pkl'
    lsapath = r'E:\C\ICT\Graduation_Research_1\Code\MyAI_Recruitment\Data\NetworkDB\lsa.pkl'
    with open(graphpath, 'rb') as f:
        G = pickle.load(f)

    with open(lsapath, 'rb') as f:
        lsa = pickle.load(f)

    jrec = Job_Recommender.JobRecommender(G, lsa)

    return jrec

all_expertises = ['Java Developer', 'Testing', 'DevOps Engineer', 'Python Developer',
        'Web Designing', 'Hadoop', 'Blockchain', 'ETL Developer',
        'Operations Manager', 'Data Science', 'Mechanical Engineer',
        'Database', 
        'Business Analyst', 'DotNet Developer', 'Automation Testing',
        'Network Security Engineer', 'SAP Developer', 'Civil Engineer',
        ]


if page == 'Input Resume':
    uploaded_file = st.file_uploader("Upload your resume in PDF format", type="pdf")
    if uploaded_file is not None:   
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        pdf_skills_extractor = PDFSkillsExtractor(temp_file_path, "All")
        json_data = pdf_skills_extractor.extract_skills_from_pdf()
        st.success('Resume uploaded and processed successfully.')
        st.json(json.loads(json_data))
    
        all_skills = pdf_skills_extractor.extract_all_skills_name(json_data)
        st.session_state['resume_text'] = all_skills
        st.text_area("All skills in resume", value=all_skills, height=300, help="The text extracted from your resume.")

jrec = load_recommender()
user_data = {}

if page == 'Your Information':
    user_expertises = st.selectbox('Choose your expertise', options=all_expertises, index = 3)
    if len(user_expertises) < 1:
        st.info('Please tell us your expertises')

    if len(user_expertises) > 0:
        
        user_resume = st.text_area(label='Enter your resume',
                                value=st.session_state.get('resume_text', ''),
                                height=300,
                                placeholder="My research interest are Machine learning,...")
        if 1 < len(user_resume) < 100:
            st.info('Please give us a longer resume :(')
            
    user_data['expertise'] = user_expertises.strip()
    user_data['resume'] = user_resume
    if len(user_data['resume']) > 100:
        jrec.add_node_to_graph('candidate', user_data)

elif page == 'Recommended for you':
    num_recommend = 10
    personalized_results = jrec.rank_nodes(True, jrec.target_node, 'job', alpha)
    personalized_results = {key:item for i, (key,item) in enumerate(personalized_results.items()) if i < num_recommend}     
    c1, c2, c3, c4, c5 = True, False, False, False, False
    col1, col2, col3, col4, col5 = st.columns(5)
    st.markdown(f"Most {num_recommend} relevant jobs for you.")
    for key, value in personalized_results.items():
        job_node = jrec.G.nodes[key]
        company_id = job_node['company_id']
        logo = jrec.G.nodes[company_id]['logo_link']
        
        if c1:                
            with col1:
                st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                c1, c2, c3, c4, c5 = False, True, False, False, False
                continue
        elif c2:
            with col2:
                st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                c1, c2, c3, c4, c5 = False, False, True, False, False
                continue
        elif c3:
            with col3:
                st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                c1, c2, c3, c4, c5 = False, False, False, True, False
                continue

        elif c4:
            with col4:
                st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                c1, c2, c3, c4, c5 = False, False, False, False, True
                continue
        elif c5:
            with col5:
                st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                c1, c2, c3, c4, c5 = True, False, False, False, False
                continue

elif page == 'Search':
    # if no node has added to the network, means user
    # does not provide any information, recommend the most
    # popular jobs in the network
    if jrec.target_node is None:
        # st.markdown("**Those are the most popular jobs in our network.**")
        # st.json(jrec.rank_nodes(personalized = False,
        #         target_node = jrec.target_node,
        #         return_node_type='job',
        #         alpha = alpha))
        st.text("Please enter your information in Your Information first")
    else:    
        search_keywords = st.text_input('Search', placeholder='Keywords skill (Solidity, Python), Job title, ...')
        if len(search_keywords) > 3:
            # First, search for all node that match the keywords
            search_results = jrec.search(search_keywords)
            # Then rank the nodes personalized to the user node and the context node.
            personalized_results = jrec._rank_node_with_context(jrec.target_node, 
                                        search_results, alpha, 'job')
            c1, c2, c3, c4, c5 = True, False, False, False, False
            col1, col2, col3, col4, col5 = st.columns(5)
            st.markdown(f"Found {len(personalized_results)} jobs out of {jrec.G.graph['num_jobs']} jobs.")
            for key, value in personalized_results.items():
                job_node = jrec.G.nodes[key]
                company_id = job_node['company_id']
                logo = jrec.G.nodes[company_id]['logo_link']
                
                if c1:                
                    with col1:
                        st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                        c1, c2, c3, c4, c5 = False, True, False, False, False
                        continue
                elif c2:
                    with col2:
                        st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                        c1, c2, c3, c4, c5 = False, False, True, False, False
                        continue
                elif c3:
                    with col3:
                        st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                        c1, c2, c3, c4, c5 = False, False, False, True, False
                        continue

                elif c4:
                    with col4:
                        st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                        c1, c2, c3, c4, c5 = False, False, False, False, True
                        continue
                elif c5:
                    with col5:
                        st.image(logo, caption = job_node['job_name'], width=60, use_column_width = 'always' )
                        c1, c2, c3, c4, c5 = True, False, False, False, False
                        continue
            # st.json(personalized_results)
        else:
            st.info('Enter your search keywords')