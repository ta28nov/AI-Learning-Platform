import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Personal courses smoke', () => {
  test('student personal courses page loads', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/personal-courses')
    await expect(page.getByRole('heading', { level: 1, name: 'Khóa học cá nhân' })).toBeVisible({
      timeout: 30_000,
    })
    await expect(page.getByRole('button', { name: 'Tạo bằng AI' })).toBeVisible()
    await expect(page.getByRole('button', { name: '+ Tạo thủ công' })).toBeVisible()
  })

  test('instructor personal courses page loads', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.instructor.email, users.instructor.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/personal-courses')
    await expect(page.getByRole('heading', { level: 1, name: 'Khóa học cá nhân' })).toBeVisible({
      timeout: 30_000,
    })
    await expect(page.getByRole('button', { name: 'Tạo bằng AI' })).toBeVisible()
  })

  test('AI prompt modal — template fills textarea', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })
    await page.goto('/dashboard/personal-courses')

    await page.getByRole('button', { name: 'Tạo bằng AI' }).click()
    await expect(page.getByRole('heading', { name: 'Tạo khóa học bằng AI' })).toBeVisible()
    await page.getByRole('button', { name: 'Mẫu 1' }).click()
    const textarea = page.locator('.personal-courses-prompt__textarea')
    await expect(textarea).not.toHaveValue('')
    await expect(textarea).toHaveValue(/Python/i)
    await page.getByRole('button', { name: 'Hủy' }).click()
    await expect(page.getByRole('heading', { name: 'Tạo khóa học bằng AI' })).not.toBeVisible()
  })
})

const hasGemini = Boolean(process.env.GOOGLE_API_KEY && process.env.GOOGLE_API_KEY !== 'fake-key-not-used-in-tests')

test.describe('Personal course from-prompt (live AI)', () => {
  test('student creates course from prompt', async ({ page }) => {
    test.skip(!hasGemini, 'Requires GOOGLE_API_KEY for POST /courses/from-prompt')
    test.setTimeout(180_000)

    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })
    await page.goto('/dashboard/personal-courses')

    await page.getByRole('button', { name: 'Tạo bằng AI' }).click()
    await page.getByRole('button', { name: 'Mẫu 1' }).click()
    await page.getByRole('button', { name: 'Tạo khóa học' }).click()
    await expect(page).toHaveURL(/\/dashboard\/personal-courses\/[^/]+\/edit/, { timeout: 120_000 })
  })
})
