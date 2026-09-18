"use client";
import { useState, useMemo } from "react";
import fundsData from "../data/funds.json";

type Fund = { id: any; name: string; category: string; stars: any; [k:string]: any };

export default function Page() {
  const rawData = fundsData as any;
  const funds = (Array.isArray(rawData)? rawData : Array.isArray(rawData?.funds)? rawData.funds : []) as Fund[];

  function getStarCount(s: any){ if(typeof s==="number") return s; if(typeof s==="string") return (s.match(/⭐/g)||[]).length; return s?.stars_count?? 0 }

  const [q,setQ]=useState(""); const [cat,setCat]=useState("all");
  const categories=useMemo(()=>Array.from(new Set(funds.map(f=>f.category).filter(Boolean))).sort() as string[],[funds]);
  const filtered=useMemo(()=>{let list=funds as Fund[]; if(cat!=="all") list=list.filter(f=>f.category===cat); if(q.trim()){const n=q.trim().toLowerCase(); list=list.filter(f=> f.name.toLowerCase().includes(n) || String(f.id).toLowerCase().includes(n));} return list;},[q,cat,funds]);

  return (<div dir="rtl" className="min-h-screen bg-[#FAF9F7] text-[#111] p-8"><h1 className="text-2xl font-bold mb-4">מציג {filtered.length} קרנות מתוך {funds.length}</h1><div className="flex gap-2 mb-4"><input value={q} onChange={e=>setQ(e.target.value)} placeholder="חיפוש" className="border p-2 rounded" /><select value={cat} onChange={e=>setCat(e.target.value)} className="border p-2 rounded"><option value="all">הכל</option>{categories.map(c=><option key={c} value={c}>{c}</option>)}</select></div><div className="grid gap-2">{filtered.slice(0,20).map(f=><div key={f.id} className="border p-3 rounded bg-white">{f.name} - {f.category} - {getStarCount(f.stars)} כוכבים</div>)}</div></div>)
}
