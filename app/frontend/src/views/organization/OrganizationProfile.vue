<template>
  <div class="organization-profile page-container">
    <header class="profile-header">
      <h1 class="page-title">Organization Profile</h1>
      <button v-if="!isEditMode" @click="enableEdit" class="btn-primary edit-btn">
        Edit Profile
      </button>
      <div v-else class="edit-actions">
        <button @click="saveProfile" class="btn-primary">Save Changes</button>
        <button @click="cancelEdit" class="btn-secondary">Cancel</button>
      </div>
    </header>

    <section class="profile-section">
      <div v-if="loading" class="loading">Loading profile...</div>
      <div v-else>
        <div class="logo-upload-container" v-if="logoPreview || profileData.logoUrl">
          <img :src="logoPreview || profileData.logoUrl" alt="Company Logo" class="company-logo" />
        </div>

        <div v-if="isEditMode" class="form-group">
          <label for="logoUpload" class="form-label">Upload Company Logo</label>
          <input id="logoUpload" type="file" accept="image/*" @change="onLogoSelected" />
          <p class="hint-text">JPG, PNG (Max 5MB)</p>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label" for="orgName">Organization Name</label>
        <input
          id="orgName"
          type="text"
          v-model="profileData.name"
          :disabled="!isEditMode"
          class="form-input"
          placeholder="Enter organization name"
        />
      </div>

      <div class="form-group">
        <label class="form-label" for="orgCin">CIN</label>
        <input
          id="orgCin"
          type="text"
          v-model="profileData.cin"
          :disabled="!isEditMode"
          class="form-input"
          placeholder="Enter Corporate Identification Number"
        />
      </div>

      <div class="form-group">
        <label class="form-label" for="orgEmail">Email</label>
        <input
          id="orgEmail"
          type="email"
          v-model="profileData.email"
          :disabled="!isEditMode"
          class="form-input"
          placeholder="Enter email"
        />
      </div>

      <div class="form-group">
        <label class="form-label" for="orgPhone">Phone</label>
        <input
          id="orgPhone"
          type="tel"
          v-model="profileData.phone"
          :disabled="!isEditMode"
          class="form-input"
          placeholder="Enter phone number"
        />
      </div>

      <div class="form-group">
        <label class="form-label" for="orgAddress">Address</label>
        <textarea
          id="orgAddress"
          v-model="profileData.address"
          :disabled="!isEditMode"
          rows="4"
          class="form-textarea"
          placeholder="Enter address"
        ></textarea>
      </div>

      <div class="form-group">
        <label class="form-label" for="orgDescription">Description</label>
        <textarea
          id="orgDescription"
          v-model="profileData.description"
          :disabled="!isEditMode"
          rows="6"
          class="form-textarea"
          placeholder="Enter organization description"
        ></textarea>
      </div>

      <div v-if="isEditMode" class="password-change-section">
        <h2 class="section-title">Change Password</h2>

        <div class="form-group">
          <label for="oldPassword" class="form-label">Old Password</label>
          <input
            id="oldPassword"
            type="password"
            v-model="passwords.oldPassword"
            class="form-input"
            placeholder="Enter old password"
          />
        </div>

        <div class="form-group">
          <label for="newPassword" class="form-label">New Password</label>
          <input
            id="newPassword"
            type="password"
            v-model="passwords.newPassword"
            class="form-input"
            placeholder="Enter new password"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword" class="form-label">Confirm New Password</label>
          <input
            id="confirmPassword"
            type="password"
            v-model="passwords.confirmPassword"
            class="form-input"
            placeholder="Confirm new password"
          />
        </div>

        <p v-if="passwordError" class="error-text">{{ passwordError }}</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

const isEditMode = ref(false)
const logoPreview = ref(null)
const logoFile = ref(null)
const store = useStore()
const loading = ref(false)

// Get company_id from user context
const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
const companyId = currentUser?.company_id

const profileData = ref({
  logoUrl: '',
  name: '',
  cin: '',
  email: '',
  phone: '',
  address: '',
  description: '',
})

const originalData = ref({})

const passwords = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const passwordError = ref('')

// Fetch company profile
const fetchProfile = async () => {
  if (!companyId) {
    console.error('Company ID not found')
    return
  }

  loading.value = true
  try {
    const res = await api.get(`/company/${companyId}`)
    const company = res.data

    profileData.value = {
      logoUrl: company.logo_url || '',
      name: company.company_name || '',
      cin: company.cin || '',
      email: company.company_email || '',
      phone: company.contact_number || '',
      address: company.location || '',
      description: company.description || '',
    }

    originalData.value = JSON.parse(JSON.stringify(profileData.value))
  } catch (err) {
    console.error('Failed to fetch company profile:', err)
    alert('Failed to load company profile')
  } finally {
    loading.value = false
  }
}

