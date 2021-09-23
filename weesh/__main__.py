from os import getenv
from typing import Optional
from uuid import uuid4
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate(json.loads(getenv("FIREBASE_CERT")))
firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()

class NewURL(BaseModel):
    id: Optional[str]
    url: str


@app.get("/{url}")
async def read_item(url: str):
    doc_ref = db.collection('urls').document(url)

    doc = doc_ref.get()
    if doc.exists:
        return RedirectResponse(doc.to_dict()["url"])
    
    raise HTTPException(status_code=404, detail="That url does not exist")

@app.get("/{url}/raw")
async def read_item(url: str):
    doc_ref = db.collection('urls').document(url)

    doc = doc_ref.get()
    if doc.exists:
        return {"id":doc.to_dict()["id"], "url":doc.to_dict()["url"]}
    
    raise HTTPException(status_code=404, detail="That url does not exist")

@app.post("/")
async def make_shortcut(url: NewURL, req: Request):
    doc_ref = db.collection('cities').document(url.id)

    doc = doc_ref.get()
    if url.id:
        if doc.exists:
            raise HTTPException(status_code=409, detail=f"the url 'https://{req.url.hostname}/{url.id}' already exists")
        shorten = {"url":url.url, "id":url.id}
    else:
        shorten = {"url":url.url, "id":uuid4().hex}
    
    doc_ref = db.collection("urls").document(shorten["id"])
    doc_ref.set(shorten)
    return {"url":f"https://{req.url.hostname}/{shorten['id']}"}
