import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import User as UserSchema, Request as RequestSchema

app = FastAPI(title="Blood Donor Nepal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize_doc(doc: dict) -> dict:
    d = doc.copy()
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    # Convert datetime to isoformat if present
    for k, v in list(d.items()):
        try:
            # hasattr for isoformat
            if hasattr(v, "isoformat"):
                d[k] = v.isoformat()
        except Exception:
            pass
    return d


@app.get("/")
def read_root():
    return {"message": "Blood Donor Nepal API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# ---------------- API: Donors (Users) ----------------
@app.post("/api/donors")
def create_donor(user: UserSchema):
    try:
        # Ensure defaults
        data = user.model_dump()
        data.setdefault("role", "Donor")
        data.setdefault("verified", False)
        inserted_id = create_document("user", data)
        return {"id": inserted_id, "message": "Donor registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/donors")
def list_donors(blood_group: Optional[str] = None, city: Optional[str] = None, limit: Optional[int] = 50):
    try:
        filter_obj = {}
        if blood_group:
            filter_obj["blood_group"] = blood_group
        if city:
            # Simple case-insensitive match for city
            filter_obj["city"] = {"$regex": f"^{city}$", "$options": "i"}
        docs = get_documents("user", filter_obj, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- API: Requests ----------------
@app.post("/api/requests")
def create_request(req: RequestSchema):
    try:
        data = req.model_dump()
        data.setdefault("status", "Pending")
        inserted_id = create_document("request", data)
        return {"id": inserted_id, "message": "Blood request submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/requests")
def list_requests(limit: Optional[int] = 50):
    try:
        docs = get_documents("request", {}, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- API: Search Donors by criteria ----------------
@app.get("/api/search/donors")
def search_donors(blood_group: str, city: str, limit: Optional[int] = 50):
    try:
        if not blood_group or not city:
            raise HTTPException(status_code=400, detail="blood_group and city are required")
        filter_obj = {
            "blood_group": blood_group,
            "city": {"$regex": f"^{city}$", "$options": "i"},
        }
        docs = get_documents("user", filter_obj, limit)
        donors = [
            {
                "id": str(d.get("_id")),
                "full_name": d.get("full_name"),
                "blood_group": d.get("blood_group"),
                "phone": d.get("phone"),
                "city": d.get("city"),
            }
            for d in docs
        ]
        return donors
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
