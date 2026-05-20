import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Instructor smoke', () => {
  test.beforeEach(async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.instructor.email, users.instructor.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })
  })

  test('instructor dashboard and classes list', async ({ page }) => {
    await page.goto('/dashboard/instructor')
    await expect(page.getByRole('button', { name: /Quản lý lớp học/i })).toBeVisible({ timeout: 30_000 })

    await page.goto('/dashboard/instructor/classes')
    await expect(page.getByRole('heading', { name: /Lớp học của tôi/i })).toBeVisible({ timeout: 30_000 })
  })

  test('instructor creates class and sees invite code', async ({ page }) => {
    const className = `E2E Class ${Date.now()}`

    await page.goto('/dashboard/instructor/classes/create')
    await expect(page.getByRole('heading', { name: /Tạo lớp học mới/i })).toBeVisible({ timeout: 30_000 })

    await page.getByPlaceholder('VD: Lớp Python cơ bản — K1').fill(className)
    await page.getByPlaceholder('Mô tả ngắn về lớp học').fill('E2E smoke class')

    const courseSelect = page.locator('select.cc-input').first()
    await expect(courseSelect.locator('option').first()).not.toHaveText(/Đang tải/, { timeout: 30_000 })

    const optionCount = await courseSelect.locator('option').count()
    test.skip(
      optionCount < 2,
      'Không có khóa học public — chạy: cd BE && python -m scripts.init_data',
    )

    await courseSelect.selectOption({ index: 1 })

    const today = new Date().toISOString().slice(0, 10)
    const nextMonth = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
    await page.locator('input[type="date"]').nth(0).fill(today)
    await page.locator('input[type="date"]').nth(1).fill(nextMonth)
    await page.locator('input[type="number"]').fill('30')

    await page.getByRole('button', { name: /^Tạo lớp học$/i }).click()
    await page.waitForURL(/\/dashboard\/instructor\/classes\/[^/]+$/, { timeout: 60_000 })

    await expect(page.getByText(/Mã mời lớp/i)).toBeVisible({ timeout: 15_000 })
    await expect(page.locator('.cld-invite__code')).not.toBeEmpty()
    await expect(page.getByRole('heading', { name: className })).toBeVisible({ timeout: 15_000 })
  })

  test('instructor analytics page loads without error', async ({ page }) => {
    await page.goto('/dashboard/instructor/analytics')
    await expect(page.getByRole('heading', { name: /Analytics giảng viên/i })).toBeVisible({
      timeout: 60_000,
    })
    await expect(page.getByText(/Lỗi tải dữ liệu/i)).not.toBeVisible()
    await expect(page.getByText(/Lớp học/i).first()).toBeVisible({ timeout: 30_000 })
  })

  test('instructor quiz list and create empty state', async ({ page }) => {
    await page.goto('/dashboard/instructor/quizzes')
    await expect(page.getByRole('heading', { name: /Quản lý Quiz/i })).toBeVisible({
      timeout: 30_000,
    })
    await expect(page.getByRole('button', { name: /Tạo quiz từ bài học/i })).toBeVisible()

    await page.goto('/dashboard/instructor/quizzes/create')
    await expect(page.getByRole('heading', { name: /Tạo quiz mới/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Chưa chọn bài học/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /Quay lại danh sách quiz/i })).toBeVisible()
  })
})
