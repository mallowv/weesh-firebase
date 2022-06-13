# pylint: disable=no-name-in-module
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-few-public-methods

from os import getenv
from typing import Optional
import random
import string
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate(json.loads(getenv("FIREBASE_CERT")))
firebase_admin.initialize_app(cred)

db = firestore.client()

app = FastAPI()

def rand_str(chars = string.ascii_uppercase + string.digits, length=10):
    """
    generate random string for id if user doesn't provide one
    """
    return ''.join(random.choice(chars) for _ in range(length))


class NewURL(BaseModel):
    id: Optional[str]
    url: str


app.mount("/static", StaticFiles(directory="ui"), name="ui")

@app.get("/")
async def root():
    """
    Serve the UI to user when user visits the root
    """
    with open("ui/index.html", encoding="utf8") as file:
        return HTMLResponse(content=file.read(), status_code=200)

@app.post("/shorten")
async def make_shortcut(url: NewURL, req: Request):
    """
    Make a new entry in the db for new url with optional id.
    :param req:
    :param url:
    :return: RedirectResponse | HTTPException
    """
    if url.id:
        doc_ref = db.collection('urls').document(url.id)

        doc = doc_ref.get()
        if doc.exists:
            raise HTTPException(
                status_code=409,
                detail=f"the url 'https://{req.url.hostname}/{url.id}' already exists"
            )
        shorten = {"url": url.url, "id": url.id}
    else:
        shorten = {"url": url.url, "id": rand_str()}

    doc_ref = db.collection("urls").document(shorten["id"])
    doc_ref.set(shorten)
    print(shorten)
    return {"url": f"https://{req.url.hostname}/{shorten['id']}", "id": shorten["id"]}

@app.get("/{url}")
async def read_item(url: str):
    """
    Fetch url from id, then redirect to the url.
    :param url:
    :return: RedirectResponse | HTTPException
    """
    doc_ref = db.collection('urls').document(url)

    doc = doc_ref.get()
    if doc.exists:
        return RedirectResponse(doc.to_dict()["url"])

    raise HTTPException(status_code=404, detail="That url does not exist")


@app.get("/{url}/raw")
async def read_item_raw(url: str):
    """
    Fetch url from id, then return a JSON object representing the
    url entry.
    :param url:
    :return: Dict | HTTPException
    """
    doc_ref = db.collection('urls').document(url)

    doc = doc_ref.get()
    if doc.exists:
        return {"id": doc.to_dict()["id"], "url": doc.to_dict()["url"]}

    raise HTTPException(status_code=404, detail="That url does not exist")
