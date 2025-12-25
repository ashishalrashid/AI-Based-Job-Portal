<template>
  <div class="create-job-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="icon-wrapper">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
          </svg>
        </div>
        <div class="header-info">
          <h1 class="page-title">Job Openings</h1>
          <p class="page-subtitle">Create and publish new job opportunities</p>
        </div>
      </div>
    </div>

    <!-- Back Button -->
    <router-link to="/hr/dashboard" class="back-button">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      <span>Back to Dashboard</span>
    </router-link>

    <!-- Form Container -->
    <div class="form-wrapper">
      <div class="form-container">
        <h2 class="form-title">Create New Opening</h2>

        <!-- Form Grid -->
        <div class="form-grid">
          <!-- Title -->
          <div class="form-group">
            <label for="title" class="form-label">
              Job Title <span class="required">*</span>
            </label>
            <input
              id="title"
              type="text"
              v-model="formData.title"
              class="form-input"
              placeholder="e.g., Senior Software Engineer"
            />
          </div>

          <!-- Level -->
          <div class="form-group">
            <label for="level" class="form-label">
              Level <span class="required">*</span>
            </label>
            <select id="level" v-model="formData.level" class="form-input">
              <option value="">Select level</option>
              <option value="Junior">Junior</option>
              <option value="Mid-level">Mid-level</option>
              <option value="Senior">Senior</option>
              <option value="Lead">Lead</option>
              <option value="Manager">Manager</option>
            </select>
          </div>

          <!-- Employment Type -->
          <div class="form-group">
            <label for="employmentType" class="form-label">
              Employment Type <span class="required">*</span>
            </label>
            <select
              id="employmentType"
              v-model="formData.employmentType"
              class="form-input"
            >
              <option value="">Select type</option>
              <option value="Full-time">Full-time</option>
              <option value="Part-time">Part-time</option>
              <option value="Contract">Contract</option>
              <option value="Intern">Internship</option>
            </select>
          </div>

          <!-- Required Education -->
          <div class="form-group">
            <label for="requiredEducation" class="form-label">
              Required Education
            </label>
            <select
              id="requiredEducation"
              v-model="formData.requiredEducation"
              class="form-input"
            >
              <option value="">Select education</option>
              <option value="BTech">B.Tech</option>
              <option value="BSc">B.Sc</option>
              <option value="MTech">M.Tech</option>
              <option value="MSc">M.Sc</option>
              <option value="MBA">MBA</option>
              <option value="MCA">MCA</option>
              <option value="Any Graduate">Any Graduate</option>
            </select>
          </div>

          <!-- Location -->
          <div class="form-group">
            <label for="location" class="form-label">
              Location <span class="required">*</span>
            </label>
            <input
              type="text"
              id="location"
              v-model="formData.location"
              placeholder="e.g., Bangalore, Remote"
              class="form-input"
            />
          </div>

          <!-- Notice Period -->
          <div class="form-group">
            <label for="noticePeriod" class="form-label">Notice Period</label>
            <input
              type="text"
              id="noticePeriod"
              v-model="formData.noticePeriod"
              placeholder="e.g., Immediate, 1 Month, 2 Months"
              class="form-input"
            />
          </div>

          <!-- Basic Salary -->
          <div class="form-group">
            <label for="salary" class="form-label">
              Annual Salary (₹) <span class="required">*</span>
            </label>
            <input
              type="number"
              id="salary"
              v-model.number="formData.salary"
              placeholder="e.g., 1200000"
              class="form-input"
              min="0"
            />
          </div>

          <!-- Experience -->
          <div class="form-group">
            <label for="experience" class="form-label">
              Required Experience (Years)
            </label>
            <input
              type="text"
              id="experience"
              v-model="formData.experience"
              placeholder="e.g., 3-5 or 0-2"
              class="form-input"
            />
          </div>

          <!-- Number of Openings -->
          <div class="form-group">
            <label for="openings" class="form-label">
              Number of Openings <span class="required">*</span>
            </label>
            <input
              id="openings"
              type="number"
              min="1"
              v-model.number="formData.openings"
              placeholder="e.g., 3"
              class="form-input"
            />
          </div>

          <!-- Duration (for Intern/Contract only) -->
          <div
            class="form-group"
            v-if="['Intern', 'Contract'].includes(formData.employmentType)"
          >
            <label for="duration" class="form-label">
              Duration <span class="required">*</span>
            </label>
            <input
              type="text"
              id="duration"
              v-model="formData.duration"
              placeholder="e.g., 3 Months, 6 Months, 1 Year"
              class="form-input"
            />
          </div>

          <!-- Required Skills -->
          <div class="form-group full-width">
            <label for="requiredSkillInput" class="form-label">
              Required Skills <span class="required">*</span>
            </label>
            <input
              id="requiredSkillInput"
              ref="requiredSkillInput"
              type="text"
              class="form-input"
              placeholder="Type skills (press Enter) or paste comma-separated: JavaScript, React, Node.js"
              @keyup.enter="addRequiredSkill"
            />
            <div class="skills-container" v-if="formData.requiredSkills.length > 0">
              <span
                v-for="skill in formData.requiredSkills"
                :key="skill"
                class="skill-tag"
              >
                {{ skill }}
                <button
                  type="button"
                  class="remove-skill"
                  @click="removeRequiredSkill(skill)"
                  aria-label="Remove skill"
                >
                  ×
                </button>
              </span>
            </div>
            <small class="form-hint">
              Press Enter after each skill OR paste comma-separated skills
            </small>
          </div>

          <!-- Additional Skills -->
          <div class="form-group full-width">
            <label for="additionalSkillInput" class="form-label">
              Additional Skills (Optional)
            </label>
            <input
              id="additionalSkillInput"
              ref="additionalSkillInput"
              type="text"
              class="form-input"
              placeholder="Type skills (press Enter) or paste comma-separated: Leadership, Agile, Communication"
              @keyup.enter="addAdditionalSkill"
            />
            <div class="skills-container" v-if="formData.additionalSkills.length > 0">
              <span
                v-for="skill in formData.additionalSkills"
                :key="skill"
                class="skill-tag secondary"
              >
                {{ skill }}
                <button
                  type="button"
                  class="remove-skill"
                  @click="removeAdditionalSkill(skill)"
                  aria-label="Remove skill"
                >
                  ×
                </button>
              </span>
            </div>
            <small class="form-hint">
              Press Enter after each skill OR paste comma-separated skills
            </small>
          </div>
        </div>

        <!-- Additional Context for AI -->
        <div class="form-group full-width">
          <label for="aiContext" class="form-label">
            Additional Context for AI Resume Matching
          </label>
          <textarea
            id="aiContext"
            v-model="formData.aiContext"
            placeholder="Add any additional details about the role, team culture, or specific requirements that will help in candidate evaluation..."
            class="form-textarea"
            rows="4"
          ></textarea>
          <small class="form-hint">
            This information will be used by AI to better match candidates
          </small>
        </div>

        <!-- Job Description Upload -->
        <div class="form-group full-width">
          <label class="form-label">
            Job Description <span class="required">*</span>
          </label>

          <div class="jd-options">
            <label class="jd-option">
              <input
                type="radio"
                v-model="formData.jdType"
                value="file"
                class="radio-input"
              />
              <span class="radio-text">Upload PDF</span>
            </label>
            <label class="jd-option">
              <input
                type="radio"
                v-model="formData.jdType"
                value="link"
                class="radio-input"
              />
              <span class="radio-text">Google Drive Link</span>
            </label>
          </div>

          <div class="jd-input">
            <input
              v-if="formData.jdType === 'file'"
              type="file"
              accept=".pdf"
              @change="handlePdfUpload"
              class="form-input file-input"
              ref="fileInput"
            />
            <div v-if="formData.jdType === 'file' && formData.jdFile" class="file-selected">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
              </svg>
              <span>{{ formData.jdFile.name }}</span>
            </div>

            <input
              v-else-if="formData.jdType === 'link'"
              type="url"
              v-model="formData.jdLink"
              placeholder="https://drive.google.com/file/d/..."
              class="form-input"
            />
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="form-actions">
          <button type="button" class="btn-cancel" @click="handleCancel">
            Cancel
          </button>
          <button type="button" class="btn-create" @click="handleCreateJob" :disabled="isSubmitting">
            <svg
              v-if="!isSubmitting"
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
              <polyline points="17 21 17 13 7 13 7 21"></polyline>
              <polyline points="7 3 7 8 15 8"></polyline>
            </svg>
            <span v-if="isSubmitting">Creating...</span>
            <span v-else>Create Job Opening</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useStore } from "vuex"

