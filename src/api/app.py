from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from ..graph.workflow import Workflow

"""Basic api using langserve"""

workflow_instance = Workflow()
compiled_graph = workflow_instance.main_graph 


app = FastAPI(
    title="YouTube Medical Fact-Checker API",
    version="1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

add_routes(
    app,
    compiled_graph,
    path="/agent", 
)

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)