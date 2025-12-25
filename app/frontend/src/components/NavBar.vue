<template>
  <header class="navbar" :style="{ left: navbarLeft }">
    <div class="navbar-content">
      <!-- Search Bar only on HR Dashboard -->
      <div v-if="isHRDashboard" class="search-container">
        <input
          type="text"
          class="search-input"
          placeholder="Search employees, positions..."
          v-model="searchQuery"
        />
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="search-icon"
        >
          <circle cx="11" cy="11" r="8"></circle>
          <path d="m21 21-4.35-4.35"></path>
        </svg>
      </div>

      <!-- Title when not on HR Dashboard -->
      <h1 v-else class="navbar-title"></h1>

      <!-- Right Section -->
      <div class="navbar-right">
        <!-- Notifications -->
        <button class="icon-btn" aria-label="Notifications">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
          </svg>
        </button>

        <!-- MailDev (Development Testing) -->
        <button
          class="icon-btn"
          @click="openMailDev"
          aria-label="View MailDev"
          title="View emails in MailDev - Development testing only"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
            <polyline points="22,6 12,13 2,6"></polyline>
          </svg>
        </button>

        <!-- User Profile Dropdown -->
        <div class="user-profile">
          <button class="profile-btn" @click="toggleDropdown" aria-label="Profile">
            <div class="avatar">{{ userInitials }}</div>
            <span class="user-name">{{ currentUserName }}</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              :class="['chevron-icon', { 'chevron-open': isDropdownOpen }]"
            >
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>

          <!-- Dropdown Menu -->
          <transition name="dropdown">
            <div v-if="isDropdownOpen" class="profile-dropdown">
              <!-- Profile Header -->
              <div class="dropdown-header">
                <div class="header-avatar">{{ userInitials }}</div>
                <div class="header-info">
                  <p class="header-name">{{ currentUserName }}</p>
                  <p class="header-email">{{ currentUserEmail }}</p>
                  <p class="header-role">{{ userRoleLabel }}</p>
                </div>
              </div>

              <!-- Divider -->
              <div class="dropdown-divider"></div>

              <!-- Menu Items -->
              <div class="dropdown-menu">
                <router-link
                  :to="`/${userRole}/profile`"
                  class="dropdown-item"
                  @click="isDropdownOpen = false"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  <span>My Profile</span>
                </router-link>

                <button class="dropdown-item" @click="handleChangeTheme">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <circle cx="12" cy="12" r="5"></circle>
                    <line x1="12" y1="1" x2="12" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="23"></line>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                    <line x1="1" y1="12" x2="3" y2="12"></line>
                    <line x1="21" y1="12" x2="23" y2="12"></line>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                  </svg>
                  <span>Change Theme</span>
                </button>
              </div>

              <!-- Divider -->
              <div class="dropdown-divider"></div>

              <!-- Logout Button -->
              <button class="dropdown-logout" @click="handleLogout">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                  <polyline points="16 17 21 12 16 7"></polyline>
                  <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
                <span>Logout</span>
              </button>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'

const route = useRoute()
const router = useRouter()
const store = useStore()

const searchQuery = ref('')
const isDropdownOpen = ref(false)

const isSidebarCollapsed = computed(() => store.getters['ui/isSidebarCollapsed'])

const isHRDashboard = computed(() => {
  return route.path.includes('hr/dashboard')
})

// Get current user from auth store
const currentUser = computed(() => store.getters['auth/currentUser'])
const userRole = computed(() => store.getters['auth/userRole'])

const currentUserName = computed(() => currentUser.value?.name || 'User')
const currentUserEmail = computed(() => currentUser.value?.email || 'user@example.com')

