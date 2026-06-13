<template>
  <section class="card">
    <h1>Game History</h1>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>White</th>
          <th>Black</th>
          <th>Status</th>
          <th>Result</th>
          <th>Open</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="game in games" :key="game.id">
          <td>{{ new Date(game.created_at).toLocaleString() }}</td>
          <td>{{ game.white_player?.username || '-' }}</td>
          <td>{{ game.black_player?.username || '-' }}</td>
          <td>{{ game.status }}</td>
          <td>{{ game.result || '-' }}</td>
          <td><RouterLink :to="`/game/${game.id}`">Open</RouterLink></td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { http } from '../api/http'
const games = ref([])
onMounted(async () => {
  const { data } = await http.get('/games')
  games.value = data.games
})
</script>
