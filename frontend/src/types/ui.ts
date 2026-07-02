export interface ConfirmOptions {
  title?: string;
  message?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
}

export type ConfirmState = Required<ConfirmOptions>;

export interface ToastItem {
  id: number;
  message: string;
  variant: "success" | "error";
}
