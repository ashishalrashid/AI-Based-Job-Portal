// This module will globally track UI state, like the sidebar.
export default {
  namespaced: true,

  state: () => ({
    isSidebarCollapsed: false,
  }),

  mutations: {
    // Mutation to set the state
    setSidebarCollapsed(state, isCollapsed) {
      state.isSidebarCollapsed = isCollapsed
    },
    // Mutation to toggle the state
    toggleSidebar(state) {
      state.isSidebarCollapsed = !state.isSidebarCollapsed
    },
  },

  actions: {
    // Action that components will call
    toggleSidebar({ commit }) {
      commit('toggleSidebar')
    },
  },

  getters: {
    // Getter for components to read the state
    isSidebarCollapsed: (state) => state.isSidebarCollapsed,
  },
}
