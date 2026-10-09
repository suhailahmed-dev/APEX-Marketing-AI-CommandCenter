import os
import sys
import json
import uvicorn
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import BASE_DIR, DASHBOARD_PORT, MARKETING_MODULES, GEMINI_API_KEY
import database
import gemini_engine

# Windows console UTF-8 fix
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

app = FastAPI(
    title="APEX MARKETING AI // Agency & Owner Command Center",
    version="2.0.0"
)

# Enable CORS for local interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
STATIC_DIR = BASE_DIR / "static"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Request Models
class GenerateRequest(BaseModel):
    module_id: str
    params: Dict[str, Any]
    title: Optional[str] = None

class BrandProfileRequest(BaseModel):
    brand_name: str
    industry: str
    target_audience: str
    tone: str
    usp: str
    website: Optional[str] = ""

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>Dashboard HTML not found in static folder</h1>", status_code=404)
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))

@app.get("/api/modules")
async def get_modules():
    return JSONResponse(MARKETING_MODULES)

@app.get("/api/stats")
async def get_stats():
    stats = database.get_stats()
    return JSONResponse(stats)

@app.get("/api/history")
async def get_history(
    limit: int = 50,
    module_id: Optional[str] = None,
    search: Optional[str] = None,
    favorites_only: bool = False
):
    history = database.get_recent_work(
        limit=limit,
        module_id=module_id,
        search=search,
        favorites_only=favorites_only
    )
    return JSONResponse(history)

@app.get("/api/history/{work_id}")
async def get_work(work_id: int):
    work = database.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work item not found")
    return JSONResponse(work)

@app.delete("/api/history/{work_id}")
async def delete_work(work_id: int):
    success = database.delete_work(work_id)
    if not success:
        raise HTTPException(status_code=404, detail="Work item not found")
    return JSONResponse({"success": True, "message": "Work deleted successfully"})

@app.post("/api/history/{work_id}/favorite")
async def toggle_favorite(work_id: int):
    new_fav = database.toggle_favorite(work_id)
    return JSONResponse({"success": True, "is_favorite": new_fav})

@app.post("/api/generate")
async def generate_asset(req: GenerateRequest):
    module_id = req.module_id
    if module_id not in MARKETING_MODULES:
        raise HTTPException(status_code=400, detail=f"Invalid module ID: {module_id}")

    module_info = MARKETING_MODULES[module_id]
    
    # Auto-generate title if none provided
    title = req.title
    if not title:
        sample_param = next(iter(req.params.values()), "Asset") if req.params else "Asset"
        title = f"{module_info['name']}: {str(sample_param)[:40]}"

    # Execute AI Generation
    try:
        output_content = gemini_engine.generate_marketing_asset(module_id, req.params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save to history database
    new_id = database.save_work(
        module_id=module_id,
        module_name=module_info["name"],
        category=module_info["category"],
        title=title,
        input_params=req.params,
        output_content=output_content
    )

    return JSONResponse({
        "success": True,
        "id": new_id,
        "module_id": module_id,
        "module_name": module_info["name"],
        "category": module_info["category"],
        "title": title,
        "output_content": output_content,
        "created_at": "Just now"
    })

@app.get("/api/brand")
async def get_brand():
    brand = database.get_active_brand()
    return JSONResponse(brand)

@app.post("/api/brand")
async def save_brand(req: BrandProfileRequest):
    brand = database.save_brand_profile(
        brand_name=req.brand_name,
        industry=req.industry,
        target_audience=req.target_audience,
        tone=req.tone,
        usp=req.usp,
        website=req.website or ""
    )
    return JSONResponse({"success": True, "brand": brand})

@app.get("/api/export/{work_id}")
async def export_work(work_id: int, format: str = "markdown"):
    work = database.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work item not found")

    content = work["output_content"]
    title_clean = "".join(c for c in work["title"] if c.isalnum() or c in (" ", "_", "-")).rstrip()
    
    if format == "txt":
        filename = f"{title_clean}.txt"
        return PlainTextResponse(
            content=content,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    elif format == "csv":
        # Extract markdown table rows if any, or plain text
        filename = f"{title_clean}.csv"
        csv_rows = []
        for line in content.split("\n"):
            if line.startswith("|") and line.endswith("|"):
                # Markdown table row
                cols = [c.strip() for c in line.strip("|").split("|")]
                if not all(set(c) <= {"-", ":", " "} for c in cols): # skip separator
                    csv_rows.append('"' + '","'.join(cols) + '"')
        if csv_rows:
            csv_content = "\n".join(csv_rows)
        else:
            csv_content = f'"Title","Content"\n"{work["title"]}","{content.replace(chr(34), chr(34)+chr(34))}"'
            
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    else:
        # Default Markdown
        filename = f"{title_clean}.md"
        return PlainTextResponse(
            content=f"# {work['title']}\n*Category: {work['category']} | Date: {work['created_at']}*\n\n{content}",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

if __name__ == "__main__":
    print(f"\n=======================================================")
    print(f" 🚀 APEX MARKETING AI // Agency & Owner Command Center ")
    print(f" 🌐 Dashboard URL: http://localhost:{DASHBOARD_PORT}")
    print(f"=======================================================\n")
    uvicorn.run("dashboard:app", host="0.0.0.0", port=DASHBOARD_PORT, reload=False)
