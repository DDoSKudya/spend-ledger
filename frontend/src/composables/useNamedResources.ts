import { ref } from "vue";

import { api } from "@/api/client";
import type { NamedResource } from "@/types/models";

type UpdateMethod = "PUT" | "PATCH";

interface UseNamedResourcesOptions {
  updateMethod?: UpdateMethod;
}

export function useNamedResources(basePath: string, { updateMethod = "PUT" }: UseNamedResourcesOptions = {}) {
  const items = ref<NamedResource[]>([]);
  const loading = ref(false);

  async function load(): Promise<void> {
    loading.value = true;
    try {
      items.value = await api<NamedResource[]>(basePath);
    } finally {
      loading.value = false;
    }
  }

  async function create(name: string): Promise<void> {
    await api(basePath, { method: "POST", body: { name } });
    await load();
  }

  async function update(id: string, name: string): Promise<void> {
    await api(`${basePath}/${id}`, { method: updateMethod, body: { name } });
    await load();
  }

  async function remove(id: string): Promise<void> {
    await api(`${basePath}/${id}`, { method: "DELETE" });
    await load();
  }

  return { items, loading, load, create, update, remove };
}
