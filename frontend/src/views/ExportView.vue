<script setup>
import { ArrowDownTrayIcon } from "@heroicons/vue/24/outline";
import { onMounted, ref } from "vue";

import { getErrorMessage } from "@/api/errors";
import AppLayout from "@/components/layout/AppLayout.vue";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import { useCategories } from "@/composables/useCategories";
import { useExport } from "@/composables/useExport";
import { useTags } from "@/composables/useTags";
import { toggleItem } from "@/utils/selection";

const { items: categories, load: loadCategories } = useCategories();
const { items: tags, load: loadTags } = useTags();
const { job, loading, polling, start, download } = useExport();

const error = ref("");
const format = ref("csv");
const filters = ref({
  category_id: "",
  tag_ids: [],
  date_from: "",
  date_to: "",
  search: "",
});

const formatOptions = [
  { value: "csv", label: "CSV" },
  { value: "xlsx", label: "Excel (XLSX)" },
];

onMounted(async () => {
  try {
    await Promise.all([loadCategories(), loadTags()]);
  } catch (err) {
    error.value = getErrorMessage(err);
  }
});

function toggleTag(tagId) {
  filters.value.tag_ids = toggleItem(filters.value.tag_ids, tagId);
}

function buildFilters() {
  return {
    category_id: filters.value.category_id || null,
    tag_ids: filters.value.tag_ids,
    date_from: filters.value.date_from || null,
    date_to: filters.value.date_to || null,
    search: filters.value.search || null,
  };
}

async function handleStart() {
  error.value = "";
  try {
    await start({ format: format.value, filters: buildFilters() });
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

async function handleDownload() {
  if (!job.value) {
    return;
  }

  error.value = "";
  try {
    await download(job.value.download_url, job.value.job_id, job.value.format ?? format.value);
  } catch (err) {
    error.value = getErrorMessage(err, "Download failed");
  }
}
</script>

<template>
  <AppLayout>
    <h1 class="mb-6 text-2xl font-semibold">
      Export expenses
    </h1>

    <p class="mb-6 text-sm text-slate-600">
      Export expenses matching your filters. Add expenses on the Expenses page first if the list is empty.
    </p>

    <BaseAlert
      v-if="error"
      variant="error"
      class="mb-4"
    >
      {{ error }}
    </BaseAlert>

    <BaseCard class="mb-6">
      <div class="grid gap-4 sm:grid-cols-2">
        <BaseSelect
          v-model="format"
          label="Format"
          :options="formatOptions"
        />

        <BaseSelect
          v-model="filters.category_id"
          label="Category"
        >
          <option value="">
            All categories
          </option>
          <option
            v-for="category in categories"
            :key="category.id"
            :value="category.id"
          >
            {{ category.name }}
          </option>
        </BaseSelect>

        <BaseInput
          v-model="filters.date_from"
          label="From"
          type="date"
        />

        <BaseInput
          v-model="filters.date_to"
          label="To"
          type="date"
        />

        <BaseInput
          v-model="filters.search"
          label="Search"
          placeholder="Description"
          class="sm:col-span-2"
        />

        <div class="sm:col-span-2">
          <p class="mb-2 text-sm text-slate-700">
            Tags (any)
          </p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tag in tags"
              :key="tag.id"
              type="button"
              class="rounded-full border px-3 py-1 text-sm transition"
              :class="filters.tag_ids.includes(tag.id)
                ? 'border-slate-800 bg-slate-800 text-white'
                : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'"
              @click="toggleTag(tag.id)"
            >
              {{ tag.name }}
            </button>
          </div>
        </div>
      </div>

      <div class="mt-6">
        <BaseButton
          :disabled="loading || polling"
          @click="handleStart"
        >
          <ArrowDownTrayIcon class="size-4" />
          {{ loading ? "Starting..." : "Start export" }}
        </BaseButton>
      </div>
    </BaseCard>

    <BaseCard v-if="job">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm text-slate-600">
            Job ID
          </p>
          <p class="font-mono text-sm">
            {{ job.job_id }}
          </p>
        </div>

        <div class="flex items-center gap-3">
          <span
            class="rounded-full px-3 py-1 text-sm capitalize"
            :class="{
              'bg-amber-100 text-amber-800': job.status === 'pending' || job.status === 'processing',
              'bg-green-100 text-green-800': job.status === 'done',
              'bg-red-100 text-red-800': job.status === 'failed',
            }"
          >
            {{ job.status }}
          </span>

          <LoadingSpinner v-if="polling" />

          <BaseButton
            v-if="job.status === 'done'"
            @click="handleDownload"
          >
            <ArrowDownTrayIcon class="size-4" />
            Download
          </BaseButton>
        </div>
      </div>

      <BaseAlert
        v-if="job.status === 'failed'"
        variant="error"
        class="mt-4"
      >
        {{ job.error_message || "Export failed" }}
      </BaseAlert>
    </BaseCard>
  </AppLayout>
</template>
