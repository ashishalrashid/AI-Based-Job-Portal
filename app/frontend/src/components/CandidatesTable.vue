<template>
  <div class="table-container">
    <div class="table-header">
      <h2>All Candidates</h2>
      <div class="table-controls">
        <span class="showing-text">Showing</span>
        <select v-model="itemsPerPage" class="items-select">
          <option value="12">12</option>
          <option value="25">25</option>
          <option value="50">50</option>
        </select>
        <span class="items-info">per page</span>
      </div>
    </div>

    <div class="filters-row">
      <select v-model="localSelectedRole" @change="handleRoleFilter" class="filter-select">
        <option value="">All Roles</option>
        <option value="Developer">Developer</option>
        <option value="Designer">Designer</option>
        <option value="Manager">Manager</option>
      </select>
    </div>

    <div class="table-wrapper">
      <table class="candidates-table">
        <thead>
          <tr>
            <th>S/N</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Gender</th>
            <th>Role</th>
            <th>AI Match Score</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(candidate, index) in paginatedCandidates" :key="candidate.id">
            <td>
              {{ String((currentPage - 1) * parseInt(itemsPerPage) + index + 1).padStart(2, '0') }}
            </td>
            <td>{{ candidate.firstName }}</td>
            <td>{{ candidate.lastName }}</td>
            <td>{{ candidate.gender }}</td>
            <td>{{ candidate.role }}</td>
            <td>
              <span
                class="score-badge"
                :class="{ high: candidate.matchScore >= 70, low: candidate.matchScore < 70 }"
              >
                {{ String(candidate.matchScore).padStart(2, '0') }}
              </span>
            </td>
            <td>
              <button class="view-more-btn" @click="$emit('viewCandidate', candidate.id)">
                View more
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button
        v-for="page in paginationPages"
        :key="page"
        @click="currentPage = page"
        :class="['pagination-btn', { active: currentPage === page }]"
      >
        {{ page }}
      </button>
      <button v-if="totalPages > 5" class="pagination-btn">>></button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  candidates: Array,
  selectedRole: String,
  searchQuery: String,
})

const emit = defineEmits(['viewCandidate'])

const itemsPerPage = ref('12')
const currentPage = ref(1)
const localSelectedRole = ref(props.selectedRole)

const filteredCandidates = computed(() => {
  return props.candidates.filter((candidate) => {
    const matchesSearch =
      candidate.firstName.toLowerCase().includes(props.searchQuery.toLowerCase()) ||
      candidate.lastName.toLowerCase().includes(props.searchQuery.toLowerCase())

    const matchesRole = !localSelectedRole.value || candidate.role === localSelectedRole.value

    return matchesSearch && matchesRole
  })
})

const totalPages = computed(() => {
  return Math.ceil(filteredCandidates.value.length / parseInt(itemsPerPage.value))
})

const paginatedCandidates = computed(() => {
  const start = (currentPage.value - 1) * parseInt(itemsPerPage.value)
  const end = start + parseInt(itemsPerPage.value)
  return filteredCandidates.value.slice(start, end)
})

const paginationPages = computed(() => {
  const pages = []
  const maxVisible = 5
  const half = Math.floor(maxVisible / 2)

  let start = Math.max(1, currentPage.value - half)
  let end = Math.min(totalPages.value, start + maxVisible - 1)

  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

const handleRoleFilter = () => {
  currentPage.value = 1
}

watch(
  () => props.searchQuery,
  () => {
    currentPage.value = 1
  },
)
</script>

<style scoped>
.table-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.table-header h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.table-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8f9fa;
  padding: 0.5rem 1rem;
  border-radius: 6px;
}

.items-select {
  padding: 0.4rem 0.6rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
  color: #1e3a5f;
  font-weight: 600;
  cursor: pointer;
}

.showing-text,
.items-info {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 500;
}

.filters-row {
  margin-bottom: 1.5rem;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #1e3a5f;
  cursor: pointer;
}

.table-wrapper {
  overflow-x: auto;
  margin-bottom: 2rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.candidates-table {
  width: 100%;
  border-collapse: collapse;
}

.candidates-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #e5e7eb;
}

.candidates-table th {
  padding: 1rem;
  text-align: left;
  font-size: 0.85rem;
  font-weight: 700;
  color: #1e3a5f;
  text-transform: uppercase;
}

.candidates-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
}

.candidates-table tbody tr:hover {
  background: #f8f9fa;
}

.candidates-table td {
  padding: 1rem;
  color: #1e3a5f;
  font-weight: 500;
}

.score-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 700;
  background: #fee2e2;
  color: #dc2626;
}

.score-badge.high {
  background: #dcfce7;
  color: #16a34a;
}

.view-more-btn {
  background: none;
  border: none;
  color: #065eb5;
  cursor: pointer;
  font-weight: 600;
  padding: 0;
  font-size: 0.95rem;
}

.view-more-btn:hover {
  color: #054a94;
  text-decoration: underline;
}

.pagination {
  display: flex;
  gap: 0.5rem;
}

.pagination-btn {
  min-width: 40px;
  height: 40px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #1e3a5f;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.pagination-btn:hover {
  border-color: #065eb5;
  color: #065eb5;
}

.pagination-btn.active {
  background: #6366f1;
  color: white;
  border-color: #6366f1;
}

@media (max-width: 768px) {
  .candidates-table th,
  .candidates-table td {
    padding: 0.75rem 0.5rem;
    font-size: 0.85rem;
  }
}
</style>
