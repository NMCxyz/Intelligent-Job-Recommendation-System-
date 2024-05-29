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
