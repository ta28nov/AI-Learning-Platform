import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'
import { AdminPage } from '../pages/AdminPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Admin smoke', () => {
  test.beforeEach(async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.admin.email, users.admin.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })
  })

  test('admin users tab loads table', async ({ page }) => {
    const admin = new AdminPage(page)
    await admin.gotoTab('users')
    await expect(
      page.getByLabel('Admin navigation').getByRole('link', { name: 'Người dùng' }),
    ).toHaveAttribute('aria-current', 'page')
    await expect(page.locator('.adm-table').first()).toBeVisible({ timeout: 30_000 })
  })

  test('admin courses tab loads', async ({ page }) => {
    const admin = new AdminPage(page)
    await admin.gotoTab('courses')
    await expect(
      page.getByLabel('Admin navigation').getByRole('link', { name: 'Khóa học' }),
    ).toHaveAttribute('aria-current', 'page')
    await expect(page.locator('.adm-table').first()).toBeVisible({ timeout: 30_000 })
  })

  test('admin classes tab loads', async ({ page }) => {
    const admin = new AdminPage(page)
    await admin.gotoTab('classes')
    await expect(
      page.getByLabel('Admin navigation').getByRole('link', { name: 'Lớp học' }),
    ).toHaveAttribute('aria-current', 'page')
    await expect(page.locator('.adm-table').first()).toBeVisible({ timeout: 30_000 })
  })

  test('admin analytics tab loads', async ({ page }) => {
    const admin = new AdminPage(page)
    await admin.gotoTab('analytics')
    await expect(
      page.getByRole('heading', { name: /Sức khỏe hệ thống|Tăng trưởng người dùng/i }).first(),
    ).toBeVisible({ timeout: 90_000 })
  })
})
