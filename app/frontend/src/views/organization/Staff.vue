<template>
  <div class="hr-page">
    <div class="hr-section">
      <div class="hr-header">
        <h2 class="hr-title">Human Resources</h2>
        <button class="add-new-hr-btn" @click="openAddHRModal">Add New HR</button>
      </div>

      <!-- DataTable Component -->
      <DataTable :columns="tableColumns" :data="staffTableData" row-key="id" :items-per-page="10">
        <!-- Custom cell for S/N -->
        <template #cell-sn="{ index }">
          {{ String(index + 1).padStart(2, '0') }}
        </template>

        <!-- Custom cell for Action -->
        <template #cell-action="{ row }">
          <router-link :to="`/organisation/staff/edit/${row.id}`" class="view-more-link">
            View more
          </router-link>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import DataTable from '@/components/DataTable.vue'
import api from '@/services/api'

const router = useRouter()
const store = useStore()

// Table columns
const tableColumns = ref([
  { key: 'sn', label: 'S/N' },
  { key: 'firstName', label: 'First Name' },
  { key: 'lastName', label: 'Last Name' },
  { key: 'gender', label: 'Gender' },
  { key: 'staffId', label: 'Staff ID' },
  { key: 'phone', label: 'Phone Number' },
  { key: 'action', label: 'Action' },
])

// Staff table data
const staffTableData = ref([])

const loadHRs = async () => {
  try {
    const user = store.getters['auth/currentUser']
    const companyId = user?.company_id
    
    if (!companyId) {
      console.error('Company ID not found')
      staffTableData.value = []
      return
    }

    console.log('Loading HRs for company:', companyId)
    const res = await api.get('/hr')
    console.log('HR API response:', res.data)
    const allHRs = Array.isArray(res.data) ? res.data : []
    
    // Filter HRs by company_id
    const companyHRs = allHRs.filter(hr => 
      (hr.company_id || hr.companyId) === companyId
    )
    
    console.log('Filtered HRs for company:', companyHRs)
    
    // Transform to match table structure
    staffTableData.value = companyHRs.map(hr => ({
      id: hr.hr_id || hr.id,
      firstName: hr.first_name || '',
      lastName: hr.last_name || '',
      gender: hr.gender || '',
      staffId: hr.staff_id || '',
      phone: hr.contact_phone || hr.phone || ''
    }))
    
    console.log('Final staffTableData:', staffTableData.value)
  } catch (error) {
    console.error('Failed to load HRs:', error)
    staffTableData.value = []
  }
}

onMounted(() => {
  loadHRs()
})

const openAddHRModal = () => {
  router.push('/organisation/staff/add')
}
</script>

<style scoped>
.hr-page {
  padding: 2rem;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

/* HR Section */
.hr-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.hr-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.hr-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.add-new-hr-btn {
  padding: 0.75rem 1.5rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.add-new-hr-btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

.view-more-link {
  color: #065eb5;
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s;
}

.view-more-link:hover {
  color: #054a94;
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
  .hr-page {
    padding: 1rem;
  }

  .hr-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
