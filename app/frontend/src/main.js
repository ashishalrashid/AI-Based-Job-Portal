import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './assets/styles/global.css'

const app = createApp(App)

app.use(store)
app.use(router)

store.dispatch('theme/initializeTheme') // Initialize theme on startup

app.mount('#app')
