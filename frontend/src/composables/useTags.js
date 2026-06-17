import { useNamedResources } from "@/composables/useNamedResources";

export function useTags() {
  return useNamedResources("/tags", { updateMethod: "PATCH" });
}
