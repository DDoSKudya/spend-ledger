import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import { configureApi } from "./api/client";
import router from "./router";
import { useAuthStore } from "./stores/auth";
import "./style.css";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

configureApi({
  getToken: () => useAuthStore().accessToken,
  refresh: () => useAuthStore().refresh(),
  onFailure: () => useAuthStore().clear(),
});

app.use(router);
app.mount("#app");
