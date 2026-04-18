import type { Backorder } from "../types";

export default function SummaryCard({ backorder }: { backorder: Backorder }) {
  const fields = [
    ["Supplier", `${backorder.supplier_name} (${backorder.supplier_code})`],
    ["Plant", backorder.plant_code],
    ["Planner Code", backorder.planner_code || "-"],
    ["Part Number", backorder.part_number],
    ["PO Number", backorder.po_number],
    ["Due Date", backorder.due_date || "-"],
    ["Ordered Qty", backorder.ordered_qty.toLocaleString()],
    ["Received Qty", backorder.received_qty.toLocaleString()],
    ["Open Qty", backorder.open_qty.toLocaleString()],
    ["Backorder Days", String(backorder.backorder_days)],
    ["Status", backorder.backorder_status]
  ];

  return (
    <section className="card summary-grid">
      {fields.map(([label, value]) => (
        <div key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </section>
  );
}
