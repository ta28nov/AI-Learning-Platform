import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'
import { AdminPage } from '../pages/AdminPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Epic E7 — Verify email (no Google API)', () => {
  test('verify email page shows resend form', async ({ page }) => {
    await page.goto('/auth/verify-email')
    await expect(page.getByRole('heading', { name: /Xác nhận tài khoản/i })).toBeVisible()
    await expect(page.getByLabel(/^Email$/i)).toBeVisible()
    await expect(page.getByRole('button', { name: /Gửi lại link xác thực/i })).toBeVisible()
  })
})

test.describe('Epic E8 — Legal pages', () => {
  test('terms page has table of contents and sections', async ({ page }) => {
    await page.goto('/terms')
    await expect(page.getByRole('heading', { name: /Điều khoản sử dụng/i })).toBeVisible()
    await expect(page.getByRole('navigation', { name: /Mục lục/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Chấp nhận điều khoản/i })).toBeVisible()
  })

  test('privacy page loads', async ({ page }) => {
    await page.goto('/privacy')
    await expect(page.getByRole('heading', { name: /Chính sách bảo mật/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Quay lại đăng ký/i })).toBeVisible()
  })
})

test.describe('Epic E4 — Admin create modals', () => {
  test.beforeEach(async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.admin.email, users.admin.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })
  })

  test('create user modal opens with labeled fields', async ({ page }) => {
    const admin = new AdminPage(page)
    await admin.gotoTab('users')
    await page.getByRole('button', { name: /\+ Tạo người dùng/i }).click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.getByRole('heading', { name: /Tạo người dùng/i })).toBeVisible()
    await expect(dialog.getByLabel(/Họ và tên/i)).toBeVisible()
    await expect(dialog.getByLabel(/^Email$/i)).toBeVisible()
    await expect(dialog.getByLabel(/Mật khẩu tạm/i)).toBeVisible()
    await page.getByRole('button', { name: /^Hủy$/i }).click()
  })

  test('create course modal opens with validation fields', async ({ page }) => {
    const admin = new AdminPage(page)
    await admin.gotoTab('courses')
    await page.getByRole('button', { name: /\+ Tạo khóa học/i }).click()
    const dialog = page.getByRole('dialog')
    await expect(dialog.getByRole('heading', { name: /Tạo khóa học/i })).toBeVisible()
    await expect(dialog.getByLabel(/Tiêu đề/i)).toBeVisible()
    await expect(dialog.getByText(/^Mô tả$/i)).toBeVisible()
    await page.getByRole('button', { name: /^Hủy$/i }).click()
  })
})

test.describe('Epic E9 — Search analytics (admin)', () => {
  test('admin sees search analytics panel on search page', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.admin.email, users.admin.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/search?q=python')
    await expect(page.getByText(/Thống kê tìm kiếm \(admin\)/i)).toBeVisible({ timeout: 60_000 })
  })
})
