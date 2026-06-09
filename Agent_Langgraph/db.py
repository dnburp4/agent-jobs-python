from __future__ import annotations
import os
from supabase import create_client, Client

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_KEY"],
        )
    return _client


def sign_up(email: str, password: str) -> dict:
    res = get_client().auth.sign_up({"email": email, "password": password})
    return res


def sign_in(email: str, password: str) -> dict:
    res = get_client().auth.sign_in_with_password({"email": email, "password": password})
    return res


def sign_out() -> None:
    get_client().auth.sign_out()


def get_profile(user_id: str) -> dict | None:
    res = (
        get_client()
        .table("user_profiles")
        .select("cv_text, candidate_profile")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    return res.data if res else None


def save_profile(user_id: str, cv_text: str, candidate_profile: dict) -> None:
    get_client().table("user_profiles").upsert(
        {
            "user_id": user_id,
            "cv_text": cv_text,
            "candidate_profile": candidate_profile,
            "updated_at": "now()",
        }
    ).execute()


def save_bewerbung(user_id: str, job_title: str, company: str, anschreiben: dict) -> None:
    get_client().table("bewerbungen").insert(
        {
            "user_id": user_id,
            "job_title": job_title,
            "company": company,
            "anschreiben": anschreiben,
        }
    ).execute()


def get_bewerbungen(user_id: str) -> list[dict]:
    res = (
        get_client()
        .table("bewerbungen")
        .select("job_title, company, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    return res.data if res else []
