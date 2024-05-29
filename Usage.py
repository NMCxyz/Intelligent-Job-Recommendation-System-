import spacy
import json
import en_core_web_lg
import numpy as np

from spacy.matcher import PhraseMatcher
from Skills_Detection.Skill_Extractor import SkillExtractor
from Skills_Detection.GeneralParameter import SKILL_DB

nlp = en_core_web_lg.load()

skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
skills_from_resume = """
JOHANN BACH
FRONT-END DEVELOPER
CONTACT
johannbach@email.com
(123) 456-7890
Portland, OR
bachtothefuture.com
linkedin.com/in/jo-bach
EDUCATION
Bachelor of Science
Computer Science
University of Oregon
2014 - 2018
Eugene, OR
SKILLS
Languages
HTML
CSS
JavaScript
Python
Libraries
React
jQuery
Redux
Frameworks
Angular.js
Node.js
Testing
Jest
CAREER OBJECTIVE
Front-End Developer with proven experience at Zillow and HubSpot in
helping companies create and maintain a better code base for reusability.
Capable of continuous learning from senior developers while still
nurturing junior developers. Experience in driving projects forward as the
development team leader, facilitating projects from concept to launch.
Passionate about learning and development with a desire to apply skills
on a larger development team at Redﬁn. Eager to tackle more complex
problems and continue to ﬁnd ways to maximize user efﬁciency.
WORK EXPERIENCE
Front-End Developer
HubSpot
May 2020 - June 2021 / Remote
· Developed membership, event, and legal platform technology
solutions, and automated internal processes.
· Generated $50K+ in annual ad revenue as a system administrator
of a large network of websites.
· Designed and implemented web applications along with 3rd-party
software integrations as a web team liaison for all inter-
departmental and customer-facing projects.
· Developed a node.js server to validate membership and track
digital badges being used, saving the company $22.5K.
· Mentored 6 team members, enabling them to achieve professional
growth and personal goals.
Software Engineer I
Zillow
July 2018 - March 2020 / Portland, OR
· Developed real estate valuation, analytics, and platform technology
solutions as part of a 5-person team.
· Designed and developed Zestimate, which manages a volume of
600k+ valuations per month.
· Reduced average valuation review time by 46%, and saved service
providers an average of 84% due to click-fee reductions.
· Rebuilt 4-year-old SaaS application in React 15 and Redux with full
user experience redesign to release a beta MVP in 8 months.
· Integrated an automated property valuation model fed by machine
learning Python data.
· Created non-technical descriptions of operations and workﬂow to
enable non-coding team to function with minimal interruption.


"""

