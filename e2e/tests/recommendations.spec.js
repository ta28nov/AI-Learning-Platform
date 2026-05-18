import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'
import { DashboardPage } from '../pages/DashboardPage.js'
import { RecommendationsPage } from '../pages/RecommendationsPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Recommendations', () => {
  test.beforeEach(async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await new DashboardPage(page).expectLoaded()
  })

  test('recommendations page shows list or empty state', async ({ page }) => {
    test.setTimeout(120_000)
    const rec = new RecommendationsPage(page)
    await rec.goto()
    await rec.expectCourseListOrEmpty()
    await expect(rec.heading).toBeVisible()
  })
})
