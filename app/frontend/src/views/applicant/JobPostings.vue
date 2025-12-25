<template>
  <div class="job-postings-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">All Opportunities</h1>
        <p class="page-subtitle">View all Related Jobs</p>
      </div>
      <div class="header-stats">
        <div class="stats-box">
          <p class="stats-number">{{ totalJobs }}</p>
          <p class="stats-label">Total Related Jobs</p>
        </div>
      </div>
    </div>

    <!-- Search & Filter Section -->
    <div class="search-filter-section">
      <!-- Search -->
      <div class="search-memo">
        <label class="filter-label">Quick search Jobs</label>
        <div class="search-input-wrapper">
          <input
            type="text"
            placeholder="Enter search word"
            v-model="searchQuery"
            class="search-input"
            @input="currentPage = 1"
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
      </div>

      <!-- Filter Jobs Dropdown -->
      <div class="filter-jobs">
        <label class="filter-label">Filter Jobs</label>
        <select v-model="selectedRole" class="role-select" @change="currentPage = 1">
  <option value="">All Jobs</option>
  <option
    v-for="role in availableRoles"
    :key="role"
    :value="role"
  >
    {{ role }}
  </option>
</select>
      </div>

      <!-- Search Button -->
      <button class="search-btn">Search</button>
    </div>

    <!-- Jobs Table Section -->
    <div class="jobs-table-section">
      <div class="table-header">
        <h2 class="table-title">All Jobs</h2>
        <div class="pagination-info">
          <span>Showing</span>
          <input
            type="number"
            v-model.number="itemsPerPage"
            min="1"
            max="100"
            class="items-input"
            @change="currentPage = 1"
          />
          <span>per page</span>
        </div>
      </div>

      <!-- Table -->
      <div class="table-wrapper">
        <table class="jobs-table">
          <thead>
            <tr>
              <th>S/N</th>
              <th>Position</th>
              <th>Company</th>
              <th>Location</th>
              <th>Work Mode</th>
              <th>Skills Matched</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(job, index) in paginatedJobs" :key="job.id">
              <td>{{ String(index + 1).padStart(2, '0') }}</td>
              <td class="position-cell">{{ job.position }}</td>
              <td>{{ job.company }}</td>
              <td>{{ job.location }}</td>
              <td>
                <span class="work-mode-badge">{{ job.workMode }}</span>
              </td>
              <td class="skills-cell">{{ job.skillsMatched }}/{{ job.totalSkills }}</td>
              <td>
                <router-link :to="`/applicant/job-details/${job.id}`" class="view-more-link">
                  View more
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination-section">
        <div class="pagination-buttons">
          <button
            @click="currentPage = 1"
            :class="['pagination-btn', { active: currentPage === 1 }]"
          >
            1
          </button>
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="currentPage = page"
            :class="['pagination-btn', { active: currentPage === page }]"
          >
            {{ page }}
          </button>
          <button v-if="totalPages > 5" class="pagination-btn pagination-dots">»</button>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <p class="footer-text">Copyright © 2022 Relia Energy. All Rights Reserved</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue"
import { useStore } from "vuex"
import { useRouter } from "vue-router"

const store = useStore()
const router = useRouter()

// UI State
const searchQuery = ref("")
const selectedRole = ref("")       // Filter by role
const currentPage = ref(1)
const itemsPerPage = ref(16)

// API Data + status
const jobs = ref([])
const totalPages = ref(1)
const totalJobs = ref(0)
const isLoading = ref(false)
const error = ref(null)
const availableRoles = ref([]) 

// Fetch jobs from backend + transform for UI
const fetchJobs = async () => {
  isLoading.value = true
  error.value = null
  try {
    console.log("fetchJobs ->", {
      role: selectedRole.value,
      search: searchQuery.value,
      page: currentPage.value,
      perPage: itemsPerPage.value,
    })

    const data = await store.dispatch("applicant/fetchJobOpportunities", {
      role: selectedRole.value,
      search: searchQuery.value,
      page: currentPage.value,
      perPage: itemsPerPage.value
    })

    // Defensive: log raw response to console to verify shape
    console.log("backend response:", data)

    // Transform backend → frontend expected structure
    jobs.value = (data.jobs || []).map(j => ({
      id: j.job_id,                                   // backend → UI expected
      position: j.position,
      company: j.company,
      location: j.location ?? "N/A",
      workMode: j.work_mode ?? "N/A",
      // skills_matched = "1/3" → split into two fields
      skillsMatched: (j.skills_matched?.split("/")[0]) ?? "0",
      totalSkills: (j.skills_matched?.split("/")[1]) ?? "0"
    }))

    totalJobs.value = data.total_jobs ?? jobs.value.length
    totalPages.value = data.total_pages ?? Math.max(1, Math.ceil(totalJobs.value / itemsPerPage.value))
    const rolesFromJobs = jobs.value.map(j => j.position)
    availableRoles.value = Array.from(new Set(rolesFromJobs)).sort()

    // sanity log
    console.log("mapped jobs:", jobs.value, { totalJobs: totalJobs.value, totalPages: totalPages.value })

  } catch (err) {
    console.error("Failed to load jobs", err)
    error.value = err
  } finally {
    isLoading.value = false
  }
}

// PAGINATION: computed list that the template uses
const paginatedJobs = computed(() => {
  // if backend already returns page-limited results (it does), you can just return jobs.value.
  // but keep a defensive local pagination in case backend returns full list:
  const perPage = Number(itemsPerPage.value) || 16
  const page = Number(currentPage.value) || 1

  // If backend is already paginating, jobs.value is the current page => return as-is:
  // Heuristic: if totalJobs > jobs.length and totalPages >= page, treat jobs as server-side page.
  if (totalPages.value > 1) {
    // return whatever the backend sent (current page)
    return jobs.value
  }

  // Fallback client-side pagination:
  const start = (page - 1) * perPage
  return jobs.value.slice(start, start + perPage)
})

