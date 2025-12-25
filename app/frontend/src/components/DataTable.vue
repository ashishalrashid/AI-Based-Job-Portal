<template>
  <div class="table-container">
    <div class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="column in columns" :key="column.key" class="table-header">
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in paginatedData" :key="row[rowKey] || index" class="table-row">
            <td
              v-for="column in columns"
              :key="column.key"
              class="table-cell"
              :class="{ 'table-cell-main': column.key === 'role' }"
            >
              <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]" :index="index">
                {{ row[column.key] }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button
        v-for="page in totalPages"
        :key="page"
        @click="currentPage = page"
        :class="['pagination-btn', { active: currentPage === page }]"
      >
        {{ page }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
  },
  data: {
    type: Array,
    required: true,
  },
  rowKey: {
    type: String,
    default: 'id',
  },
  itemsPerPage: {
    type: Number,
    default: 12,
  },
})

const currentPage = ref(1)

const totalPages = computed(() => Math.ceil(props.data.length / props.itemsPerPage))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * props.itemsPerPage
  const end = start + props.itemsPerPage
  return props.data.slice(start, end)
})
</script>

<style scoped>
.table-container {
  width: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.table-header {
  padding: 1rem;
  text-align: left;
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
  transition: background 0.2s ease;
}

.data-table tbody tr:hover {
  background: #f9fafb;
}

.table-cell {
  padding: 1.25rem;
  color: #475569;
  font-weight: 500;
  font-size: 0.9rem;
}

.table-cell-main {
  font-weight: 600;
  color: #1e3a5f;
}

.pagination {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  padding: 1rem;
  flex-wrap: wrap;
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
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.pagination-btn:hover {
  border-color: #f59e0b;
  color: #f59e0b;
}

.pagination-btn.active {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

@media (max-width: 768px) {
  .table-header,
  .table-cell {
    padding: 0.75rem 0.5rem;
    font-size: 0.85rem;
  }

  .pagination-btn {
    min-width: 36px;
    height: 36px;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .table-header,
  .table-cell {
    padding: 0.6rem 0.4rem;
    font-size: 0.8rem;
  }

  .pagination-btn {
    min-width: 32px;
    height: 32px;
    font-size: 0.8rem;
  }
}
</style>
