import type { Comment } from "../types";

type Props = {
  comments: Comment[];
  onEdit: (comment: Comment) => void;
  onDelete: (comment: Comment) => void;
};

export default function CommentTimeline({ comments, onEdit, onDelete }: Props) {
  if (!comments.length) {
    return <div className="empty-state compact">No comments yet.</div>;
  }

  return (
    <section className="timeline">
      {comments.map((comment) => {
        const edited = comment.updated_at !== comment.created_at;
        return (
          <article className="timeline-item" key={comment.id}>
            <div className="timeline-head">
              <div>
                <strong>{comment.action_status}</strong>
                <span>
                  {comment.action_owner || "Unassigned"} · {new Date(comment.created_at).toLocaleString()}
                </span>
              </div>
              <div className="row-actions">
                {edited && <span className="edited">edited</span>}
                <button type="button" className="link-button" onClick={() => onEdit(comment)}>
                  Edit
                </button>
                <button type="button" className="link-button danger-text" onClick={() => onDelete(comment)}>
                  Delete
                </button>
              </div>
            </div>
            <p>{comment.comment_text}</p>
            <dl>
              <div>
                <dt>Planner</dt>
                <dd>{comment.planner_code || "-"}</dd>
              </div>
              <div>
                <dt>Action due</dt>
                <dd>{comment.due_date || "-"}</dd>
              </div>
              <div>
                <dt>By</dt>
                <dd>{comment.created_by}</dd>
              </div>
            </dl>
          </article>
        );
      })}
    </section>
  );
}
