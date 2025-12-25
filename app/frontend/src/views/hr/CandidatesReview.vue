<template>
  <div class="review-candidates-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">👥 All Candidates</h1>
        <p class="page-subtitle">View, search for and add new staff</p>
      </div>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <!-- Search Box -->
      <div class="search-box">
        <label class="search-label">Quick search a Candidate</label>
        <div class="search-input-wrapper">
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
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Enter search word"
            class="search-input"
          />
        </div>
      </div>

      <!-- Stats Box -->
      <div class="stats-box">
        <p class="stats-number">{{ totalCandidates }}</p>
        <p class="stats-label">Total number of Candidates</p>
      </div>

      <!-- Filter by Role -->
      <div class="filter-box">
        <label class="filter-label">Filter by Role</label>
        <select v-model="selectedRole" class="filter-select">
          <option value="">All Roles</option>
          <option value="Frontend Developer">Frontend Developer</option>
          <option value="Backend Developer">Backend Developer</option>
          <option value="Full Stack Developer">Full Stack Developer</option>
          <option value="DevOps Engineer">DevOps Engineer</option>
          <option value="Data Scientist">Data Scientist</option>
          <option value="UI/UX Designer">UI/UX Designer</option>
        </select>
      </div>
    </div>

    <!-- Table Section -->
    <div class="table-section">
      <div class="table-header">
        <h2 class="table-title">All Candidates</h2>
        <div class="table-controls">
          <select v-model="selectedRole" class="inline-filter">
            <option value="">All Roles</option>
            <option value="Frontend Developer">Frontend Developer</option>
            <option value="Backend Developer">Backend Developer</option>
            <option value="Full Stack Developer">Full Stack Developer</option>
            <option value="DevOps Engineer">DevOps Engineer</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="UI/UX Designer">UI/UX Designer</option>
          </select>
          <div class="pagination-info">
            <span>Showing</span>
            <select v-model="itemsPerPage" class="items-per-page">
              <option :value="12">12</option>
              <option :value="25">25</option>
              <option :value="50">50</option>
            </select>
            <span>per page</span>
          </div>
        </div>
      </div>

      <!-- DataTable Component -->
      <DataTable
        :columns="tableColumns"
        :data="filteredCandidates"
        row-key="id"
        :items-per-page="itemsPerPage"
      >
        <!-- S/N Cell -->
        <template #cell-sn="{ index }">
          {{ String(index + 1).padStart(2, '0') }}
        </template>

        <!-- AI Match Score Cell -->
        <template #cell-aiMatchScore="{ row }">
          <span :class="['score-badge', row.aiMatchScore >= 70 ? 'high' : 'low']">
            {{ row.aiMatchScore }}
          </span>
        </template>

        <!-- Action Cell -->
        <template #cell-action="{ row }">
          <router-link :to="`/hr/candidates/${row.id}`" class="action-link">
            View more
          </router-link>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import DataTable from '@/components/DataTable.vue'

const store = useStore()

const hrUser = JSON.parse(localStorage.getItem('currentUser'))
const companyId = hrUser?.company_id

const searchQuery = ref('')
const selectedRole = ref('')
const itemsPerPage = ref(12)

const tableColumns = ref([
  { key: 'sn', label: 'S/N' },
  { key: 'firstName', label: 'First Name' },
  { key: 'lastName', label: 'Last Name' },
  { key: 'gender', label: 'Gender' },
  { key: 'role', label: 'Role' },
  { key: 'aiMatchScore', label: 'AI Match Score' },
  { key: 'action', label: 'Action' },
])

const roles = ref([])
const candidatesData = ref([])

/* --------------------------------------------------
   Fetch list of roles
--------------------------------------------------- */
const loadRoles = async () => {
  roles.value = await store.dispatch("hr/fetchCandidateRoles", companyId)
}

/* --------------------------------------------------
   Fetch Candidates + Extract ID from action_url
--------------------------------------------------- */
const loadCandidates = async () => {
  const res = await store.dispatch("hr/fetchCandidates", {
    companyId,
    role: '',
    search: '',
    page: 1,
    perPage: 2000
  })

  candidatesData.value = res.candidates.map((c, index) => {
    // Extract ID from /candidate/<id> → e.g. "/candidate/5"
    const id = c.action_url?.split("/").pop()

    return {
      id: id, // IMPORTANT FIX
      sn: index + 1,
      firstName: c.first_name,
      lastName: c.last_name,
      gender: c.gender,
      role: c.role,
      aiMatchScore: c.ai_match_score ?? 0,
      actionUrl: c.action_url,
    }
  })
}

