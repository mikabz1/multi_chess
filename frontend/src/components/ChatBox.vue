<template>
  <section class="card chat-box">
    <h3>Game Chat</h3>
    <div class="messages">
      <div v-for="msg in messages" :key="msg.id" class="message">
        <strong>{{ msg.sender_username || 'Player' }}:</strong>
        <span>{{ msg.message }}</span>
      </div>
    </div>
    <form class="chat-form" @submit.prevent="submit">
      <input v-model="text" placeholder="Write message..." maxlength="500" />
      <button type="submit">Send</button>
    </form>
  </section>
</template>

<script setup>
import { ref } from 'vue'
const props = defineProps({ messages: { type: Array, default: () => [] } })
const emit = defineEmits(['send'])
const text = ref('')
function submit() {
  const value = text.value.trim()
  if (!value) return
  emit('send', value)
  text.value = ''
}
</script>
