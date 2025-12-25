<template>
  <div class="search-section">
    <div class="search-box">
      <label>Quick search a Candidate</label>
      <div class="search-input-wrapper">
        <input
          type="text"
          placeholder="Enter search word"
          :value="searchQuery"
          @input="$emit('update:searchQuery', $event.target.value)"
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

    <div class="stats-box">
      <div class="stat-number">{{ totalCandidates }}</div>
      <div class="stat-label">Total number of Candidates</div>
    </div>

    <div class="filter-section">
      <label>Filter by Role</label>
      <select
        :value="selectedRole"
        @change="$emit('update:selectedRole', $event.target.value)"
        class="role-select"
      >
        <option value="">All Roles</option>
        <option value="Developer">Developer</option>
        <option value="Designer">Designer</option>
        <option value="Manager">Manager</option>
      </select>
    </div>
  </div>
</template>

<script setup>
defineProps({
  searchQuery: String,
  selectedRole: String,
  totalCandidates: Number,
})

defineEmits(['update:searchQuery', 'update:selectedRole'])
</script>

<style scoped>
.search-section {
  display: grid;
  grid-template-columns: 1fr 250px 200px;
  gap: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.search-box,
.stats-box,
.filter-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.search-box label,
.filter-section label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e3a5f;
}

.search-input-wrapper {
  position: relative;
}

.search-input-wrapper input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  background: #f8f9fa;
}

.search-input-wrapper input:focus {
  border-color: #065eb5;
  background: white;
  box-shadow: 0 0 0 3px rgba(6, 94, 181, 0.1);
  outline: none;
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  pointer-events: none;
}

.stats-box {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e5e7eb;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #065eb5;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 500;
}

.role-select {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #1e3a5f;
  cursor: pointer;
  font-weight: 500;
}

.role-select:focus {
  border-color: #065eb5;
  outline: none;
}

@media (max-width: 1200px) {
  .search-section {
    grid-template-columns: 1fr 200px;
  }

  .filter-section {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .search-section {
    grid-template-columns: 1fr;
  }
}
</style>
