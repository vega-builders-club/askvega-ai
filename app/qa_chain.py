# Question And Answer Handler
from typing import List
from langchain.schema import Document
from langchain.callbacks.base import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.vectorstores.base import VectorStore, VectorStoreRetriever
from qa_prompts import CONDENSE_QUESTION_PROMPT, QA_PROMPT


async def aget_relevant_documents(self, query: str) -> List[Document]:
    return self.get_relevant_documents(query)

VectorStoreRetriever.aget_relevant_documents = aget_relevant_documents


def get_chain(vectorstore: VectorStore, question_handler, stream_handler, tracing: bool = False) -> ConversationalRetrievalChain:
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])

    if tracing:
        tracer = LangChainTracer()
        tracer.load_default_session()
        manager.add_handler(tracer)
        question_manager.add_handler(tracer)
        stream_manager.add_handler(tracer)

    question_lim = OpenAI(
        temperature=0, verbose=True, callback_manager=question_manager)

    streaming_lim = OpenAI(temperature=0, verbose=True,
                           callback_manager=stream_manager, streaming=True)

    question_generator = LLMChain(
        llm=question_lim, prompt=CONDENSE_QUESTION_PROMPT, callback_manager=manager)

    doc_chain = load_qa_chain(
        streaming_lim, chain_type="stuff", prompt=QA_PROMPT, callback_manager=manager)

    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(), combine_docs_chain=doc_chain, question_generator=question_generator, callback_manager=manager)

    return qa
