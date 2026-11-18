import json, os, re, sqlite3, logging
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher
from urllib.parse import quote_plus
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL", "")
SEED = BASE / "seed_tickets.json"
log = logging.getLogger("campusflow")
app = FastAPI(title="CampusFlow", version="2.0.0")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE / "templates"))
PROVIDERS = {
 "Gemini":{"env":"GEMINI_API_KEY","models":["gemini-3.8-flash","gemini-flash-latest"],"default":"gemini-3.8-flash"},
 "Groq":{"env":"GROQ_API_KEY","models":["openai/gpt-oss-120b","openai/gpt-oss-20b","qwen/qwen3.8-27b"],"default":"openai/gpt-oss-120b"},
 "OpenRouter":{"env":"OPENROUTER_API_KEY","models":["openai/gpt-oss-120b","anthropic/claude-sonnet-4-6","google/gemini-3.8-flash"],"default":"openai/gpt-oss-120b"}
}
class TicketIn(BaseModel):
 title:str=Field(min_length=3,max_length=140)
 description:str=Field(min_length=8,max_length=5000)
 category:str="Unclassified"
 priority:str="Unassigned"
 department:str="Unassigned"
class TicketPatch(BaseModel):
 status:str|None=None
 assigned_to:str|None=None
 department:str|None=None
 category:str|None=None
 priority:str|None=None
class AIIn(BaseModel):
 prompt:str=Field(min_length=3,max_length=5000)
 provider:str="Gemini"
 model:str|None=None
class ChatIn(BaseModel):
 message:str=Field(min_length=1,max_length=3000)
 provider:str="Gemini"
 model:str|None=None
 history:list[dict]=[]

def db():
 if DATABASE_URL:
  import psycopg
  return psycopg.connect(DATABASE_URL)
 if os.getenv("VERCEL"):
  raise HTTPException(503,"Persistent storage is not connected. Add DATABASE_URL to the Vercel project before using CampusFlow.")
 c=sqlite3.connect(BASE/"campusflow.local.db"); c.row_factory=sqlite3.Row; return c
def execute(c,q,p=()):
 if DATABASE_URL:q=q.replace("?","%s")
 cur=c.cursor();cur.execute(q,p);return cur
