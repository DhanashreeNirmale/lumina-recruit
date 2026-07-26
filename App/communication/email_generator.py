from langchain_core.prompts import PromptTemplate
from App.llm.llm import llm

from .prompts import (
    SHORTLIST_PROMPT,
    REJECTION_PROMPT,
    INTERVIEW_PROMPT
)


def generate_shortlist_email(name, role, skills):

    prompt = PromptTemplate.from_template(SHORTLIST_PROMPT)

    chain = prompt | llm

    response = chain.invoke({
        "name": name,
        "role": role,
        "skills": skills
    })

    return response.content


def generate_rejection_email(name, role):

    prompt = PromptTemplate.from_template(REJECTION_PROMPT)

    chain = prompt | llm

    response = chain.invoke({
        "name": name,
        "role": role
    })

    return response.content


def generate_interview_email(name, role, date, time, link):

    prompt = PromptTemplate.from_template(INTERVIEW_PROMPT)

    chain = prompt | llm

    response = chain.invoke({
        "name": name,
        "role": role,
        "date": date,
        "time": time,
        "link": link
    })

    return response.content