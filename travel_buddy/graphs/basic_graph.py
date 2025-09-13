from typing import Dict

from langgraph.graph import StateGraph, START, END

from ..chains.basic_chain import run_basic_chain


def call_llm(state: Dict) -> Dict:
    question = state.get("question", "")
    answer = run_basic_chain(question)
    return {"question": question, "answer": answer}


def build_graph():
    graph = StateGraph(dict)
    graph.add_node("llm", call_llm)
    graph.add_edge(START, "llm")
    graph.add_edge("llm", END)
    return graph.compile()


def run_graph(question: str) -> Dict:
    app = build_graph()
    return app.invoke({"question": question})
