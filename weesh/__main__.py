# pylint: disable=no-name-in-module
# pylint: disable=missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-few-public-methods

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


@app.post("/")
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
        shorten = {"url": url.url, "id": uuid4().hex}

    doc_ref = db.collection("urls").document(shorten["id"])
    doc_ref.set(shorten)
    return {"url": f"https://{req.url.hostname}/{shorten['id']}"}
