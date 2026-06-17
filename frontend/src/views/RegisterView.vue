<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

import { getErrorMessage } from "@/api/errors";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { useAuth } from "@/composables/useAuth";

const router = useRouter();
const { register } = useAuth();

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function submit() {
  error.value = "";
  loading.value = true;

  try {
    await register(email.value, password.value);
    await router.push({ name: "login", query: { registered: "1" } });
  } catch (err) {
    error.value = getErrorMessage(err, "Registration failed");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4 py-8">
    <BaseCard>
      <h1 class="mb-6 text-2xl font-semibold">
        Create account
      </h1>

      <form
        class="grid gap-4"
        @submit.prevent="submit"
      >
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
          {{ loading ? "Creating..." : "Register" }}
        </BaseButton>
      </form>

      <p class="mt-4 text-sm text-slate-600">
        Already have an account?
        <RouterLink
          class="font-medium text-slate-900 underline"
          to="/login"
        >
          Sign in
        </RouterLink>
      </p>
    </BaseCard>
  </div>
</template>
