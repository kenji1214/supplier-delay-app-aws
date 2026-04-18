import { FormEvent, useEffect, useState } from "react";
import type { Comment, CommentPayload } from "../types";

type Props = {
  mode: "add" | "edit";
  plannerCode: string | null;
  comment?: Comment | null;
  onClose: () => void;
  onSubmit: (payload: CommentPayload) => Promise<void>;
};

export default function CommentFormModal({ mode, plannerCode, comment, onClose, onSubmit }: Props) {
  const [form, setForm] = useState<CommentPayload>({
    planner_code: plannerCode,
    comment_text: "",
    action_status: "Open",
    action_owner: "",
    due_date: ""
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (comment) {
      setForm({
        planner_code: comment.planner_code || plannerCode,
        comment_text: comment.comment_text,
        action_status: comment.action_status,
        action_owner: comment.action_owner || "",
        due_date: comment.due_date || ""
      });
    } else {
      setForm((current) => ({ ...current, planner_code: plannerCode }));
    }
  }, [comment, plannerCode]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      await onSubmit(form);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <form className="modal" onSubmit={submit}>
        <div className="modal-head">
          <h2>{mode === "add" ? "Add Comment" : "Edit Comment"}</h2>
          <button type="button" className="icon-button" onClick={onClose}>
            x
          </button>
        </div>
        <div className="field">
          <label>Planner Code</label>
          <input
            value={form.planner_code || ""}
            onChange={(e) => setForm({ ...form, planner_code: e.target.value })}
            required
          />
        </div>
        <div className="field">
          <label>Comment</label>
          <textarea
            value={form.comment_text}
            onChange={(e) => setForm({ ...form, comment_text: e.target.value })}
            required
            rows={5}
          />
        </div>
        <div className="modal-grid">
          <div className="field">
            <label>Status</label>
            <select value={form.action_status} onChange={(e) => setForm({ ...form, action_status: e.target.value })}>
              <option>Open</option>
              <option>Supplier contacted</option>
              <option>Expedite requested</option>
              <option>Waiting supplier</option>
              <option>Resolved</option>
            </select>
          </div>
          <div className="field">
            <label>Owner</label>
            <input
              value={form.action_owner || ""}
              onChange={(e) => setForm({ ...form, action_owner: e.target.value })}
            />
          </div>
          <div className="field">
            <label>Due Date</label>
            <input type="date" value={form.due_date || ""} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
          </div>
        </div>
        <div className="modal-actions">
          <button type="button" className="secondary-button" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="primary-button" disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </form>
    </div>
  );
}
