import { ref } from "vue";

import { api } from "@/api/client";

export function useNamedResources(basePath, { updateMethod = "PUT" } = {}) {
  const items = ref([]);
  const loading = ref(false);

  async function load() {
    loading.value = true;
    try {
      items.value = await api(basePath);
    } finally {
      loading.value = false;
    }
  }

  async function create(name) {
    await api(basePath, { method: "POST", body: { name } });
    await load();
  }

  async function update(id, name) {
    await api(`${basePath}/${id}`, { method: updateMethod, body: { name } });
    await load();
  }

  async function remove(id) {
    await api(`${basePath}/${id}`, { method: "DELETE" });
    await load();
  }

  return { items, loading, load, create, update, remove };
}
