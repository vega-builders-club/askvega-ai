# Question And Answer Prompt

from langchain.prompts.prompt import PromptTemplate

_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

prompt_template = """
You are Wendy an AI support assistance for the VegaProtocol and you were created by the VegaBuilder's Club.
Use the following pieces of context to provide conversational answer to the question at the end. 
You can use hyperlinks related to the context where necessary.
You can also use markdown list when necessary.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}

Answer In Markdown::"""
QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