def init_db():
 try:c=db()
 except HTTPException:return
 try:
  execute(c,"CREATE TABLE IF NOT EXISTS tickets (id TEXT PRIMARY KEY,title TEXT NOT NULL,description TEXT NOT NULL,category TEXT DEFAULT 'Unclassified',priority TEXT DEFAULT 'Unassigned',department TEXT DEFAULT 'Unassigned',reason TEXT,status TEXT DEFAULT 'Open',assigned_to TEXT,assigned_at TEXT,created_at TEXT NOT NULL)")
  c.commit()
  count=execute(c,"SELECT COUNT(*) FROM tickets").fetchone()[0]
  if count==0 and SEED.exists():
   for t in json.loads(SEED.read_text()):
    execute(c,"INSERT INTO tickets (id,title,description,category,priority,department,reason,status,assigned_to,assigned_at,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(t["id"],t.get("title","Untitled"),t.get("description",""),t.get("category","Unclassified"),t.get("priority","Unassigned"),t.get("department","Unassigned"),t.get("reason",""),t.get("status","Open"),t.get("assigned_to"),t.get("assigned_at"),t.get("created_at") or datetime.now(timezone.utc).isoformat()))
   c.commit()
 finally:c.close()
@app.on_event("startup")
def startup():init_db()
KEYS=["id","title","description","category","priority","department","reason","status","assigned_to","assigned_at","created_at"]
def asdict(row):return dict(row) if isinstance(row,sqlite3.Row) else dict(zip(KEYS,row))
def tickets():
 c=db()
 try:return [asdict(x) for x in execute(c,"SELECT * FROM tickets ORDER BY created_at DESC").fetchall()]
 finally:c.close()
@app.get("/",response_class=HTMLResponse)
def home(request:Request):return templates.TemplateResponse("index.html",{"request":request})
@app.get("/api/health")
def health():return {"status":"ok","version":"2.0.0","database":"connected" if DATABASE_URL else "local-only"}
@app.get("/api/tickets")
def list_tickets():return {"tickets":tickets()}
@app.post("/api/tickets")
def create_ticket(t:TicketIn):
 old=tickets();nums=[int(m.group(1)) for x in old if (m:=re.search(r"(\d+)$",x["id"]))]
 tid=f"TKT-{max(nums,default=0)+1:03d}";similar=[]
 for x in old:
  score=SequenceMatcher(None,(t.title+" "+t.description).lower(),(x["title"]+" "+x["description"]).lower()).ratio()
  if score>=.42:similar.append({"id":x["id"],"title":x["title"],"similarity":round(score*100,1)})
 c=db()
 try:
  execute(c,"INSERT INTO tickets (id,title,description,category,priority,department,reason,status,created_at) VALUES (?,?,?,?,?,?,?,?,?)",(tid,t.title.strip(),t.description.strip(),t.category,t.priority,t.department,"Awaiting AI analysis" if t.category=="Unclassified" else "","Open",datetime.now(timezone.utc).isoformat()));c.commit()
 finally:c.close()
 return {"ticket":next(x for x in tickets() if x["id"]==tid),"possible_duplicates":similar}
@app.patch("/api/tickets/{tid}")
def patch_ticket(tid:str,p:TicketPatch):
 changes=p.model_dump(exclude_unset=True)
 if not changes:raise HTTPException(400,"No changes supplied.")
 if "status" in changes and changes["status"] not in {"Open","In Progress","Resolved","Closed"}:raise HTTPException(400,"Invalid status.")
 if "assigned_to" in changes and changes["assigned_to"]:changes["assigned_at"]=datetime.now(timezone.utc).isoformat()
 c=db()
 try:
  if not execute(c,"SELECT id FROM tickets WHERE id=?",(tid,)).fetchone():raise HTTPException(404,"Ticket not found.")
  execute(c,"UPDATE tickets SET "+", ".join(k+"=?" for k in changes)+" WHERE id=?",(*changes.values(),tid));c.commit()
 finally:c.close()
 return {"ticket":next(x for x in tickets() if x["id"]==tid)}
@app.delete("/api/tickets/{tid}")
def remove_ticket(tid:str):
 c=db()
 try:
  cur=execute(c,"DELETE FROM tickets WHERE id=?",(tid,))
  if cur.rowcount==0:raise HTTPException(404,"Ticket not found.")
  c.commit()
 finally:c.close()
 return {"deleted":tid}
@app.get("/api/reports")
def reports():
 ts=tickets(); total=len(ts);resolved=sum(t["status"]=="Resolved" for t in ts)
 def count(key):
  out={}
  for t in ts:
   v=t.get(key) or "Unassigned";out[v]=out.get(v,0)+1
  return out
 departments=count("department");dr={}
 for d,n in departments.items():
  done=sum(t["department"]==d and t["status"]=="Resolved" for t in ts);dr[d]=round(done/n*100,1)
 return {"total":total,"resolved":resolved,"outstanding":total-resolved,"resolution_rate":round(resolved/total*100,1) if total else 0,"categories":count("category"),"priorities":count("priority"),"departments":departments,"department_resolution":dr}
def ai(provider,model,prompt,temp=.4):
 if provider not in PROVIDERS:raise HTTPException(400,"Unsupported provider.")
 cfg=PROVIDERS[provider];model=model if model in cfg["models"] else cfg["default"];key=os.getenv(cfg["env"])
 if not key:raise HTTPException(503,provider+" API key is not configured in Vercel.")
 if provider=="Gemini":
  url=f"https://generativelanguage.googleapis.com/v1beta/models/{quote_plus(model)}:generateContent?key={quote_plus(key)}"
  r=requests.post(url,json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":temp,"maxOutputTokens":1800}},timeout=75);data=r.json()
  answer="".join(p.get("text","") for p in data.get("candidates",[{}])[0].get("content",{}).get("parts",[]))
 else:
  url="https://api.groq.com/openai/v1/chat/completions" if provider=="Groq" else "https://openrouter.ai/api/v1/chat/completions"
  headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"}
  if provider=="OpenRouter":headers.update({"HTTP-Referer":"https://vercel.com","X-Title":"CampusFlow"})
  r=requests.post(url,headers=headers,json={"model":model,"messages":[{"role":"user","content":prompt}],"temperature":temp,"max_tokens":1800},timeout=75);data=r.json()
  answer=data.get("choices",[{}])[0].get("message",{}).get("content","")
 if not r.ok:raise HTTPException(502,str(data.get("error",{}).get("message") or "AI provider request failed.")[:400])
 if not answer:raise HTTPException(502,"AI provider returned an empty response.")
 return answer.strip()
@app.get("/api/ai/providers")
def providers():return {"providers":[{"name":n,"models":v["models"],"default":v["default"],"configured":bool(os.getenv(v["env"]))} for n,v in PROVIDERS.items()]}
@app.post("/api/ai/analyze")
def analyze(p:AIIn):
 raw=ai(p.provider,p.model,"You are CampusFlow ticket intelligence. Return ONLY valid JSON with keys category, priority, department, reason. Category should be Network, Facilities, Academic, Security, Administration or Other. Priority must be Low, Medium, High or Critical. Give a short reason. Issue: "+p.prompt,.2)
 try:return json.loads(raw[raw.find("{"):raw.rfind("}")+1])
 except Exception:raise HTTPException(502,"AI did not return valid ticket analysis.")
@app.post("/api/ai/suggest")
def suggest(p:AIIn):return {"suggestions":ai(p.provider,p.model,"Give safe, numbered troubleshooting steps for this campus issue. Include when to escalate and what details to include in a ticket. Issue: "+p.prompt,.45)}
@app.post("/api/ai/chat")
def chat(p:ChatIn):
 history="\n".join(str(x.get("role","user"))+": "+str(x.get("content",""))[:1000] for x in p.history[-8:])
 context="\n".join(f'{t["id"]}: {t["title"]} ({t["status"]}, {t["priority"]})' for t in tickets()[:25])
 return {"response":ai(p.provider,p.model,f"You are CampusFlow AI, a helpful campus support assistant. Answer practically and clearly. Do not invent ticket data. Recent conversation:\n{history}\nTicket context:\n{context}\nUser: {p.message}",.5)}
@app.get("/api/news")
def news():
 import xml.etree.ElementTree as ET
 searches=[("Library News","libraries OR librarians OR library services"),("Books and Publishing","books OR publishing OR authors"),("Reading and Literacy","reading OR literacy"),("Research and Digital Libraries","digital libraries OR academic libraries")]
 found=[];seen=set()
 for source,q in searches:
  try:
   url="https://news.google.com/rss/search?q="+quote_plus(q+" when:7d")+"&hl=en&gl=US&ceid=US:en";root=ET.fromstring(requests.get(url,timeout=8,headers={"User-Agent":"Mozilla/5.0 CampusFlow"}).content)
   for item in root.findall(".//item"):
    title=item.findtext("title") or "";link=item.findtext("link") or "";desc=item.findtext("description") or ""
    if not title or title.lower() in seen:continue
    seen.add(title.lower());match=re.search(r'<img[^>]+src=["\']([^"\']+)',desc,re.I)
    found.append({"title":title,"link":link,"description":re.sub("<[^>]+>"," ",desc)[:260],"source":source,"image":match.group(1) if match else None})
  except Exception as e:log.warning("News feed %s failed: %s",source,type(e).__name__)
 return {"articles":found[:18],"updated_at":datetime.now(timezone.utc).isoformat()}
@app.get("/api/gallery")
def gallery():
 folder=BASE/"static"/"campus"
 return {"images":["/static/campus/"+p.name for p in sorted(folder.iterdir()) if p.suffix.lower() in {".jpg",".jpeg",".png",".webp"}] if folder.exists() else []}
