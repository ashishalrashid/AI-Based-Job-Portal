const state = {
  isDarkMode: localStorage.getItem('theme') === 'dark' || false,
}

const getters = {
  isDarkMode: (state) => state.isDarkMode,
  currentTheme: (state) => (state.isDarkMode ? 'dark' : 'light'),
}

const mutations = {
  SET_DARK_MODE(state, isDark) {
    state.isDarkMode = isDark
    localStorage.setItem('theme', isDark ? 'dark' : 'light')
    updateDocumentTheme(isDark)
  },
  TOGGLE_THEME(state) {
    const newTheme = !state.isDarkMode
    state.isDarkMode = newTheme
    localStorage.setItem('theme', newTheme ? 'dark' : 'light')
    updateDocumentTheme(newTheme)
  },
}

const actions = {
  toggleTheme({ commit }) {
    commit('TOGGLE_THEME')
  },
  setTheme({ commit }, isDark) {
    commit('SET_DARK_MODE', isDark)
  },
  initializeTheme({ commit }) {
    const savedTheme = localStorage.getItem('theme')
    const isDark = savedTheme === 'dark'
    commit('SET_DARK_MODE', isDark)
  },
}

// Helper function to apply theme class to document element
function updateDocumentTheme(isDark) {
  if (isDark) {
    document.documentElement.classList.add('dark-theme')
    document.documentElement.classList.remove('light-theme')
  } else {
    document.documentElement.classList.add('light-theme')
    document.documentElement.classList.remove('dark-theme')
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
}
