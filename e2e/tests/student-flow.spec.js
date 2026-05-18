import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'
import { DashboardPage } from '../pages/DashboardPage.js'
import { AssessmentPage } from '../pages/AssessmentPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Student learning flow', () => {
  test.beforeEach(async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await new DashboardPage(page).expectLoaded()
  })

  test('dashboard loads for student', async ({ page }) => {
    await expect(page.getByRole('banner')).toBeVisible()
  })

  test('assessment generate navigates to quiz UI', async ({ page }) => {
    test.setTimeout(180_000)
    const assessment = new AssessmentPage(page)
    await assessment.startBeginnerPythonAssessment()
    await expect(page).toHaveURL(/\/dashboard\/assessment\/quiz/)
  })
})
