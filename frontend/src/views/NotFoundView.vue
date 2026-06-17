<script setup>
import { RouterLink } from "vue-router";

import AppLayout from "@/components/layout/AppLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
</script>

<template>
  <AppLayout>
    <div class="flex justify-center py-16">
      <BaseCard class="max-w-md text-center">
        <p class="text-sm font-medium uppercase tracking-wide text-slate-500">
          404
        </p>
        <h1 class="mt-2 text-2xl font-semibold text-slate-900">
          Page not found
        </h1>
        <p class="mt-2 text-slate-600">
          The page you are looking for does not exist.
        </p>
        <RouterLink
          to="/expenses"
          class="mt-6 inline-block"
        >
          <BaseButton>
            Back to expenses
          </BaseButton>
        </RouterLink>
      </BaseCard>
    </div>
  </AppLayout>
</template>
