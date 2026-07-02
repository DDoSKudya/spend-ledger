import { useNamedResources } from "@/composables/useNamedResources";

export function useCategories() {
  return useNamedResources("/categories", { updateMethod: "PUT" });
}
