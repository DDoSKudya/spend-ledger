import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";

import { useAuthStore } from "@/stores/auth";

declare module "vue-router" {
  interface RouteMeta {
    public?: boolean;
    shell?: "auth" | "app";
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/LoginView.vue"),
    meta: { public: true, shell: "auth" },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/views/RegisterView.vue"),
    meta: { public: true, shell: "auth" },
  },
  {
    path: "/",
    component: () => import("@/components/layout/AppLayout.vue"),
    meta: { shell: "app" },
    children: [
      {
        path: "",
        redirect: { name: "expenses" },
      },
      {
        path: "expenses",
        name: "expenses",
        component: () => import("@/views/ExpensesView.vue"),
      },
      {
        path: "categories",
        name: "categories",
        component: () => import("@/views/CategoriesView.vue"),
      },
      {
        path: "tags",
        name: "tags",
        component: () => import("@/views/TagsView.vue"),
      },
      {
        path: "reports",
        name: "reports",
        component: () => import("@/views/ReportsView.vue"),
      },
      {
        path: "export",
        name: "export",
        component: () => import("@/views/ExportView.vue"),
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/views/NotFoundView.vue"),
    meta: { public: true, shell: "auth" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
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