/* --------------------------------------------------
   PAGE LOAD
--------------------------------------------------- */
onMounted(async () => {
  await loadRoles()
  await loadCandidates()
})

/* --------------------------------------------------
   FILTERING
--------------------------------------------------- */
const filteredCandidates = computed(() => {
  return candidatesData.value.filter(c => {
    const search = searchQuery.value.toLowerCase()

    const matchesSearch =
      c.firstName.toLowerCase().includes(search) ||
      c.lastName.toLowerCase().includes(search) ||
      c.role.toLowerCase().includes(search)

    const matchesRole =
      !selectedRole.value || c.role === selectedRole.value

    return matchesSearch && matchesRole
  })
})

const totalCandidates = computed(() => filteredCandidates.value.length)
</script>



<style scoped>
.review-candidates-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.page-subtitle {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}

/* Search Section */
.search-section {
  display: grid;
  grid-template-columns: 1fr 250px 250px;
  gap: 1.5rem;
  margin-bottom: 2rem;
  align-items: flex-end;
}

/* Search Box */
.search-box {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.search-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
}

.search-input-wrapper {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0 1rem;
  height: 44px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.search-input-wrapper:focus-within {
  border-color: #065eb5;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
}

.search-icon {
  color: #94a3b8;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 0.9rem;
  color: #1e3a5f;
  outline: none;
}

.search-input::placeholder {
  color: #cbd5e1;
}

/* Stats Box */
.stats-box {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.stats-number {
  font-size: 2rem;
  font-weight: 700;
  color: #065eb5;
  margin: 0;
}

.stats-label {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0.25rem 0 0 0;
  font-weight: 500;
}

/* Filter Box */
.filter-box {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
}

.filter-select {
  padding: 0.625rem 1rem;
  padding-right: 2.5rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #1e3a5f;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  height: 44px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%231e3a5f' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 12px;
  transition: all 0.2s ease;
}

.filter-select:hover {
  border-color: #065eb5;
  background-color: #f8fafc;
}

.filter-select:focus {
  border-color: #065eb5;
  outline: none;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
  background-color: white;
}

.filter-select option {
  background: white;
  color: #1e3a5f;
  padding: 0.5rem;
}

.filter-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f1f5f9;
}

/* Table Section */
.table-section {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.table-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.table-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.inline-filter {
  padding: 0.5rem 0.75rem;
  padding-right: 2.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  font-size: 0.85rem;
  color: #1e3a5f;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%231e3a5f' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 12px;
  transition: all 0.2s ease;
}

.inline-filter:hover {
  border-color: #065eb5;
  background-color: #f8fafc;
}

.inline-filter:focus {
  border-color: #065eb5;
  outline: none;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
  background-color: white;
}

.inline-filter option {
  background: white;
  color: #1e3a5f;
  padding: 0.5rem;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #64748b;
}

.items-per-page {
  padding: 0.3rem 0.5rem;
  padding-right: 2rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-weight: 600;
  text-align: center;
  min-width: 50px;
  color: #1e3a5f;
  background: white;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%231e3a5f' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.4rem center;
  background-size: 10px;
  transition: all 0.2s ease;
}

.items-per-page:hover {
  border-color: #065eb5;
  background-color: #f8fafc;
}

.items-per-page:focus {
  border-color: #065eb5;
  outline: none;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
  background-color: white;
}

.items-per-page option {
  background: white;
  color: #1e3a5f;
  padding: 0.5rem;
}

/* Score Badge */
.score-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
}

.score-badge.high {
  background: #dcfce7;
  color: #16a34a;
}

.score-badge.low {
  background: #fee2e2;
  color: #dc2626;
}

/* Action Link */
.action-link {
  color: #065eb5;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.action-link:hover {
  color: #054a94;
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 1200px) {
  .search-section {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .review-candidates-page {
    padding: 1rem;
  }

  .search-section {
    grid-template-columns: 1fr;
  }

  .table-section {
    padding: 1rem;
  }

  .table-controls {
    flex-wrap: wrap;
    width: 100%;
  }
}
</style>
