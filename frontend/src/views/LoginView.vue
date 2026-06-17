<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getErrorMessage } from "@/api/errors";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { useAuth } from "@/composables/useAuth";
import { safeRedirectPath } from "@/utils/navigation";

const router = useRouter();
const route = useRoute();
const { login } = useAuth();

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);
const registered = route.query.registered === "1";

async function submit() {
  error.value = "";
  loading.value = true;

  try {
    await login(email.value, password.value);
    await router.push(safeRedirectPath(route.query.redirect));
  } catch (err) {
    error.value = getErrorMessage(err, "Login failed");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4 py-8">
    <BaseCard>
      <h1 class="mb-6 text-2xl font-semibold">
        Sign in
      </h1>

      <form
        class="grid gap-4"
        @submit.prevent="submit"
      >
        <BaseAlert
          v-if="registered"
          variant="success"
        >
          Account created. Sign in to continue.
        </BaseAlert>

        <BaseAlert
          v-if="error"
          variant="error"
        >
          {{ error }}
        </BaseAlert>

        <BaseInput
          v-model="email"
          label="Email"
          type="email"
          required
        />

        <BaseInput
          v-model="password"
          label="Password"
          type="password"
          minlength="8"
          required
        />

        <BaseButton
          type="submit"
          :disabled="loading"
        >
          {{ loading ? "Signing in..." : "Sign in" }}
        </BaseButton>
      </form>

      <p class="mt-4 text-sm text-slate-600">
        No account?
        <RouterLink
          class="font-medium text-slate-900 underline"
          to="/register"
        >
          Register
        </RouterLink>
      </p>
    </BaseCard>
  </div>
</template>
