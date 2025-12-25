<template>
  <div class="dashboard-layout">
    <Sidebar />
    <NavBar />
    <div class="layout-wrapper" :class="{ 'with-sidebar': showRightSidebar }">
      <div class="main-content">
        <router-view />
      </div>
      <!-- Only show UpcomingMeetings on HR Dashboard -->
      <aside v-if="showRightSidebar" class="right-sidebar">
        <UpcomingMeetings />
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import Sidebar from './Sidebar.vue'
import NavBar from './NavBar.vue'
import UpcomingMeetings from './UpcomingMeetings.vue'

const store = useStore()
const route = useRoute()

const isSidebarCollapsed = computed(() => store.getters['ui/isSidebarCollapsed'])

// Show right sidebar only on HR Dashboard
const showRightSidebar = computed(() => {
  return route.path.includes('/hr/dashboard')
})
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

.layout-wrapper {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
  margin-top: 60px;
  margin-left: 240px;
  transition: margin-left 220ms cubic-bezier(0.4, 0.8, 0.6, 1);
}

/* When right sidebar is shown, adjust grid */
.layout-wrapper.with-sidebar {
  grid-template-columns: 1fr 380px;
}

.dashboard-layout :deep(.sidebar) {
  transition: width 220ms cubic-bezier(0.4, 0.8, 0.6, 1);
}

/* When sidebar is collapsed, adjust main wrapper */
:global(.sidebar-collapsed ~ .layout-wrapper) {
  margin-left: 72px;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: #f5f7fa;
}

.right-sidebar {
  position: sticky;
  top: 60px;
  height: calc(100vh - 60px);
  background: #fff;
  border-left: 1px solid #e5e7eb;
  overflow-y: auto;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.03);
}

/* Scrollbar styling */
.right-sidebar::-webkit-scrollbar {
  width: 6px;
}

.right-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.right-sidebar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 3px;
}

.right-sidebar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

/* Responsive */
@media (max-width: 1200px) {
  .layout-wrapper.with-sidebar {
    grid-template-columns: 1fr;
  }

  .right-sidebar {
    display: none;
  }
}

@media (max-width: 768px) {
  .layout-wrapper {
    margin-left: 0;
  }
}
</style>
