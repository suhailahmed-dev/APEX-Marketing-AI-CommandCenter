import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Work History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id TEXT NOT NULL,
            module_name TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            input_params TEXT,
            output_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_favorite INTEGER DEFAULT 0,
            status TEXT DEFAULT 'completed'
        )
    """)

    # Brand Profiles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brand_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL,
            industry TEXT,
            target_audience TEXT,
            tone TEXT,
            usp TEXT,
            website TEXT,
            is_active INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Seed default brand profile if none exists
    cursor.execute("SELECT COUNT(*) FROM brand_profiles")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO brand_profiles (brand_name, industry, target_audience, tone, usp, website, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            "Your Project / Brand Name",
            "General Business / E-Commerce / Agency",
            "Target Audience & Prospective Customers",
            "Professional, engaging, and high-converting",
            "Delivering exceptional quality and proven results",
            ""
        ))
        conn.commit()

    conn.close()

def save_work(module_id: str, module_name: str, category: str, title: str, input_params: dict, output_content: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO work_history (module_id, module_name, category, title, input_params, output_content, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        module_id,
        module_name,
        category,
        title,
        json.dumps(input_params, ensure_ascii=False),
        output_content,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_recent_work(limit: int = 50, module_id: Optional[str] = None, search: Optional[str] = None, favorites_only: bool = False) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM work_history WHERE 1=1"
    params = []

    if module_id and module_id != "all":
        query += " AND module_id = ?"
        params.append(module_id)

    if favorites_only:
        query += " AND is_favorite = 1"

    if search:
        query += " AND (title LIKE ? OR output_content LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    result = []
    for r in rows:
        item = dict(r)
        try:
            item["input_params"] = json.loads(item["input_params"]) if item["input_params"] else {}
        except Exception:
            item["input_params"] = {}
        result.append(item)

    conn.close()
    return result

def get_work_by_id(work_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM work_history WHERE id = ?", (work_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        item = dict(row)
        try:
            item["input_params"] = json.loads(item["input_params"]) if item["input_params"] else {}
        except Exception:
            item["input_params"] = {}
        return item
    return None

def delete_work(work_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM work_history WHERE id = ?", (work_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def toggle_favorite(work_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_favorite FROM work_history WHERE id = ?", (work_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return 0
    new_fav = 0 if row["is_favorite"] == 1 else 1
    cursor.execute("UPDATE work_history SET is_favorite = ? WHERE id = ?", (new_fav, work_id))
    conn.commit()
    conn.close()
    return new_fav

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM work_history")
    total_assets = cursor.fetchone()[0]

    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM work_history WHERE created_at LIKE ?", (f"{today_str}%",))
    today_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_history WHERE is_favorite = 1")
    favorites_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM work_history 
        GROUP BY category 
        ORDER BY count DESC
    """)
    category_counts = {row["category"]: row["count"] for row in cursor.fetchall()}

    cursor.execute("""
        SELECT module_name, COUNT(*) as count 
        FROM work_history 
        GROUP BY module_name 
        ORDER BY count DESC LIMIT 1
    """)
    top_module_row = cursor.fetchone()
    top_module = top_module_row["module_name"] if top_module_row else "None yet"

    conn.close()
    return {
        "total_assets": total_assets,
        "today_count": today_count,
        "favorites_count": favorites_count,
        "category_counts": category_counts,
        "top_module": top_module
    }

def get_active_brand() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM brand_profiles WHERE is_active = 1 ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "brand_name": "My Business Brand",
        "industry": "General Business",
        "target_audience": "Customers and clients",
        "tone": "Professional and Friendly",
        "usp": "Quality and satisfaction guaranteed",
        "website": ""
    }

def save_brand_profile(brand_name: str, industry: str, target_audience: str, tone: str, usp: str, website: str) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE brand_profiles SET is_active = 0")
    cursor.execute("""
        INSERT INTO brand_profiles (brand_name, industry, target_audience, tone, usp, website, is_active, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    """, (brand_name, industry, target_audience, tone, usp, website, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return get_active_brand()

# Initialize DB on import
init_db()