function enableEdit() {
  isEditMode.value = true
  passwordError.value = ''
  logoPreview.value = null
  logoFile.value = null
  originalData.value = JSON.parse(JSON.stringify(profileData.value))
}

function cancelEdit() {
  isEditMode.value = false
  passwordError.value = ''
  logoPreview.value = null
  logoFile.value = null
  profileData.value = JSON.parse(JSON.stringify(originalData.value))
}

function onLogoSelected(event) {
  const file = event.target.files[0]
  if (!file) return
  
  // Validate file type
  if (!file.type.startsWith('image/')) {
    alert('Please select a valid image file')
    return
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    alert('File size must be less than 5MB')
    return
  }

  // Store file for upload
  logoFile.value = file

  // Preview the logo
  const reader = new FileReader()
  reader.onload = (e) => {
    logoPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

function validatePasswords() {
  if (
    !passwords.value.oldPassword &&
    (passwords.value.newPassword || passwords.value.confirmPassword)
  ) {
    passwordError.value = 'Please enter your old password to change password.'
    return false
  }
  if (passwords.value.newPassword !== passwords.value.confirmPassword) {
    passwordError.value = 'New password and confirm password do not match.'
    return false
  }
  if (passwords.value.newPassword && passwords.value.newPassword.length < 6) {
    passwordError.value = 'New password must be at least 6 characters.'
    return false
  }
  passwordError.value = ''
  return true
}

async function saveProfile() {
  if (!validatePasswords()) return

  if (!companyId) {
    alert('Company ID not found')
    return
  }

  loading.value = true
  try {
    const formData = new FormData()
    
    // Add company fields
    if (profileData.value.name) {
      formData.append('company_name', profileData.value.name)
    }
    if (profileData.value.email) {
      formData.append('company_email', profileData.value.email)
    }
    if (profileData.value.phone) {
      formData.append('contact_number', profileData.value.phone)
    }
    if (profileData.value.address) {
      formData.append('location', profileData.value.address)
    }
    if (profileData.value.description) {
      formData.append('description', profileData.value.description)
    }

    // Add logo if uploaded
    if (logoFile.value instanceof File) {
      formData.append('logo', logoFile.value)
    }

    await api.put(`/company/${companyId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    // Handle password update if provided
    if (passwords.value.newPassword && passwords.value.oldPassword) {
      // Note: Password update should be handled via auth endpoint
      // For now, we'll just show a message
      console.log('Password update should be handled via auth endpoint')
    }

    alert('Profile updated successfully!')

    passwords.value.oldPassword = ''
    passwords.value.newPassword = ''
    passwords.value.confirmPassword = ''

    isEditMode.value = false
    logoPreview.value = null
    logoFile.value = null

    // Reload profile
    await fetchProfile()
  } catch (err) {
    console.error('Failed to save profile:', err)
    alert(err.response?.data?.message || 'Failed to update profile')
  } finally {
    loading.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.page-container {
  padding: 2rem;
  background: #f5f7fa;
  min-height: 100vh;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0;
}

.edit-btn,
.btn-primary,
.btn-secondary {
  cursor: pointer;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.95rem;
  padding: 0.75rem 1.5rem;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.edit-btn,
.btn-primary {
  background: #6366f1;
  color: white;
}

.edit-btn:hover,
.btn-primary:hover {
  background: #4f46e5;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
  background: #e5e7eb;
  color: #1e3a5f;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.profile-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  max-width: 600px;
}

.logo-upload-container {
  width: 150px;
  height: 150px;
  background: #f0f4ff;
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(101, 103, 205, 0.15);
}

.company-logo {
  max-width: 130px;
  max-height: 130px;
  border-radius: 16px;
  object-fit: contain;
}

.form-group {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #475569;
}

.form-input,
.form-textarea {
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  font-family: inherit;
  font-size: 0.95rem;
  color: #1e3a5f;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  outline: none;
}

.password-change-section {
  margin-top: 2rem;
  border-top: 1px solid #e2e8f0;
  padding-top: 1.5rem;
}

.section-title {
  font-weight: 700;
  font-size: 1.25rem;
  color: #1e3a5f;
  margin-bottom: 1rem;
}

.error-text {
  color: #dc2626;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.hint-text {
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.25rem;
}
</style>
