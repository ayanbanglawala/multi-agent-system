from dotenv import load_dotenv
load_dotenv()

import os

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=0.7
)

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert research writer."
    ),
    (
        "human",
        """
Topic:
{topic}

Research:
{research}

Create a professional report with:

# Introduction

# Key Findings

# Conclusion

# Sources
"""
    )
])

writer_chain = writer_prompt | llm | StrOutputParser()

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a strict research critic."
    ),
    (
        "human",
        """
Report:

{report}

Provide:

Score: X/10

Strengths:
- ...

Areas to Improve:
- ...

Verdict:
...
"""
    )
])

critic_chain = critic_prompt | llm | StrOutputParser()