<template>
  <div class="game-layout">
    <section class="card game-main">
      <div class="game-header">
        <div>
          <h1>Chess Game</h1>
          <p v-if="game">Status: <strong>{{ game.status }}</strong> · Turn: <strong>{{ game.turn }}</strong> · You: <strong>{{ yourColor || 'spectator' }}</strong></p>
        </div>
        <button v-if="game?.status === 'active'" @click="resign">Resign</button>
      </div>
      <ChessBoard v-if="game" :fen="game.current_fen" :your-color="yourColor" :last-move="lastMove" @move="makeMove" />
      <p v-if="error" class="error">{{ error }}</p>
      <div v-if="game?.status === 'finished'" class="success">Game over: {{ game.result }}</div>
    </section>

    <aside>
      <section class="card">
        <h3>Players</h3>
        <p><strong>White:</strong> {{ game?.white_player?.username || 'Waiting...' }}</p>
        <p><strong>Black:</strong> {{ game?.black_player?.username || 'Waiting...' }}</p>
      </section>
      <section class="card moves-card">
        <h3>Moves</h3>
        <ol>
          <li v-for="move in moves" :key="move.id">{{ move.san_move }} <small>({{ move.uci_move }})</small></li>
        </ol>
      </section>
      <ChatBox :messages="messages" @send="sendChat" />
    </aside>
  </div>

  <Transition name="modal">
    <div v-if="gameOverModal" class="modal-backdrop" @click.self="gameOverModal = null">
      <div class="modal-card" :class="gameOverModal.type">
        <div class="modal-glow" />
        <div class="modal-emoji">{{ gameOverModal.emoji }}</div>
        <h2 class="modal-title">{{ gameOverModal.title }}</h2>
        <p class="modal-sub">{{ gameOverModal.subtitle }}</p>
        <div class="modal-actions">
          <button class="btn-primary" @click="router.push('/lobby')">🏠 Back to Lobby</button>
          <button class="btn-secondary" @click="gameOverModal = null">📋 View Board</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { io } from 'socket.io-client'
import { http } from '../api/http'
import ChessBoard from '../components/ChessBoard.vue'
import ChatBox from '../components/ChatBox.vue'

const route = useRoute()
const router = useRouter()
const game = ref(null)
const moves = ref([])
const messages = ref([])
const yourColor = ref('white')
const error = ref('')
const socket = ref(null)
const lastMove = ref('')
const gameOverModal = ref(null)

const socketUrl = import.meta.env.VITE_SOCKET_URL || window.location.origin

onMounted(async () => {
  try {
    if (route.path.startsWith('/join/')) {
      const { data } = await http.post(`/games/join/${route.params.token}`)
      router.replace(`/game/${data.game.id}`)
      game.value = data.game
    } else {
      const { data } = await http.get(`/games/${route.params.id}`)
      game.value = data.game
      moves.value = data.moves
      messages.value = data.messages
    }
    connectSocket()
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load game'
  }
})

onBeforeUnmount(() => {
  socket.value?.emit('leave_game', { game_id: game.value?.id })
  socket.value?.disconnect()
})

function connectSocket() {
  const token = localStorage.getItem('token')
  socket.value = io(socketUrl, { transports: ['websocket', 'polling'] })
  socket.value.on('connect', () => socket.value.emit('join_game', { token, game_id: game.value.id }))
  socket.value.on('game_state', (payload) => {
    game.value = payload.game
    yourColor.value = payload.your_color
  })
  socket.value.on('move_made', (payload) => {
    game.value = payload.game
    moves.value.push(payload.move)
    lastMove.value = payload.move.uci_move
    error.value = ''
  })
  socket.value.on('chat_message', (payload) => messages.value.push(payload))
  socket.value.on('game_over', (payload) => {
    game.value = payload.game
    const result = payload.game.result
    const color = yourColor.value
    const resign = payload.reason === 'resign'
    const won = (result === 'white_win' && color === 'white') || (result === 'black_win' && color === 'black')
    const lost = (result === 'white_win' && color === 'black') || (result === 'black_win' && color === 'white')
    gameOverModal.value = won
      ? { type: 'win',  emoji: '🏆', title: 'You Won!',  subtitle: resign ? 'Your opponent resigned. Well played!' : 'Brilliant play — your opponent had no answer.' }
      : lost
      ? { type: 'lose', emoji: '😔', title: 'You Lost',  subtitle: resign ? 'You resigned. Better luck next time!' : 'Better luck next time. Study the board and come back stronger.' }
      : { type: 'draw', emoji: '🤝', title: 'It\'s a Draw!', subtitle: 'An even battle — neither side could break through.' }
  })
  socket.value.on('invalid_move', (payload) => { error.value = payload.error })
  socket.value.on('error_message', (payload) => { error.value = payload.error })
}

function makeMove(move) {
  const token = localStorage.getItem('token')
  socket.value.emit('make_move', { token, game_id: game.value.id, move })
}

function sendChat(message) {
  const token = localStorage.getItem('token')
  socket.value.emit('send_chat_message', { token, game_id: game.value.id, message })
}

async function resign() {
  try {
    await http.post(`/games/${game.value.id}/resign`)
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to resign'
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-card {
  position: relative;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 24px;
  padding: 3rem 3.5rem;
  text-align: center;
  max-width: 420px;
  width: 90%;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.6);
}

.modal-glow {
  position: absolute;
  inset: 0;
  border-radius: 24px;
  pointer-events: none;
  opacity: 0.15;
}
.modal-card.win  .modal-glow { background: radial-gradient(circle at 50% 0%, #22c55e, transparent 70%); }
.modal-card.lose .modal-glow { background: radial-gradient(circle at 50% 0%, #ef4444, transparent 70%); }
.modal-card.draw .modal-glow { background: radial-gradient(circle at 50% 0%, #3b82f6, transparent 70%); }

.modal-card.win  { border-color: rgba(34, 197, 94, 0.35); }
.modal-card.lose { border-color: rgba(239, 68, 68, 0.35); }
.modal-card.draw { border-color: rgba(59, 130, 246, 0.35); }

.modal-emoji {
  font-size: 5rem;
  line-height: 1;
  margin-bottom: 1rem;
  animation: pop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

.modal-title {
  font-size: 2rem;
  font-weight: 900;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}
.modal-card.win  .modal-title { color: #4ade80; }
.modal-card.lose .modal-title { color: #f87171; }
.modal-card.draw .modal-title { color: #60a5fa; }

.modal-sub {
  color: #94a3b8;
  margin: 0 0 2rem;
  font-size: 0.95rem;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: #fff;
  font-weight: 700;
  padding: 0.65rem 1.4rem;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
}
.btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }

.btn-secondary {
  background: rgba(30, 41, 59, 0.8);
  color: #cbd5e1;
  font-weight: 600;
  padding: 0.65rem 1.4rem;
  border-radius: 10px;
  border: 1px solid #334155;
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
}
.btn-secondary:hover { background: rgba(51, 65, 85, 0.9); transform: translateY(-1px); }

.modal-enter-active { animation: modal-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both; }
.modal-leave-active { animation: modal-out 0.2s ease-in both; }

@keyframes modal-in {
  from { opacity: 0; transform: scale(0.8) translateY(30px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes modal-out {
  from { opacity: 1; transform: scale(1); }
  to   { opacity: 0; transform: scale(0.9); }
}
@keyframes pop {
  from { transform: scale(0.4); opacity: 0; }
  to   { transform: scale(1);   opacity: 1; }
}
</style>