const router = useRouter()
const store = useStore()

// Refs for inputs
const requiredSkillInput = ref(null)
const additionalSkillInput = ref(null)
const fileInput = ref(null)

// Loading state
const isSubmitting = ref(false)

// Get logged-in HR user
const hrUser = store.getters['auth/currentUser'] || JSON.parse(localStorage.getItem("currentUser") || "null")
const companyId = hrUser?.company_id ?? hrUser?.companyid ?? hrUser?.companyId ?? null
const hrId = hrUser?.hr_id ?? hrUser?.hrid ?? hrUser?.hrId ?? hrUser?.id ?? null

// Form data
const formData = ref({
  title: "",
  level: "",
  employmentType: "",
  requiredEducation: "",
  location: "",
  noticePeriod: "",
  salary: "",
  experience: "",
  openings: 1,
  duration: "",
  requiredSkills: [],
  additionalSkills: [],
  aiContext: "",
  jdType: "file",
  jdFile: null,
  jdLink: ""
})

// Add required skill - supports both Enter key AND comma-separated
const addRequiredSkill = (event) => {
  const input = event.target
  const rawValue = input.value.trim()

  if (!rawValue) return

  // Split by comma and process each skill
  const skills = rawValue
    .split(',')
    .map(s => s.trim())
    .filter(s => s.length > 0)

  let addedCount = 0
  let duplicateCount = 0

  skills.forEach(skill => {
    if (!formData.value.requiredSkills.includes(skill)) {
      formData.value.requiredSkills.push(skill)
      addedCount++
    } else {
      duplicateCount++
    }
  })

  // Clear input
  input.value = ""

  // Optional: Show feedback
  if (duplicateCount > 0) {
    console.log(`${duplicateCount} duplicate skill(s) skipped`)
  }
  if (addedCount > 0) {
    console.log(`${addedCount} skill(s) added`)
  }
}

