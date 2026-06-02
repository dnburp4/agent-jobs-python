from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class Absender(BaseModel):
    name: str
    strasse: str
    ort: str
    telefon: str
    email: str


class Empfaenger(BaseModel):
    ansprechsartner: Optional[str] = None
    unternehmen: str
    strasse: Optional[str] = None
    ort: str


class AnschreibenSchema(BaseModel):
    absender: Absender
    empfaenger: Empfaenger
    datum: str
    betreff: str
    anrede: str
    absaetze: list[str]
    abschluss: str
    unterschrift: str
