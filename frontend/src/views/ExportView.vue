<script setup lang="ts">
import { ArrowDownTrayIcon } from "@heroicons/vue/24/outline";
import { onMounted, ref } from "vue";

import { getErrorMessage } from "@/api/errors";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";
import TagPill from "@/components/ui/TagPill.vue";
import { useCategories } from "@/composables/useCategories";
import { useExport } from "@/composables/useExport";
import { useTags } from "@/composables/useTags";
import { useToast } from "@/composables/useToast";
import type { ExportFilters, SelectOption } from "@/types/models";
import { toggleItem } from "@/utils/selection";

interface ExportFormFilters {
  category_id: string;
  tag_ids: string[];
  date_from: string;
  date_to: string;
  search: string;
}

const { items: categories, load: loadCategories } = useCategories();
const { items: tags, load: loadTags } = useTags();
const { job, loading, polling, start, download } = useExport();
const { show: showToast } = useToast();

const error = ref("");
const format = ref("csv");
const filters = ref<ExportFormFilters>({
  category_id: "",
  tag_ids: [],
  date_from: "",
  date_to: "",
  search: "",
});

const formatOptions: SelectOption[] = [
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

function toggleTag(tagId: string): void {
  filters.value.tag_ids = toggleItem(filters.value.tag_ids, tagId);
}

function buildFilters(): ExportFilters {
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
    showToast("Export started");
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}

async function handleDownload() {
  if (!job.value) return;
  error.value = "";
  try {
    await download(job.value.download_url, job.value.job_id, job.value.format ?? format.value);
    showToast("Download started");
  } catch (err) {
    error.value = getErrorMessage(err, "Download failed");
  }
}
</script>

<template>
  <div>
    <header class="view-head">
      <div>
        <h1 class="view-head__title">
          Export
        </h1>
        <p class="view-head__meta">
          Download filtered expenses
        </p>
      </div>
    </header>

    <Transition name="motion-alert">
      <BaseAlert
        v-if="error"
        variant="error"
        class="mb-4"
      >
        {{ error }}
      </BaseAlert>
    </Transition>

    <div class="split-layout split-layout--reverse">
      <BaseCard>
        <form
          class="stack"
          @submit.prevent="handleStart"
        >
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
          />

          <div>
            <span class="field-label">Tags</span>
            <div class="mt-2 flex flex-wrap gap-2">
              <TagPill
                v-for="tag in tags"
                :key="tag.id"
                :label="tag.name"
                :active="filters.tag_ids.includes(tag.id)"
                @toggle="toggleTag(tag.id)"
              />
            </div>
          </div>

          <BaseButton
            type="submit"
            :disabled="loading || polling"
          >
            <ArrowDownTrayIcon class="icon-md" />
            {{ loading ? "Starting..." : "Start export" }}
          </BaseButton>
        </form>
      </BaseCard>

      <BaseCard>
        <template v-if="job">
          <div class="stack stack--sm">
            <div>
              <span class="field-label">Status</span>
              <div class="mt-2 flex items-center gap-2">
                <StatusBadge :status="job.status" />
                <LoadingSpinner v-if="polling" />
              </div>
            </div>
            <div>
              <span class="field-label">Job ID</span>
              <p class="mono mt-1 text-sm">
                {{ job.job_id }}
              </p>
            </div>
            <BaseButton
              v-if="job.status === 'done'"
              @click="handleDownload"
            >
              <ArrowDownTrayIcon class="icon-md" />
              Download
            </BaseButton>
            <BaseAlert
              v-if="job.status === 'failed'"
              variant="error"
            >
              {{ job.error_message || "Export failed" }}
            </BaseAlert>
          </div>
        </template>
        <div
          v-else
          class="empty"
        >
          <p class="empty__title">
            No export yet
          </p>
          <p class="empty__text">
            Configure filters and start an export.
          </p>
        </div>
      </BaseCard>
    </div>
  </div>
</template>
