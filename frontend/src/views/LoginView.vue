<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import AuthLayout from "@/components/layout/AuthLayout.vue";
import { getErrorMessage } from "@/api/errors";
import BaseAlert from "@/components/ui/BaseAlert.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
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
  <AuthLayout title="Sign in">
    <form
      class="stack"
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
        block
        :disabled="loading"
      >
        {{ loading ? "Signing in..." : "Sign in" }}
      </BaseButton>
    </form>

    <p class="auth-panel__footer">
      No account?
      <RouterLink
        class="link"
        to="/register"
      >
        Register
      </RouterLink>
    </p>
  </AuthLayout>
</template>
