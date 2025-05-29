from fastapi import FastAPI
from pydantic import BaseModel

# Import the compiled LangGraph app from our new graph.py file
from .graph import app as financial_assistant_graph


app = FastAPI(
    title="LangGraph Financial Assistant API",
    description="An API powered by LangGraph to orchestrate a multi-agent workflow.",
    version="3.0.0"
)

# API Models
class QueryRequest(BaseModel):
    query: str

# API Endpoints
@app.post("/query", summary="Get a dynamic market brief using the agent graph")
async def get_market_brief(request: QueryRequest):
    """
    This endpoint takes a user's query and runs it through the complete
    LangGraph-powered agent workflow.
    """
    user_query = request.query
    print(f"Received query, invoking agent graph: {user_query}")
    
    # The input to the graph must be a dictionary with keys matching the GraphState
    inputs = {"user_query": user_query}
    
    # Invoke the graph and stream the results
    # .invoke() runs the graph to completion
    final_state = financial_assistant_graph.invoke(inputs)

    # The final response is in the 'final_response' key of the state
    response_text = final_state.get("final_response", "Error: No final response was generated.")
    
    print("--- Graph Execution Complete ---")
    
    # We return the final response and the full state for debugging/context
    return {"response": response_text, "context_used": final_state}

@app.get("/", summary="Root endpoint for health check")
def read_root():
    return {"status": "API is running."}