<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import AuthLayout from "@/components/layout/AuthLayout.vue";
import { getErrorMessage } from "@/api/errors";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
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
  <AuthLayout title="Create account">
    <form
      class="stack"
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
        block
        :disabled="loading"
      >
        {{ loading ? "Creating..." : "Register" }}
      </BaseButton>
    </form>

    <p class="auth-panel__footer">
      Already have an account?
      <RouterLink
        class="link"
        to="/login"
      >
        Sign in
      </RouterLink>
    </p>
  </AuthLayout>
</template>
