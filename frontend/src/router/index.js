import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "@/stores/auth";
import CategoriesView from "@/views/CategoriesView.vue";
import ExpensesView from "@/views/ExpensesView.vue";
import ExportView from "@/views/ExportView.vue";
import LoginView from "@/views/LoginView.vue";
import NotFoundView from "@/views/NotFoundView.vue";
import RegisterView from "@/views/RegisterView.vue";
import ReportsView from "@/views/ReportsView.vue";
import TagsView from "@/views/TagsView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      redirect: "/expenses",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { public: true },
    },
    {
      path: "/register",
      name: "register",
      component: RegisterView,
      meta: { public: true },
    },
    {
      path: "/expenses",
      name: "expenses",
      component: ExpensesView,
    },
    {
      path: "/categories",
      name: "categories",
      component: CategoriesView,
    },
    {
      path: "/tags",
      name: "tags",
      component: TagsView,
    },
    {
      path: "/reports",
      name: "reports",
      component: ReportsView,
    },
    {
      path: "/export",
      name: "export",
      component: ExportView,
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: NotFoundView,
      meta: { public: true },
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (to.meta.public) {
    if (auth.isAuthenticated && (to.name === "login" || to.name === "register")) {
      return { name: "expenses" };
    }
    return true;
  }

  if (auth.isAuthenticated) {
    return true;
  }

  try {
    await auth.refresh();
    await auth.fetchMe();
    return true;
  } catch {
    return {
      name: "login",
      query: { redirect: to.fullPath },
    };
  }
});

export default router;
