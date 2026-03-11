import { defineStore } from 'pinia'

export const useSimpleStore = defineStore('simple', {
  state: () => ({
    count: 0,
    message: 'Hello Pinia!'
  }),
  
  getters: {
    doubleCount: (state) => state.count * 2
  },
  
  actions: {
    increment() {
      this.count++
    },
    
    setMessage(newMessage) {
      this.message = newMessage
    }
  }
})
