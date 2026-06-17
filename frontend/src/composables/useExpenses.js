import { ref } from "vue";

import { api } from "@/api/client";

const defaultFilters = () => ({
  page: 1,
  size: 20,
  sort: "expense_date:desc",
  category_id: "",
  tag_ids: [],
  date_from: "",
  date_to: "",
  search: "",
});

function buildQuery(filters) {
  const params = new URLSearchParams();
  params.set("page", String(filters.page));
  params.set("size", String(filters.size));
  params.set("sort", filters.sort);

  if (filters.category_id) {
    params.set("category_id", filters.category_id);
  }
  if (filters.date_from) {
    params.set("date_from", filters.date_from);
  }
  if (filters.date_to) {
    params.set("date_to", filters.date_to);
  }
  if (filters.search) {
    params.set("search", filters.search);
  }
  for (const tagId of filters.tag_ids) {
    params.append("tag_ids", tagId);
  }

  return params.toString();
}

export function useExpenses() {
  const items = ref([]);
  const total = ref(0);
  const pages = ref(0);
  const loading = ref(false);
  const filters = ref(defaultFilters());

  async function load() {
    loading.value = true;
    try {
      const data = await api(`/expenses?${buildQuery(filters.value)}`);
      items.value = data.items;
      total.value = data.total;
      pages.value = data.pages;
      filters.value.page = data.page;
      filters.value.size = data.size;
    } finally {
      loading.value = false;
    }
  }

  async function create(payload) {
    await api("/expenses", { method: "POST", body: payload });
    await load();
  }

  async function update(id, payload) {
    await api(`/expenses/${id}`, { method: "PUT", body: payload });
    await load();
  }

  async function remove(id) {
    await api(`/expenses/${id}`, { method: "DELETE" });
    await load();
  }

  function setPage(page) {
    filters.value.page = page;
    return load();
  }

  function resetFilters() {
    filters.value = defaultFilters();
    return load();
  }

  return {
    items,
    total,
    pages,
    loading,
    filters,
    load,
    create,
    update,
    remove,
    setPage,
    resetFilters,
  };
}
