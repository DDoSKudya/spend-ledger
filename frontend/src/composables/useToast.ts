import { ref } from "vue";

import type { ToastItem } from "@/types/ui";
import type { ToastVariant } from "@/types/models";

const toasts = ref<ToastItem[]>([]);
let nextId = 1;

function removeToast(id: number): void {
  toasts.value = toasts.value.filter((toast) => toast.id !== id);
}

export function useToast() {
  function show(message: string, variant: ToastVariant = "success", duration = 3200): void {
    const id = nextId++;
    toasts.value.push({ id, message, variant });

    window.setTimeout(() => {
      removeToast(id);
    }, duration);
  }

  return {
    toasts,
    show,
    remove: removeToast,
  };
}
