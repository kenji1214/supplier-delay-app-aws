import { useNavigate } from "react-router-dom";
import type { Backorder } from "../types";

type Props = {
  rows: Backorder[];
};

export default function BackorderTable({ rows }: Props) {
  const navigate = useNavigate();

  if (!rows.length) {
    return <div className="empty-state">No backorders match the current filters.</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Supplier</th>
            <th>Plant</th>
            <th>Planner Code</th>
            <th>Part Number</th>
            <th>PO Number</th>
            <th>Due Date</th>
            <th>Open Qty</th>
            <th>Backorder Days</th>
            <th>Status</th>
            <th>Latest Comment</th>
            <th>Owner</th>
            <th>Action Due Date</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.shipment_key} onClick={() => navigate(`/backorders/${encodeURIComponent(row.shipment_key)}`)}>
              <td>
                <strong>{row.supplier_name}</strong>
                <span>{row.supplier_code}</span>
              </td>
              <td>{row.plant_code}</td>
              <td>{row.planner_code || "-"}</td>
              <td>{row.part_number}</td>
              <td>{row.po_number}</td>
              <td>{row.due_date || "-"}</td>
              <td>{row.open_qty.toLocaleString()}</td>
              <td>
                <span className={row.backorder_days >= 14 ? "badge danger" : "badge"}>{row.backorder_days}</span>
              </td>
              <td>{row.backorder_status}</td>
              <td className="comment-cell">{row.action_summary.latest_comment_preview || "-"}</td>
              <td>{row.action_summary.latest_action_owner || "-"}</td>
              <td>{row.action_summary.latest_due_date || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
