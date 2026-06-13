<template>
  <section class="auth-card card">
    <h1>Register</h1>
    <form @submit.prevent="submit">
      <label>Username</label>
      <input v-model="username" required minlength="3" />
      <label>Email</label>
      <input v-model="email" type="email" required />
      <label>Password</label>
      <input v-model="password" type="password" required minlength="6" />
      <button type="submit">Register</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <RouterLink to="/login">Already have account?</RouterLink>
  </section>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
async function submit() {
  try {
    error.value = ''
    await auth.register(username.value, email.value, password.value)
    router.push('/lobby')
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed'
  }
}
</script>