// Watchers → auto-refresh
watch([searchQuery, selectedRole], () => {
  currentPage.value = 1
  fetchJobs()
})

// When page changes, fetch page (server-side pagination)
watch(currentPage, (n, o) => {
  // avoid redundant fetch on initialization if you prefer (but it's ok)
  fetchJobs()
})

// If itemsPerPage changed, reset to page 1 and fetch
watch(itemsPerPage, () => {
  currentPage.value = 1
  fetchJobs()
})

// Initial load
onMounted(fetchJobs)

// Pagination compute (5 visible pagination numbers)
const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  const half = Math.floor(maxVisible / 2)

  let start = Math.max(2, currentPage.value - half)
  let end = Math.min(totalPages.value, start + maxVisible - 2)

  if (end - start < maxVisible - 2) {
    start = Math.max(2, end - maxVisible + 2)
  }

  for (let i = start; i <= end; i++) pages.push(i)

  return pages
})
</script>




<style scoped>
.job-postings-page {
  background: #f5f7fa;
  min-height: 100vh;
  padding: 2rem 1.5rem;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.header-content h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-content h1::before {
  content: '📁';
  font-size: 1.5rem;
}

.page-subtitle {
  font-size: 0.9rem;
  color: #94a3b8;
  margin: 0.25rem 0 0 0;
}

.header-stats {
  display: flex;
  gap: 1rem;
}

.stats-box {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
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
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0.5rem 0 0 0;
  font-weight: 500;
}

/* Search & Filter Section */
.search-filter-section {
  display: grid;
  grid-template-columns: 1.5fr 1fr auto;
  gap: 1.5rem;
  margin-bottom: 2rem;
  align-items: flex-end;
}

.search-memo,
.filter-jobs {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e3a5f;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
  color: #1e3a5f;
  font-family: inherit;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #065eb5;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
}

.search-input::placeholder {
  color: #cbd5e1;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  pointer-events: none;
}

.role-select {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
  color: #1e3a5f;
  cursor: pointer;
  font-weight: 500;
  font-family: inherit;
  transition: all 0.2s ease;
}

.role-select:focus {
  outline: none;
  border-color: #065eb5;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
}

.search-btn {
  padding: 0.75rem 2rem;
  background: #0284c7;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2);
}

.search-btn:hover {
  background: #0369a1;
  box-shadow: 0 4px 8px rgba(2, 132, 199, 0.3);
  transform: translateY(-1px);
}

.search-btn:active {
  transform: translateY(0);
}

/* Jobs Table Section */
.jobs-table-section {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.table-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #64748b;
}

.items-input {
  width: 50px;
  padding: 0.4rem 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 0.9rem;
  text-align: center;
  font-weight: 600;
  color: #1e3a5f;
}

.items-input:focus {
  outline: none;
  border-color: #065eb5;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.jobs-table {
  width: 100%;
  border-collapse: collapse;
}

.jobs-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #e5e7eb;
}

.jobs-table th {
  padding: 1rem 1.25rem;
  text-align: left;
  font-size: 0.85rem;
  font-weight: 700;
  color: #1e3a5f;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.jobs-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
  transition: background 0.2s ease;
}

.jobs-table tbody tr:hover {
  background: #f9fafb;
}

.jobs-table td {
  padding: 1rem 1.25rem;
  color: #1e3a5f;
  font-weight: 500;
  font-size: 0.9rem;
}

.position-cell,
.skills-cell {
  color: #64748b;
}

.work-mode-badge {
  display: inline-block;
  padding: 0.4rem 0.85rem;
  background: #f0f9ff;
  color: #0284c7;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}

.view-more-link {
  color: #0284c7;
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s ease;
}

.view-more-link:hover {
  color: #0369a1;
  text-decoration: underline;
}

/* Pagination */
.pagination-section {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.pagination-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: center;
}

.pagination-btn {
  min-width: 40px;
  height: 40px;
  padding: 0 0.75rem;
  border: 1px solid #e5e7eb;
  background: white;
  color: #1e3a5f;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(.pagination-dots) {
  border-color: #065eb5;
  color: #065eb5;
  background: #f0f7ff;
}

.pagination-btn.active {
  background: #0284c7;
  color: white;
  border-color: #0284c7;
}

.pagination-dots {
  border: none;
  background: none;
  cursor: default;
  color: #94a3b8;
}

.pagination-dots:hover {
  background: none;
  color: #94a3b8;
}

/* Footer */
.page-footer {
  text-align: center;
  padding: 1.5rem 0;
}

.footer-text {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .search-filter-section {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .search-btn {
    width: 100%;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .job-postings-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1.5rem;
    align-items: flex-start;
  }

  .jobs-table-section {
    padding: 1.5rem;
    overflow-x: auto;
  }

  .jobs-table th,
  .jobs-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.8rem;
  }

  .jobs-table th {
    white-space: nowrap;
  }

  .view-more-link {
    font-size: 0.8rem;
  }

  .pagination-btn {
    min-width: 36px;
    height: 36px;
    font-size: 0.85rem;
    padding: 0 0.5rem;
  }
}

@media (max-width: 480px) {
  .job-postings-page {
    padding: 0.75rem;
  }

  .header-content h1 {
    font-size: 1.5rem;
  }

  .search-filter-section {
    grid-template-columns: 1fr;
  }

  .jobs-table-section {
    padding: 1rem;
  }

  .jobs-table th,
  .jobs-table td {
    padding: 0.5rem 0.25rem;
    font-size: 0.75rem;
  }

  .pagination-info {
    font-size: 0.8rem;
  }
}
</style>
