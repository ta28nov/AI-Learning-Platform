import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Instructor smoke', () => {
  test('instructor dashboard and classes', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.instructor.email, users.instructor.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/instructor')
    await expect(page.getByRole('button', { name: /Quản lý lớp học/i })).toBeVisible({ timeout: 30_000 })

    await page.goto('/dashboard/instructor/classes')
    await expect(page.getByRole('heading', { name: /Lớp học của tôi/i })).toBeVisible({ timeout: 30_000 })
  })
})
