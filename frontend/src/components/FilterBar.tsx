import type { BackorderFilters } from "../types";
import PlannerCodeMultiSelect from "./PlannerCodeMultiSelect";

type Props = {
  filters: BackorderFilters;
  plannerCodes: string[];
  onChange: (filters: BackorderFilters) => void;
  onExport: () => void;
};

export default function FilterBar({ filters, plannerCodes, onChange, onExport }: Props) {
  function setField(key: keyof BackorderFilters, value: string | string[]) {
    onChange({ ...filters, [key]: value });
  }

  return (
    <section className="filter-bar">
      <div className="field">
        <label>Supplier</label>
        <input value={filters.supplier_code} onChange={(e) => setField("supplier_code", e.target.value)} />
      </div>
      <div className="field">
        <label>Plant</label>
        <input value={filters.plant_code} onChange={(e) => setField("plant_code", e.target.value)} />
      </div>
      <PlannerCodeMultiSelect
        options={plannerCodes}
        selected={filters.planner_codes}
        onChange={(value) => setField("planner_codes", value)}
      />
      <div className="field">
        <label>Part Number</label>
        <input value={filters.part_number} onChange={(e) => setField("part_number", e.target.value)} />
      </div>
      <div className="field">
        <label>PO Number</label>
        <input value={filters.po_number} onChange={(e) => setField("po_number", e.target.value)} />
      </div>
      <div className="field small">
        <label>Min Days</label>
        <input
          type="number"
          min="0"
          value={filters.min_backorder_days}
          onChange={(e) => setField("min_backorder_days", e.target.value)}
        />
      </div>
      <div className="field wide">
        <label>Search</label>
        <input value={filters.search} onChange={(e) => setField("search", e.target.value)} />
      </div>
      <button className="secondary-button" type="button" onClick={onExport}>
        Export CSV
      </button>
    </section>
  );
}
