<script setup lang="ts">
import { RouterLink } from "vue-router";

import AuthLayout from "@/components/layout/AuthLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
</script>

<template>
  <AuthLayout title="Page not found">
    <p class="view-head__meta mb-4">
      The page you requested does not exist.
    </p>
    <RouterLink to="/expenses">
      <BaseButton block>
        Back to expenses
      </BaseButton>
    </RouterLink>
  </AuthLayout>
</template>
