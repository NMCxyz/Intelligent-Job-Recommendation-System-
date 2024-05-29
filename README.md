# Intelligent Job Recommendation System

## 🚀 System Architecture

The architecture of the system is illustrated in the following image, depicting the flow from data collection to job recommendations.

![System Architecture](Resume%20and%20Academic%20recommendation.png)

## 💡 Introduction

In an ever-evolving educational landscape, each year witnesses a large influx of graduates entering the job market, presenting a significant challenge for businesses and organizations to sift through and select the most suitable candidates from a highly competitive pool of applicants. This project focuses on the development of an automated system capable of extracting skill information from resumes and compiling data to assist employers in easily identifying and selecting candidates based on their skill set.

## 🛠️ Features

- **Lightcast Skills API Integration**: Fetch IT-related skills data according to the ontology of skills.
- **Data Crawling**: Use spiders to crawl job and company data from itviec.com.
- **Graph Construction**: Build a graph using `Network_Builder.py` for the PageRank algorithm, containing employers, jobs, and candidates.

## 📝 Requirements

To install the necessary dependencies, run:

```bash
pip install -r requirements.txt
```
## 🚀 Getting Started
To run the application, use the following command:

```bash
streamlit run app.py
```
## 📊 Data Collection and Processing
Lightcast Skills API: The system uses the Lightcast Open Skills API to fetch a comprehensive dataset of IT skills and their ontology.
Web Crawling: Job and company data are crawled from itviec.com using spiders.
Graph Construction: The Network_Builder.py script constructs a graph for the PageRank algorithm. The graph includes nodes for employers, jobs, and candidates.
## 🕸️ Crawling Data from itviec.com
The data crawling process involves using spiders to fetch job listings and company information from itviec.com. This data is then used to build the job recommendation system.

## 📈 Building the Graph
To construct the graph used for the PageRank algorithm, run the following script:

```bash
python Network_Builder.py
```
The graph includes nodes representing employers, jobs, and candidates, and edges representing relationships such as job postings and skill matches.

## ⚠️ Notes
Ensure all necessary dependencies are installed by running pip install -r requirements.txt.
Make sure to update the configurations in the project as per your environment settings.
## 📧 Contact
For any inquiries, please contact:

Nguyễn Mạnh Cường
Email: cuongtls123@gmail.com

## 📚 References

- **A Recommender System for Job Seeking and Recruiting Website**
  
- **The 3A Personalized, Contextual and Relation-based Recommender System**

