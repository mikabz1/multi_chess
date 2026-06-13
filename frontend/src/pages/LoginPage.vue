<template>
  <section class="auth-card card">
    <h1>Login</h1>
    <form @submit.prevent="submit">
      <label>Username or Email</label>
      <input v-model="usernameOrEmail" required />
      <label>Password</label>
      <input v-model="password" type="password" required />
      <button type="submit">Login</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <RouterLink to="/register">Create account</RouterLink>
  </section>
</template>
<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const usernameOrEmail = ref('')
const password = ref('')
const error = ref('')
async function submit() {
  try {
    error.value = ''
    await auth.login(usernameOrEmail.value, password.value)
    router.push(route.query.redirect || '/lobby')
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed'
  }
}
</script>
