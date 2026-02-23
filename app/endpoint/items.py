from fastapi import APIRouter, HTTPException
from app.schema import Item

router = APIRouter()


_DB: dict[int, Item] = {}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    item = _DB.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items", response_model=Item, status_code=201)
def create_item(item: Item):
    if item.id in _DB:
        raise HTTPException(status_code=400, detail="Item already exists")
    _DB[item.id] = item
    return item
