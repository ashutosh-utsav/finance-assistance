import os
import json
import sys
from typing import TypedDict, List, Optional

# --- Add project root to the Python path ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Import agents and LangGraph components ---
from agents import retriever_agent, analysis_agent, llm_agent, scraper_agent
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate


# --- Configuration ---
PORTFOLIO_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'portfolio.json')
DAILY_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'daily_log.json')
CONFIDENCE_THRESHOLD = 1.2

# --- Define the State of our Graph ---
class GraphState(TypedDict):
    user_query: str
    intent_type: str 
    portfolio_data: dict
    previous_portfolio_data: Optional[dict]
    scraped_headlines: List[str]
    retrieved_news: List[str]
    retrieval_scores: List[float]
    analysis_summary: dict
    final_response: str

# --- Node Functions ---

# --- NEW NODE: Intent Classification Router ---
def classify_intent(state: GraphState):
    """
    Node 1 (New Entry Point): Classifies the user's query to decide which path to take.
    """
    print("---Entering Node: classify_intent---")
    user_query = state["user_query"]
    
    # We use a simple, fast LLM call to classify the intent
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    prompt = ChatPromptTemplate.from_template(
        """Your task is to classify the user's query into one of two categories: 'financial_query' or 'general_conversation'.
        - 'financial_query': For questions about stocks, markets, portfolios, earnings, financial news, or specific companies.
        - 'general_conversation': For greetings, questions about your capabilities (e.g., "how can you help?"), or any non-financial topic.
        
        User Query: "{query}"
        
        Return only the category name as a single string."""
    )
    chain = prompt | llm
    intent = chain.invoke({"query": user_query}).content.strip()
    
    print(f"Intent classified as: {intent}")
    return {"intent_type": intent}

# --- NEW NODE: Handles general non-financial questions ---
def handle_general_conversation(state: GraphState):
    """Node 2a: Handles general conversation by bypassing the RAG pipeline."""
    print("---Entering Node: handle_general_conversation (General Path)---")
    user_query = state["user_query"]
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful and friendly AI financial assistant. Answer the user's general question directly and conversationally.
        
        User's question: "{query}" """
    )
    chain = prompt | llm
    response = chain.invoke({"query": user_query}).content
    
    return {"final_response": response}

# --- Nodes from our previous financial workflow ---

def load_data_and_scrape(state: GraphState):
    """Node 2b: Loads portfolio and scrapes news (Financial Path)"""
    print("---Entering Node: load_data_and_scrape (Financial Path)---")
    # (This function's internal code is unchanged)
    with open(PORTFOLIO_CONFIG_PATH, 'r') as f:
        portfolio_data = json.load(f).get("portfolio", {})
    try:
        with open(DAILY_LOG_PATH, 'r') as f:
            previous_portfolio_data = json.load(f).get("portfolio", {})
    except FileNotFoundError:
        previous_portfolio_data = {}
    scraped_headlines = scraper_agent.get_earnings_surprises(portfolio=portfolio_data)
    return {"portfolio_data": portfolio_data, "previous_portfolio_data": previous_portfolio_data, "scraped_headlines": scraped_headlines}

def retrieve_relevant_news(state: GraphState):
    """Node 2: Retrieves news and now prints debug information."""
    print("---Entering Node: retrieve_relevant_news---")
    user_query = state["user_query"]
    scraped_headlines = state["scraped_headlines"]

    # ADDED FOR DEBUGGING 
    print(f"Found {len(scraped_headlines)} headlines to search through.")
    if scraped_headlines:
        print("First 5 headlines:", scraped_headlines[:5])


    if not scraped_headlines:
        return {"retrieved_news": [], "retrieval_scores": []}

    retriever_agent.create_and_store_embeddings(scraped_headlines)
    retrieval_results = retriever_agent.retrieve_top_k(user_query, k=5)

    # ADDED FOR DEBUGGING
    print(f"Retrieved {len(retrieval_results['documents'])} documents.")
    if retrieval_results['documents']:
        print("Top result:", retrieval_results['documents'][0])
        print("Top result score:", retrieval_results['scores'][0])
  

    return {
        "retrieved_news": retrieval_results["documents"],
        "retrieval_scores": retrieval_results["scores"]
    }

def run_analysis(state: GraphState):
    print("---Entering Node: run_analysis---")
    # (This function's internal code is unchanged)
    analysis_summary = analysis_agent.analyze_portfolio_risk(state["portfolio_data"], state["previous_portfolio_data"], state["scraped_headlines"])
    return {"analysis_summary": analysis_summary}

def generate_final_response(state: GraphState):
    print("---Entering Node: generate_final_response---")
    # (This function's internal code is unchanged)
    final_summary = llm_agent.generate_summary(state)
    return {"final_response": final_summary}

def generate_clarification_response(state: GraphState):
    print("---Entering Node: generate_clarification_response---")
    # (This function's internal code is unchanged)
    clarification_message = "I couldn't find any specific information related to your query in the recent news. Could you please try rephrasing your question?"
    return {"final_response": clarification_message}

def save_daily_log(state: GraphState):
    print("---Entering Node: save_daily_log---")
    # (This function's internal code is unchanged)
    with open(DAILY_LOG_PATH, 'w') as f: json.dump({"portfolio": state["portfolio_data"]}, f, indent=2)
    return {}



def route_based_on_intent(state: GraphState):
    """New primary router. Decides between the financial path and general chat."""
    print("---Routing based on intent...---")
    intent_type = state.get("intent_type", "")
    if "financial_query" in intent_type:
        return "continue_financial_workflow"
    else:
        return "handle_general_conversation"

def should_generate_response_or_clarify(state: GraphState):
    """Secondary check for retrieval confidence within the financial path."""
    print("---Checking retrieval confidence...---")
    scores = state.get("retrieval_scores", [])
    if not scores or scores[0] > CONFIDENCE_THRESHOLD:
        return "generate_clarification"
    else:
        return "continue_to_analysis"

# --- Assemble the NEW Graph ---

workflow = StateGraph(GraphState)

# Add all nodes
workflow.add_node("classify_intent", classify_intent)
workflow.add_node("handle_general_conversation", handle_general_conversation)
workflow.add_node("load_and_scrape", load_data_and_scrape)
workflow.add_node("retrieve_news", retrieve_relevant_news)
workflow.add_node("analyze_data", run_analysis)
workflow.add_node("generate_response", generate_final_response)
workflow.add_node("clarify_question", generate_clarification_response)
workflow.add_node("save_log", save_daily_log)

# Set the new entry point
workflow.set_entry_point("classify_intent")

# Define the new primary conditional routing
workflow.add_conditional_edges(
    "classify_intent",
    route_based_on_intent,
    {
        "continue_financial_workflow": "load_and_scrape",
        "handle_general_conversation": "handle_general_conversation"
    }
)

# Define edges for the financial path
workflow.add_edge("load_and_scrape", "retrieve_news")
workflow.add_conditional_edges(
    "retrieve_news",
    should_generate_response_or_clarify,
    {
        "continue_to_analysis": "analyze_data",
        "generate_clarification": "clarify_question"
    }
)
workflow.add_edge("analyze_data", "generate_response")
workflow.add_edge("generate_response", "save_log")

# Define end points for all paths
workflow.add_edge("save_log", END)
workflow.add_edge("clarify_question", END)
workflow.add_edge("handle_general_conversation", END)

app = workflow.compile()