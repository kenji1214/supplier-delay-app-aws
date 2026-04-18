export type ActionSummary = {
  latest_action_status: string | null;
  latest_action_owner: string | null;
  latest_due_date: string | null;
  latest_comment_preview: string | null;
  latest_planner_code: string | null;
  comment_count: number;
};

export type Backorder = {
  shipment_key: string;
  supplier_code: string;
  supplier_name: string;
  plant_code: string;
  planner_code: string | null;
  part_number: string;
  po_number: string;
  due_date: string | null;
  ordered_qty: number;
  received_qty: number;
  open_qty: number;
  is_backorder: boolean;
  backorder_days: number;
  backorder_status: string;
  action_summary: ActionSummary;
};

export type Comment = {
  id: number;
  shipment_key: string;
  supplier_code: string;
  supplier_name: string;
  plant_code: string;
  planner_code: string | null;
  part_number: string;
  po_number: string;
  comment_text: string;
  action_status: string;
  action_owner: string | null;
  due_date: string | null;
  created_by: string;
  created_at: string;
  updated_by: string | null;
  updated_at: string;
  is_deleted: boolean;
};

export type BackorderDetail = {
  backorder: Backorder;
  comments: Comment[];
};

export type CommentPayload = {
  planner_code?: string | null;
  comment_text: string;
  action_status: string;
  action_owner?: string | null;
  due_date?: string | null;
};

export type BackorderFilters = {
  supplier_code: string;
  plant_code: string;
  planner_codes: string[];
  part_number: string;
  po_number: string;
  min_backorder_days: string;
  search: string;
};
