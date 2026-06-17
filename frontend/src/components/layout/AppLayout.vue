<script setup>
import AppNav from "@/components/layout/AppNav.vue";
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <AppNav />
    <main class="mx-auto max-w-6xl px-4 py-6">
      <slot />
    </main>
  </div>
</template>