// Remove required skill
const removeRequiredSkill = (skill) => {
  formData.value.requiredSkills = formData.value.requiredSkills.filter(
    (s) => s !== skill
  )
}

// Add additional skill - supports both Enter key AND comma-separated
const addAdditionalSkill = (event) => {
  const input = event.target
  const rawValue = input.value.trim()

  if (!rawValue) return

  // Split by comma and process each skill
  const skills = rawValue
    .split(',')
    .map(s => s.trim())
    .filter(s => s.length > 0)

  let addedCount = 0
  let duplicateCount = 0

  skills.forEach(skill => {
    if (!formData.value.additionalSkills.includes(skill)) {
      formData.value.additionalSkills.push(skill)
      addedCount++
    } else {
      duplicateCount++
    }
  })

  // Clear input
  input.value = ""

  // Optional: Show feedback
  if (duplicateCount > 0) {
    console.log(`${duplicateCount} duplicate skill(s) skipped`)
  }
  if (addedCount > 0) {
    console.log(`${addedCount} skill(s) added`)
  }
}

// Remove additional skill
const removeAdditionalSkill = (skill) => {
  formData.value.additionalSkills = formData.value.additionalSkills.filter(
    (s) => s !== skill
  )
}

// Handle PDF upload
const handlePdfUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.type !== "application/pdf") {
      alert("Please upload a PDF file")
      event.target.value = ""
      return
    }
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      alert("File size must be less than 10MB")
      event.target.value = ""
      return
    }
    formData.value.jdFile = file
  }
}

// Handle cancel
const handleCancel = () => {
  if (confirm("Are you sure you want to cancel? All unsaved changes will be lost.")) {
    router.push("/hr/dashboard")
  }
}

// Validation helper
const validateForm = () => {
  // Required fields
  if (!formData.value.title.trim()) {
    alert("Please enter a job title")
    return false
  }

  if (!formData.value.level) {
    alert("Please select a job level")
    return false
  }

  if (!formData.value.employmentType) {
    alert("Please select employment type")
    return false
  }

  if (!formData.value.location.trim()) {
    alert("Please enter a location")
    return false
  }

  if (!formData.value.salary || formData.value.salary <= 0) {
    alert("Please enter a valid salary")
    return false
  }

  if (!formData.value.openings || formData.value.openings < 1) {
    alert("Please enter number of openings (at least 1)")
    return false
  }

  // Duration required for Intern/Contract
  if (["Intern", "Contract"].includes(formData.value.employmentType)) {
    if (!formData.value.duration.trim()) {
      alert("Please enter duration for this position")
      return false
    }
  }

  // Required skills
  if (formData.value.requiredSkills.length === 0) {
    alert("Please add at least one required skill")
    return false
  }

  // JD validation
  if (formData.value.jdType === "file" && !formData.value.jdFile) {
    alert("Please upload a job description PDF")
    return false
  }

  if (formData.value.jdType === "link" && !formData.value.jdLink.trim()) {
    alert("Please enter a Google Drive link")
    return false
  }

  return true
}