skills_from_job_description = """
Skills * Programming Languages: Python (pandas, numpy, scipy, scikit-learn, matplotlib), Sql, Java, JavaScript/JQuery. * Machine learning: Regression, SVM, NaÃ¯ve Bayes, KNN, Random Forest, Decision Trees, Boosting techniques, Cluster Analysis, Word Embedding, Sentiment Analysis, Natural Language processing, Dimensionality reduction, Topic Modelling (LDA, NMF), PCA & Neural Nets. * Database Visualizations: Mysql, SqlServer, Cassandra, Hbase, ElasticSearch D3.js, DC.js, Plotly, kibana, matplotlib, ggplot, Tableau. * Others: Regular Expression, HTML, CSS, Angular 6, Logstash, Kafka, Python Flask, Git, Docker, computer vision - Open CV and understanding of Deep learning.Education Details \r\n\r\nData Science Assurance Associate \r\n\r\nData Science Assurance Associate - Ernst & Young LLP\r\nSkill Details \r\nJAVASCRIPT- Exprience - 24 months\r\njQuery- Exprience - 24 months\r\nPython- Exprience - 24 monthsCompany Details \r\ncompany - Ernst & Young LLP\r\ndescription - Fraud Investigations and Dispute Services   Assurance\r\nTECHNOLOGY ASSISTED REVIEW\r\nTAR (Technology Assisted Review) assists in accelerating the review process and run analytics and generate reports.\r\n* Core member of a team helped in developing automated review platform tool from scratch for assisting E discovery domain, this tool implements predictive coding and topic modelling by automating reviews, resulting in reduced labor costs and time spent during the lawyers review.\r\n* Understand the end to end flow of the solution, doing research and development for classification models, predictive analysis and mining of the information present in text data. Worked on analyzing the outputs and precision monitoring for the entire tool.\r\n* TAR assists in predictive coding, topic modelling from the evidence by following EY standards. Developed the classifier models in order to identify "red flags" and fraud-related issues.\r\n\r\nTools & Technologies: Python, scikit-learn, tfidf, word2vec, doc2vec, cosine similarity, NaÃ¯ve Bayes, LDA, NMF for topic modelling, Vader and text blob for sentiment analysis. Matplot lib, Tableau dashboard for reporting.\r\n\r\nMULTIPLE DATA SCIENCE AND ANALYTIC PROJECTS (USA CLIENTS)\r\nTEXT ANALYTICS - MOTOR VEHICLE CUSTOMER REVIEW DATA * Received customer feedback survey data for past one year. Performed sentiment (Positive, Negative & Neutral) and time series analysis on customer comments across all 4 categories.\r\n* Created heat map of terms by survey category based on frequency of words * Extracted Positive and Negative words across all the Survey categories and plotted Word cloud.\r\n* Created customized tableau dashboards for effective reporting and visualizations.\r\nCHATBOT * Developed a user friendly chatbot for one of our Products which handle simple questions about hours of operation, reservation options and so on.\r\n* This chat bot serves entire product related questions. Giving overview of tool via QA platform and also give recommendation responses so that user question to build chain of relevant answer.\r\n* This too has intelligence to build the pipeline of questions as per user requirement and asks the relevant /recommended questions.\r\n\r\nTools & Technologies: Python, Natural language processing, NLTK, spacy, topic modelling, Sentiment analysis, Word Embedding, scikit-learn, JavaScript/JQuery, SqlServer\r\n\r\nINFORMATION GOVERNANCE\r\nOrganizations to make informed decisions about all of the information they store. The integrated Information Governance portfolio synthesizes intelligence across unstructured data sources and facilitates action to ensure organizations are best positioned to counter information risk.\r\n* Scan data from multiple sources of formats and parse different file formats, extract Meta data information, push results for indexing elastic search and created customized, interactive dashboards using kibana.\r\n* Preforming ROT Analysis on the data which give information of data which helps identify content that is either Redundant, Outdated, or Trivial.\r\n* Preforming full-text search analysis on elastic search with predefined methods which can tag as (PII) personally identifiable information (social security numbers, addresses, names, etc.) which frequently targeted during cyber-attacks.\r\nTools & Technologies: Python, Flask, Elastic Search, Kibana\r\n\r\nFRAUD ANALYTIC PLATFORM\r\nFraud Analytics and investigative platform to review all red flag cases.\r\nâ\x80¢ FAP is a Fraud Analytics and investigative platform with inbuilt case manager and suite of Analytics for various ERP systems.\r\n* It can be used by clients to interrogate their Accounting systems for identifying the anomalies which can be indicators of fraud by running advanced analytics\r\nTools & Technologies: HTML, JavaScript, SqlServer, JQuery, CSS, Bootstrap, Node.js, D3.js, DC.js
"""

annotations = skill_extractor.annotate(skills_from_resume)
def filter_it_skills_and_update(annotations):
    annotations["results"]["full_matches"] = [
        item for item in annotations["results"]["full_matches"]
        if item.get("skill_category") == "Information Technology"
    ]
    annotations["results"]["ngram_scored"] = [
        item for item in annotations["results"]["ngram_scored"]
        if item.get("skill_category") == "Information Technology"
    ]
    return annotations
annotations = filter_it_skills_and_update(annotations)


def convert(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


with open('E:\\C\\ICT\\Graduation_Research_1\\Code\\MyAI_Recruitment\\Data\\OutputPDF\\Output_skills.json', 'w') as file:
    json.dump(annotations, file, default=convert)