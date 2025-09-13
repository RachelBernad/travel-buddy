from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_huggingface.llms import HuggingFacePipeline

from ..models.hf_loader import load_local_hf_pipeline


def build_basic_chain() -> LLMChain:
    pipe = load_local_hf_pipeline()
    llm = HuggingFacePipeline(pipeline=pipe)

    template = """
You are a helpful travel assistant.
User: {question}
Assistant:
""".strip()

    prompt = PromptTemplate(template=template, input_variables=["question"]) 
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain


def run_basic_chain(question: str) -> str:
    chain = build_basic_chain()
    return chain.run(question)
