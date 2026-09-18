"use client";
import { useEffect, useState } from "react";

type Fund = {
  id: string;
  name: string;
  category: string;
  return_1y: number;
  return_3y: number;
  std_12: number;
  fee: number;
  score: number;
  stars: string;
  rank_in_category: number;
};

export default function Page() {
  const [funds, setFunds] = useState<Fund[]>([]);
  const [cat, setCat] = useState<string>("all");

  useEffect(() => {
    fetch("/funds.json")
      .then(r => r.json())
      .then(data => {
        // תומך גם במערך ישיר וגם ב- {funds: []}
        const list = Array.isArray(data) ? data : data.funds || [];
        setFunds(list);
      });
  }, []);

  const categories = Array.from(new Set(funds.map(f => f.category))).sort();
  const filtered = cat === "all" ? funds : funds.filter(f => f.category === cat);
  const sorted = [...filtered].sort((a,b) => a.rank_in_category - b.rank_in_category).slice(0, 300);

  if (funds.length === 0) return <div className="p-10">טוען { "2460 קרנות..." } </div>;

  return (
    <div dir="rtl" className="p-6 max-w-7xl mx-auto font-sans">
      <h1 className="text-3xl font-bold">FPRS - דירוג קטגוריאלי מתוקן ✅</h1>
      <p className="mt-2 text-gray-600">Z-Score מחושב בתוך כל קטגוריה בנפרד | סה"כ {funds.length} קרנות | תיקון: scoring.py עם groupby('category')</p>
      
      <select value={cat} onChange={e => setCat(e.target.value)} className="mt-6 border p-3 rounded w-full max-w-xl bg-white">
        <option value="all">כל הקטגוריות ({funds.length})</option>
        {categories.map(c => {
          const count = funds.filter(f => f.category === c).length;
          return <option key={c} value={c}>{c} ({count})</option>
        })}
      </select>

      <div className="mt-6 overflow-auto border rounded">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 sticky top-0">
            <tr>
              <th className="p-2 text-right"># בקטגוריה</th>
              <th className="p-2 text-right">שם הקרן</th>
              <th className="p-2">תשואה 1Y</th>
              <th className="p-2">ציון קטגוריאלי</th>
              <th className="p-2">כוכבים</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map(f => (
              <tr key={f.id} className="border-t hover:bg-gray-50">
                <td className="p-2 text-center font-bold">{f.rank_in_category}</td>
                <td className="p-2">{f.name}</td>
                <td className="p-2 text-center">{Number(f.return_1y || 0).toFixed(2)}%</td>
                <td className="p-2 text-center">{f.score}</td>
                <td className="p-2 text-center">{f.stars}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-xs text-gray-500">
        בדיקה: בכל קטגוריה אמורה להיות חלוקה של ~10% ⭐⭐⭐⭐⭐ , 22.5% ⭐⭐⭐⭐ , 35% ⭐⭐⭐ , 22.5% ⭐⭐ , 10% ⭐ - זה מוכיח שהדירוג קטגוריאלי ולא רוחבי.
      </div>
    </div>
  );
}
