<template>
  <nav class="topbar">
    <RouterLink to="/lobby" class="brand">♟ Multi Chess Pro</RouterLink>
    <div class="nav-links">
      <RouterLink v-if="auth.isLoggedIn" to="/lobby">Lobby</RouterLink>
      <RouterLink v-if="auth.isLoggedIn" to="/history">History</RouterLink>
      <span v-if="auth.user" class="user-pill">{{ auth.user.username }} · {{ auth.user.rating }}</span>
      <button v-if="auth.isLoggedIn" @click="logout">Logout</button>
      <RouterLink v-if="!auth.isLoggedIn" to="/login">Login</RouterLink>
      <RouterLink v-if="!auth.isLoggedIn" to="/register">Register</RouterLink>
    </div>
  </nav>
  <main class="container">
    <RouterView />
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
const auth = useAuthStore()
const router = useRouter()
function logout() {
  auth.logout()
  router.push('/login')
}
</script>
