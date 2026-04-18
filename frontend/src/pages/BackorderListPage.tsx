import { useEffect, useMemo, useState } from "react";
import { fetchBackorders, fetchPlannerCodes } from "../api/client";
import BackorderTable from "../components/BackorderTable";
import FilterBar from "../components/FilterBar";
import type { Backorder, BackorderFilters } from "../types";

const initialFilters: BackorderFilters = {
  supplier_code: "",
  plant_code: "",
  planner_codes: [],
  part_number: "",
  po_number: "",
  min_backorder_days: "",
  search: ""
};

export default function BackorderListPage() {
  const [filters, setFilters] = useState(initialFilters);
  const [rows, setRows] = useState<Backorder[]>([]);
  const [plannerCodes, setPlannerCodes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState(localStorage.getItem("currentUser") || "poc.planner");

  useEffect(() => {
    localStorage.setItem("currentUser", currentUser);
  }, [currentUser]);

  useEffect(() => {
    fetchPlannerCodes().then(setPlannerCodes).catch(() => setPlannerCodes([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const timeout = window.setTimeout(() => {
      fetchBackorders(filters)
        .then(setRows)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }, 180);
    return () => window.clearTimeout(timeout);
  }, [filters]);

  const sortedRows = useMemo(
    () => [...rows].sort((a, b) => b.backorder_days - a.backorder_days),
    [rows]
  );

  function exportCsv() {
    const headers = ["Supplier", "Plant", "Planner Code", "Part Number", "PO Number", "Due Date", "Open Qty", "Backorder Days", "Status"];
    const lines = sortedRows.map((row) =>
      [
        row.supplier_name,
        row.plant_code,
        row.planner_code || "",
        row.part_number,
        row.po_number,
        row.due_date || "",
        row.open_qty,
        row.backorder_days,
        row.backorder_status
      ]
        .map((value) => `"${String(value).replaceAll('"', '""')}"`)
        .join(",")
    );
    const blob = new Blob([[headers.join(","), ...lines].join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "supplier-backorders.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main className="page">
      <header className="topbar">
        <div>
          <p>Supply chain planning</p>
          <h1>Supplier Backorder Monitor</h1>
        </div>
        <label className="user-field">
          Current user
          <input value={currentUser} onChange={(e) => setCurrentUser(e.target.value)} />
        </label>
      </header>

      <FilterBar filters={filters} plannerCodes={plannerCodes} onChange={setFilters} onExport={exportCsv} />

      <section className="content-section">
        <div className="section-head">
          <h2>Backorders</h2>
          <span>{sortedRows.length} records</span>
        </div>
        {loading && <div className="loading">Loading backorders...</div>}
        {error && <div className="error-state">{error}</div>}
        {!loading && !error && <BackorderTable rows={sortedRows} />}
      </section>
    </main>
  );
}
