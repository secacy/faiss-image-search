import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

// 页面组件懒加载
const Home = () => import("@/views/Home.vue");
const ImageGallery = () => import("@/views/ImageGallery.vue");
const SearchResults = () => import("@/views/SearchResults.vue");
const AdminLogin = () => import("@/views/admin/Login.vue");
const AdminDashboard = () => import("@/views/admin/Dashboard.vue");
const AdminLayout = () => import("@/layouts/AdminLayout.vue");
const UserLayout = () => import("@/layouts/UserLayout.vue");

const routes = [
  {
    path: "/",
    component: UserLayout,
    children: [
      {
        path: "",
        name: "Home",
        component: Home,
        meta: {
          title: "首页 - 图与图寻",
          description: "智能图像搜索，以图搜图",
        },
      },
      {
        path: "/gallery",
        name: "ImageGallery",
        component: ImageGallery,
        meta: {
          title: "图片库 - 图与图寻",
        },
      },
      {
        path: "/search",
        name: "SearchResults",
        component: SearchResults,
        meta: {
          title: "搜索结果 - 图与图寻",
        },
      },
    ],
  },
  {
    path: "/admin/login",
    name: "AdminLogin",
    component: AdminLogin,
    meta: {
      title: "管理员登录 - 图与图寻",
      requiresGuest: true,
    },
  },
  {
    path: "/admin",
    component: AdminLayout,
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: "",
        redirect: "/admin/dashboard",
      },
      {
        path: "dashboard",
        name: "AdminDashboard",
        component: AdminDashboard,
        meta: {
          title: "管理后台 - 图与图寻",
        },
      },
      {
        path: "images",
        name: "AdminImages",
        component: () => import("@/views/admin/ImageManagement.vue"),
        meta: {
          title: "图片管理 - 图与图寻",
        },
      },
      {
        path: "upload",
        name: "AdminUpload",
        component: () => import("@/views/admin/ImageUpload.vue"),
        meta: {
          title: "图片上传 - 图与图寻",
        },
      },
      {
        path: "logs",
        name: "AdminLogs",
        component: () => import("@/views/admin/SystemLogs.vue"),
        meta: {
          title: "操作日志 - 图与图寻",
        },
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: () => import("@/views/NotFound.vue"),
    meta: {
      title: "页面未找到 - 图与图寻",
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title;
  }

  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/admin/login");
    return;
  }

  // 检查是否需要游客状态（已登录用户不能访问登录页）
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next("/admin/dashboard");
    return;
  }

  next();
});

export default router;
