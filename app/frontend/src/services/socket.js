import { io } from 'socket.io-client'
import { ref } from 'vue'

const socket = ref(null)

export function connectSocket(sessionId) {
  return new Promise((resolve, reject) => {
    if (socket.value?.connected) {
      console.log('✅ Reusing existing socket connection')
      socket.value.emit('joinInterview', { sessionId })
      resolve(socket.value)
      return
    }

    console.log('🔌 Creating new socket connection...')
    socket.value = io(import.meta.env.VITE_BACKEND_URL, {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
      forceNew: false,
      autoConnect: true
    })

    let resolved = false

    socket.value.on('connect', () => {
      console.log('✅ Socket connected, joining interview...')
      if (!resolved) {
        socket.value.emit('joinInterview', { sessionId })
        resolved = true
        resolve(socket.value)
      }

      // ✅ Keep-alive: Send periodic pings to prevent timeout
      const keepAliveInterval = setInterval(() => {
        if (socket.value?.connected) {
          // Send a ping event to keep connection alive
          socket.value.emit('ping', { timestamp: Date.now() })
        } else {
          clearInterval(keepAliveInterval)
        }
      }, 15000) // Every 15 seconds (less than ping_timeout/2)

      // Store interval for cleanup
      socket.value._keepAliveInterval = keepAliveInterval
    })

    socket.value.on('connect_error', (err) => {
      console.error('❌ Socket connection failed:', err)
      if (!resolved) {
        resolved = true
        reject(err)
      }
    })

    socket.value.on('disconnect', (reason) => {
      console.warn('⚠️ Socket disconnected:', reason)
      if (reason === 'io server disconnect') {
        // Server disconnected, reconnect manually
        socket.value.connect()
      }
    })

    socket.value.on('reconnect', (attemptNumber) => {
      console.log(`🔄 Socket reconnected after ${attemptNumber} attempts`)
      if (socket.value.connected) {
        socket.value.emit('joinInterview', { sessionId })
      }
    })

    socket.value.on('reconnect_attempt', (attemptNumber) => {
      console.log(`🔄 Reconnection attempt ${attemptNumber}...`)
    })

    socket.value.on('reconnect_error', (error) => {
      console.error('❌ Reconnection error:', error)
    })

    socket.value.on('reconnect_failed', () => {
      console.error('❌ Reconnection failed after all attempts')
    })

    // Timeout fallback
    setTimeout(() => {
      if (!resolved) {
        if (socket.value?.connected) {
          resolved = true
          socket.value.emit('joinInterview', { sessionId })
          resolve(socket.value)
        } else {
          resolved = true
          reject(new Error('Socket connection timeout'))
        }
      }
    }, 20000)
  })
}

export function disconnectSocket() {
  if (socket.value) {
    console.log('🔌 Disconnecting socket...')
    // Clear keep-alive interval
    if (socket.value._keepAliveInterval) {
      clearInterval(socket.value._keepAliveInterval)
      socket.value._keepAliveInterval = null
    }
    socket.value.disconnect()
    socket.value = null
  }
}

export function getSocket() {
  return socket.value
}

