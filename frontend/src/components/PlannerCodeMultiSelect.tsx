type Props = {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
};

export default function PlannerCodeMultiSelect({ options, selected, onChange }: Props) {
  const available = options.filter((option) => !selected.includes(option));

  function add(value: string) {
    if (value && !selected.includes(value)) onChange([...selected, value]);
  }

  return (
    <div className="multi-select">
      <label>Planner Code</label>
      <input
        list="planner-code-options"
        placeholder="Search planner"
        onChange={(event) => {
          add(event.target.value);
          event.target.value = "";
        }}
      />
      <datalist id="planner-code-options">
        {available.map((option) => (
          <option value={option} key={option} />
        ))}
      </datalist>
      {selected.length > 0 && (
        <div className="pills">
          {selected.map((planner) => (
            <button
              type="button"
              className="pill"
              key={planner}
              onClick={() => onChange(selected.filter((item) => item !== planner))}
            >
              {planner} x
            </button>
          ))}
          <button type="button" className="link-button" onClick={() => onChange([])}>
            Clear all
          </button>
        </div>
      )}
    </div>
  );
}
