import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { createComment, deleteComment, fetchBackorderDetail, updateComment } from "../api/client";
import CommentFormModal from "../components/CommentFormModal";
import CommentTimeline from "../components/CommentTimeline";
import ConfirmDialog from "../components/ConfirmDialog";
import SummaryCard from "../components/SummaryCard";
import type { BackorderDetail, Comment, CommentPayload } from "../types";

export default function BackorderDetailPage() {
  const { shipmentKey = "" } = useParams();
  const navigate = useNavigate();
  const decodedKey = decodeURIComponent(shipmentKey);
  const [detail, setDetail] = useState<BackorderDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalMode, setModalMode] = useState<"add" | "edit" | null>(null);
  const [activeComment, setActiveComment] = useState<Comment | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Comment | null>(null);

  async function loadDetail() {
    setLoading(true);
    setError(null);
    try {
      setDetail(await fetchBackorderDetail(decodedKey));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load backorder");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDetail();
  }, [decodedKey]);

  async function handleAdd(payload: CommentPayload) {
    await createComment(decodedKey, payload);
    setModalMode(null);
    navigate("/");
  }

  async function handleEdit(payload: CommentPayload) {
    if (!activeComment) return;
    const updated = await updateComment(activeComment.id, payload);
    setDetail((current) => {
      if (!current) return current;
      return {
        ...current,
        comments: current.comments.map((comment) => (comment.id === updated.id ? updated : comment))
      };
    });
    await loadDetail();
    setActiveComment(null);
    setModalMode(null);
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    await deleteComment(deleteTarget.id);
    setDeleteTarget(null);
    await loadDetail();
  }

  if (loading) return <main className="page"><div className="loading">Loading detail...</div></main>;
  if (error || !detail) return <main className="page"><div className="error-state">{error || "Not found"}</div></main>;

  const summary = detail.backorder.action_summary;

  return (
    <main className="page">
      <header className="detail-header">
        <Link to="/" className="back-link">Back to list</Link>
        <div className="section-head">
          <div>
            <p>{detail.backorder.supplier_name}</p>
            <h1>{detail.backorder.part_number}</h1>
          </div>
          <button className="primary-button" type="button" onClick={() => setModalMode("add")}>
            Add Comment
          </button>
        </div>
      </header>

      <SummaryCard backorder={detail.backorder} />

      <section className="card action-summary">
        <div className="section-head">
          <h2>Action Summary</h2>
          <span>{summary.comment_count} comments</span>
        </div>
        <div className="summary-grid tight">
          <div><span>Status</span><strong>{summary.latest_action_status || "-"}</strong></div>
          <div><span>Owner</span><strong>{summary.latest_action_owner || "-"}</strong></div>
          <div><span>Planner Code</span><strong>{summary.latest_planner_code || detail.backorder.planner_code || "-"}</strong></div>
          <div><span>Due Date</span><strong>{summary.latest_due_date || "-"}</strong></div>
        </div>
        <p>{summary.latest_comment_preview || "No action comment captured yet."}</p>
      </section>

      <section className="content-section">
        <div className="section-head">
          <h2>Comment Timeline</h2>
          <span>Newest first</span>
        </div>
        <CommentTimeline
          comments={detail.comments}
          onEdit={(comment) => {
            setActiveComment(comment);
            setModalMode("edit");
          }}
          onDelete={setDeleteTarget}
        />
      </section>

      <section className="content-section attachment-placeholder">
        <h2>Attachments</h2>
        <p>Attachment tracking can be connected in a later version.</p>
      </section>

      {modalMode && (
        <CommentFormModal
          mode={modalMode}
          plannerCode={detail.backorder.planner_code}
          comment={modalMode === "edit" ? activeComment : null}
          onClose={() => {
            setModalMode(null);
            setActiveComment(null);
          }}
          onSubmit={modalMode === "add" ? handleAdd : handleEdit}
        />
      )}

      {deleteTarget && (
        <ConfirmDialog
          title="Delete comment"
          message="This comment will be hidden from the workflow history."
          onCancel={() => setDeleteTarget(null)}
          onConfirm={confirmDelete}
        />
      )}
    </main>
  );
}
