import { defineStore } from 'pinia'
import { http } from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token'),
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token),
  },
  actions: {
    setSession(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    async login(usernameOrEmail, password) {
      const { data } = await http.post('/auth/login', { username_or_email: usernameOrEmail, password })
      this.setSession(data.access_token, data.user)
    },
    async register(username, email, password) {
      const { data } = await http.post('/auth/register', { username, email, password })
      this.setSession(data.access_token, data.user)
    },
  },
})
