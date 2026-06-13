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
  socket.value.on('game_over', (payload) => { game.value = payload.game })
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
    const { data } = await http.post(`/games/${game.value.id}/resign`)
    game.value = data.game
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to resign'
  }
}
</script>