// Get user initials for avatar
const userInitials = computed(() => {
  const name = currentUserName.value || 'User'
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

// Get role label
const userRoleLabel = computed(() => {
  const roles = {
    applicant: 'Candidate',
    hr: 'HR Manager',
    organization: 'Organization Admin',
  }
  return roles[userRole.value] || 'User'
})

// Dynamically calculate navbar left position based on sidebar state
const navbarLeft = computed(() => {
  return isSidebarCollapsed.value ? '60px' : '240px'
})

// Toggle dropdown menu
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  const dropdown = document.querySelector('.user-profile')
  if (dropdown && !dropdown.contains(event.target)) {
    isDropdownOpen.value = false
  }
}

// Change theme handler
const handleChangeTheme = () => {
  store.dispatch('theme/toggleTheme')
  isDropdownOpen.value = false
}

// Logout handler
const handleLogout = async () => {
  console.log('Logging out...')
  await store.dispatch('auth/logout')
  isDropdownOpen.value = false
  router.push('/login')
}

// MailDev handler - Opens MailDev for testing
const openMailDev = () => {
  window.open('http://localhost:1080', '_blank')
}

// Add event listener for outside clicks
if (typeof window !== 'undefined') {
  window.addEventListener('click', handleClickOutside)
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  right: 0;
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  z-index: 90;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  transition: left 220ms cubic-bezier(0.4, 0.8, 0.6, 1);
}

.navbar-content {
  height: 100%;
  padding: 0 2rem 0 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 2rem;
}

/* Search Bar Styles */
.search-container {
  flex: 1;
  max-width: 400px;
  position: relative;
  display: flex;
  align-items: center;
  margin-left: 2rem;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.25rem;
  font-size: 0.9rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  outline: none;
  transition: all 0.2s ease;
  background: #f8f9fa;
  color: #1e293b;
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-input:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #64748b;
  pointer-events: none;
}

/* Title Styles */
.navbar-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 0 2rem;
  flex: 1;
}

/* Right Section */
.navbar-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-left: auto;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
  border-radius: 6px;
  width: 36px;
  height: 36px;
}

.icon-btn:hover {
  color: #1e3a5f;
  background: #f1f5f9;
}

/* User Profile */
.user-profile {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-left: 1rem;
  border-left: 1px solid #e2e8f0;
}

.profile-btn {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #1e3a5f;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.profile-btn:hover {
  background: #f1f5f9;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #6366f1;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1e3a5f;
  display: none;
}

.chevron-icon {
  color: #94a3b8;
  transition: transform 0.2s ease;
}

.chevron-icon.chevron-open {
  transform: rotate(180deg);
}

/* Dropdown Menu */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 10px 38px rgba(0, 0, 0, 0.12);
  z-index: 1000;
  width: 320px;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e5e7eb;
}

.header-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #6366f1;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  flex-shrink: 0;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.header-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-email {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0.2rem 0 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-role {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0.2rem 0 0 0;
  font-weight: 500;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
}

/* Dropdown Menu Items */
.dropdown-menu {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: #475569;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  text-align: left;
}

.dropdown-item:hover {
  background: #f8f9fa;
  color: #1e3a5f;
}

.dropdown-item svg {
  color: #64748b;
  transition: color 0.2s ease;
  flex-shrink: 0;
}

.dropdown-item:hover svg {
  color: #6366f1;
}

/* Logout Button */
.dropdown-logout {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: #ef4444;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  text-align: left;
}

.dropdown-logout:hover {
  background: #fee2e2;
}

.dropdown-logout svg {
  color: #ef4444;
  transition: color 0.2s ease;
  flex-shrink: 0;
}

/* Dropdown Animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Responsive */
@media (max-width: 900px) {
  .navbar {
    left: 60px !important;
  }

  .navbar-content {
    padding: 0 1.5rem 0 0;
  }

  .search-container {
    max-width: 300px;
    margin-left: 1rem;
  }

  .navbar-title {
    font-size: 1.1rem;
    margin-left: 1rem;
  }
}

@media (max-width: 768px) {
  .navbar {
    left: 0 !important;
  }

  .navbar-title {
    display: none;
  }

  .navbar-content {
    padding: 0 1rem;
    gap: 1rem;
  }

  .search-container {
    max-width: 200px;
    margin-left: 0.5rem;
  }

  .user-name {
    display: none;
  }

  .user-profile {
    padding-left: 0;
    border-left: none;
  }

  .profile-dropdown {
    width: 280px;
    right: -10px;
  }
}
</style>
