export interface User {
  id?: string;
  email: string;
}

export interface NamedResource {
  id: string;
  name: string;
}

export type Category = NamedResource;
export type Tag = NamedResource;

export interface Expense {
  id: string;
  amount: string | number;
  expense_date: string;
  description?: string | null;
  category: Category;
  tags: Tag[];
}

export interface ExpenseFilters {
  page: number;
  size: number;
  sort: string;
  category_id: string;
  tag_ids: string[];
  date_from: string;
  date_to: string;
  search: string;
}

export interface PaginatedExpenses {
  items: Expense[];
  total: number;
  pages: number;
  page: number;
  size: number;
}

export interface ExpensePayload {
  amount: string | number;
  category_id: string;
  description: string | null;
  expense_date: string;
  tag_ids: string[];
}

export interface MonthlyReportRow {
  month: number;
  total: string | number;
  count: number;
}

export interface MonthlyReport {
  year?: number;
  grand_total: string | number;
  months: MonthlyReportRow[];
}

export type ExportStatus = "pending" | "processing" | "done" | "failed";

export interface ExportJob {
  job_id: string;
  status: ExportStatus;
  download_url?: string;
  error_message?: string;
  format?: string;
}

export interface ExportFilters {
  category_id: string | null;
  tag_ids: string[];
  date_from: string | null;
  date_to: string | null;
  search: string | null;
}

export interface SelectOption {
  value: string;
  label: string;
}

export type AlertVariant = "error" | "success";
export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
export type ToastVariant = "success" | "error";
