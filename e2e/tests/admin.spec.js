import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Admin smoke', () => {
  test('admin users tab loads', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.admin.email, users.admin.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/admin/users')
    await expect(page.getByRole('heading', { name: /Admin Console/i })).toBeVisible({ timeout: 30_000 })
    await expect(page.getByText(/Người dùng/i).first()).toBeVisible()
  })
})
