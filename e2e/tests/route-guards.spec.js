import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Route guards (FE ProtectedRoute)', () => {
  test('student cannot open admin console', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/admin/users')
    await expect(page).toHaveURL(/\/unauthorized/, { timeout: 15_000 })
    await expect(page.getByRole('heading', { name: /Không có quyền truy cập/i })).toBeVisible()
  })

  test('student cannot open instructor dashboard', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/instructor')
    await expect(page).toHaveURL(/\/unauthorized/, { timeout: 15_000 })
  })

  test('instructor cannot open admin console', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.instructor.email, users.instructor.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/admin/courses')
    await expect(page).toHaveURL(/\/unauthorized/, { timeout: 15_000 })
  })

  test('instructor can open personal courses', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.instructor.email, users.instructor.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/personal-courses')
    await expect(page.getByRole('heading', { name: /Khóa học cá nhân/i })).toBeVisible({ timeout: 30_000 })
    await expect(page).not.toHaveURL(/\/unauthorized/)
  })
})

test.describe('Mobile sidebar overlay (FIX-005)', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('overlay opens and closes on backdrop click', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.getByRole('button', { name: 'Mở sidebar' }).click()
    const overlay = page.locator('.sidebar-overlay')
    await expect(overlay).toBeVisible({ timeout: 10_000 })

    await overlay.click({ position: { x: 10, y: 10 } })
    await expect(overlay).toBeHidden({ timeout: 10_000 })
  })
})
