<template>
  <section class="grid two">
    <div class="card">
      <h1>Lobby</h1>

      <div class="quick-match-box">
        <h3>⚡ Quick Match</h3>
        <p>Get paired with a random opponent instantly.</p>
        <button v-if="!inQueue" @click="joinQueue" class="btn-quick">Find Opponent</button>
        <div v-else class="searching">
          <div class="spinner"></div>
          <span>Searching for opponent...</span>
          <button class="btn-cancel" @click="leaveQueue">Cancel</button>
        </div>
      </div>

      <div class="divider">or</div>

      <p>Create a private room and send the invite link to a friend.</p>
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
import { ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { io } from 'socket.io-client'
import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const preferredColor = ref('white')
const inviteUrl = ref('')
const error = ref('')
const inQueue = ref(false)

const socketUrl = import.meta.env.VITE_SOCKET_URL || window.location.origin
let socket = null

function joinQueue() {
  const token = localStorage.getItem('token')
  socket = io(socketUrl, { transports: ['websocket', 'polling'] })
  socket.on('connect', () => socket.emit('join_queue', { token }))
  socket.on('queue_joined', () => { inQueue.value = true })
  socket.on('match_found', ({ game_id }) => {
    inQueue.value = false
    socket.disconnect()
    router.push(`/game/${game_id}`)
  })
  socket.on('queue_error', ({ error: e }) => {
    error.value = e
    cleanup()
  })
}

function leaveQueue() {
  const token = localStorage.getItem('token')
  socket?.emit('leave_queue', { token })
  cleanup()
}

function cleanup() {
  inQueue.value = false
  socket?.disconnect()
  socket = null
}

onBeforeUnmount(() => { if (inQueue.value) leaveQueue() })

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

<style scoped>
.quick-match-box {
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.3);
  border-radius: 14px;
  padding: 1.2rem 1.4rem;
  margin-bottom: 1rem;
}
.quick-match-box h3 { margin: 0 0 0.3rem; color: #93c5fd; }
.quick-match-box p  { margin: 0 0 1rem; color: #94a3b8; font-size: 0.9rem; }

.btn-quick {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  width: 100%;
  font-size: 1rem;
  padding: 0.7rem;
}

.searching {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(147, 197, 253, 0.3);
  border-top-color: #93c5fd;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

.btn-cancel {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  padding: 0.35rem 0.9rem;
  font-size: 0.85rem;
}

.divider {
  text-align: center;
  color: #475569;
  font-size: 0.85rem;
  margin: 1rem 0;
  position: relative;
}
.divider::before, .divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 42%;
  height: 1px;
  background: #1e293b;
}
.divider::before { left: 0; }
.divider::after  { right: 0; }
</style>
