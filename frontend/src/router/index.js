import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../pages/LoginPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import LobbyPage from '../pages/LobbyPage.vue'
import GamePage from '../pages/GamePage.vue'
import HistoryPage from '../pages/HistoryPage.vue'

const routes = [
  { path: '/', redirect: '/lobby' },
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  { path: '/lobby', component: LobbyPage, meta: { requiresAuth: true } },
  { path: '/game/:id', component: GamePage, meta: { requiresAuth: true } },
  { path: '/join/:token', component: GamePage, meta: { requiresAuth: true, joinByToken: true } },
  { path: '/history', component: HistoryPage, meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    return `/login?redirect=${encodeURIComponent(to.fullPath)}`
  }
})

export default router