// Submit job creation
const handleCreateJob = async () => {
  if (!validateForm()) return

  if (!companyId) {
    alert("Company ID missing. Please log out and log back in.")
    return
  }

  if (!hrId) {
    alert("HR ID missing. Please log out and log back in.")
    return
  }

  try {
    isSubmitting.value = true

    const fd = new FormData()

    // Required fields
    fd.append("hr_id", hrId)
    fd.append("company_id", companyId)
    fd.append("job_title", formData.value.title.trim())
    fd.append("level", formData.value.level)
    fd.append("employment_type", formData.value.employmentType)
    fd.append("required_education", formData.value.requiredEducation)
    fd.append("location", formData.value.location.trim())
    fd.append("notice_period", formData.value.noticePeriod.trim())
    fd.append("basic_salary", formData.value.salary)
    fd.append("required_experience", formData.value.experience.trim())
    fd.append("no_of_openings", formData.value.openings)
    fd.append("duration", formData.value.duration.trim())
    fd.append("job_description_ai", formData.value.aiContext.trim())

    // Skills - join arrays with commas
    fd.append("required_skills", formData.value.requiredSkills.join(", "))
    fd.append("additional_skills", formData.value.additionalSkills.join(", "))

    // JD attachment
    if (formData.value.jdType === "file") {
      fd.append("attachment_type", "file")
      fd.append("file", formData.value.jdFile)
    } else {
      fd.append("attachment_type", "gdrive")
      fd.append("attachment_url", formData.value.jdLink.trim())
    }

    await store.dispatch("hr/createJob", fd)

    alert("✅ Job opening created successfully!")
    router.push("/hr/dashboard")
  } catch (err) {
    console.error("Error creating job:", err)

    let errorMsg = "Failed to create job. Please try again."

    if (err.response?.data) {
      if (typeof err.response.data === "string") {
        errorMsg = err.response.data
      } else if (err.response.data.message) {
        errorMsg = err.response.data.message
      } else if (err.response.data.error) {
        errorMsg = err.response.data.error
      }
    }

    alert("❌ " + errorMsg)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.create-job-page {
  padding: 2rem;
  background: #f8fafc;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.page-subtitle {
  font-size: 0.95rem;
  color: #64748b;
  margin: 0;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #6366f1;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 2rem;
  transition: all 0.2s;
  padding: 0.5rem 0;
}

.back-button:hover {
  gap: 0.75rem;
  color: #4f46e5;
}

.form-wrapper {
  display: flex;
  justify-content: center;
}

.form-container {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 4px 12px rgba(0, 0, 0, 0.02);
  width: 100%;
  max-width: 1000px;
  border: 1px solid #e2e8f0;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 2rem 0;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f1f5f9;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.required {
  color: #ef4444;
  font-weight: 700;
}

.form-hint {
  font-size: 0.8rem;
  color: #64748b;
  margin-top: 0.25rem;
  display: block;
}

.form-input,
.form-textarea {
  padding: 0.875rem 1rem;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.95rem;
  background: white;
  color: #1e293b;
  font-family: inherit;
  transition: all 0.2s;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #94a3b8;
}

.form-input:focus,
.form-textarea:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  outline: none;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.file-input {
  cursor: pointer;
}

.file-selected {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f1f5f9;
  border-radius: 8px;
  color: #334155;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.file-selected svg {
  color: #6366f1;
}

.skills-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.skill-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border: 1.5px solid #6366f1;
  color: #4f46e5;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
}

.skill-tag.secondary {
  background: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
}

.skill-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
}

.remove-skill {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.remove-skill:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.jd-options {
  display: flex;
  gap: 1.5rem;
  margin: 0.75rem 0 1rem 0;
}

.jd-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.radio-input {
  cursor: pointer;
  width: 18px;
  height: 18px;
  accent-color: #6366f1;
}

.radio-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: #334155;
  cursor: pointer;
}

.jd-input {
  margin-top: 0.75rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2.5rem;
  padding-top: 2rem;
  border-top: 2px solid #f1f5f9;
}

.btn-cancel,
.btn-create {
  padding: 0.875rem 2rem;
  border: none;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-cancel {
  background: #f1f5f9;
  color: #475569;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.btn-create {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-create:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-create:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .create-job-page {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-container {
    padding: 1.5rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .jd-options {
    flex-direction: column;
    gap: 0.75rem;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .btn-cancel,
  .btn-create {
    width: 100%;
    justify-content: center;
  }
}
</style>

