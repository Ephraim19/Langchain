from fastapi import FastAPI, HTTPException, Path, Query, BackgroundTasks,Request
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from services.langchn import LangChainService, LangChainRAG
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Initialize FastAPI app and templates
app = FastAPI(
    title="Simple API",
    description="A simple FastAPI application with basic CRUD operations",
    version="0.1.0"
)

templates = Jinja2Templates(directory="templates")

#Langchain
@app.get("/langchain")
async def LangchainApi():
    """Endpoint to interact with LangChain service."""
    try:
        response = LangChainService()
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#RAG
@app.get("/langchain/rag")
async def LangchainRAGApi(url:str, question:str):
    try:
        response = LangChainRAG(url, question)
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Data model
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# In-memory database
items = {}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.get("/items/", response_model=List[Item])
async def read_items():
    """Get all items."""
    return list(items.values())

@app.get("/items/{item_id}", response_model=Item)
async def read_item(
    item_id: int = Path(..., title="The ID of the item to get", ge=0)
):
    """Get a specific item by ID."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    """Create a new item."""
    item_id = len(items)
    items[item_id] = item
    return item

@app.put("/items/{item_id}", response_model=Item)
async def update_item(
    item: Item,
    item_id: int = Path(..., title="The ID of the item to update", ge=0)
):
    """Update an existing item."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    items[item_id] = item
    return item

@app.delete("/items/{item_id}")
async def delete_item(
    item_id: int = Path(..., title="The ID of the item to delete", ge=0)
):
    """Delete an item."""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    del items[item_id]
    return {"message": "Item deleted successfully"}

@app.get("/items/search/", response_model=List[Item])
async def search_items(
    keyword: Optional[str] = Query(None, title="Keyword to search in item names"),
    max_price: Optional[float] = Query(None, title="Maximum price filter")
):
    """Search items by name keyword and/or maximum price."""
    results = list(items.values())
    
    if keyword:
        results = [item for item in results if keyword.lower() in item.name.lower()]
    
    if max_price is not None:
        results = [item for item in results if item.price <= max_price]
    
    return results

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)