# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate
# from langchain_core.runnables import RunnableSequence
# from langchain_huggingface.llms import HuggingFacePipeline
#
# from ..models.hf_loader import load_local_hf_pipeline
#
# def run_basic_chain(question: str) -> str:
#     """Run the basic chain with a simple prompt."""
#     from ..models.llm_loader import generate
#
#     # Simple template for basic responses
#     prompt = f"""You are a helpful travel assistant.
# User: {question}
# Assistant:"""
#
#     # Use the unified generate function with proper parameters
#     response = generate(prompt)
#
#     # Extract just the assistant's response (remove the prompt)
#     if "Assistant:" in response:
#         return response.split("Assistant:")[-1].strip()
#     return response.strip()
