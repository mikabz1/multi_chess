<template>
  <section class="grid two">
    <div class="card">
      <h1>Lobby</h1>
      <p>Create a private chess room and send the invite link to another player.</p>
      <label>Your color</label>
      <select v-model="preferredColor">
        <option value="white">White</option>
        <option value="black">Black</option>
      </select>
      <button @click="createGame">Create Game</button>
      <div v-if="inviteUrl" class="invite-box">
        <h3>Invite link</h3>
        <input :value="inviteUrl" readonly />
        <button @click="copyInvite">Copy</button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <div class="card">
      <h2>Your stats</h2>
      <p><strong>Rating:</strong> {{ auth.user?.rating }}</p>
      <p><strong>Wins:</strong> {{ auth.user?.wins }}</p>
      <p><strong>Losses:</strong> {{ auth.user?.losses }}</p>
      <p><strong>Draws:</strong> {{ auth.user?.draws }}</p>
      <RouterLink to="/history">View game history</RouterLink>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
const preferredColor = ref('white')
const inviteUrl = ref('')
const error = ref('')

async function createGame() {
  try {
    error.value = ''
    const { data } = await http.post('/games', { preferred_color: preferredColor.value })
    inviteUrl.value = `${window.location.origin}/join/${data.invite_token}`
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to create game'
  }
}
async function copyInvite() {
  await navigator.clipboard.writeText(inviteUrl.value)
}
</script>
