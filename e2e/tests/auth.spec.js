import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'
import { RegisterPage } from '../pages/RegisterPage.js'
import { DashboardPage } from '../pages/DashboardPage.js'
import { expectAccessTokenInStorage } from '../utils/auth.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Authentication', () => {
  test('register then login', async ({ page }) => {
    const email = `e2e-${Date.now()}@example.com`
    const register = new RegisterPage(page)
    await register.register({
      fullName: users.register.fullName,
      email,
      password: users.register.password,
    })
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 15_000 })

    const login = new LoginPage(page)
    await login.login(email, users.register.password)
    await new DashboardPage(page).expectLoaded()
    await expectAccessTokenInStorage(page)
  })

  test('login with seed student and JWT persists after reload', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await new DashboardPage(page).expectLoaded()
    await expectAccessTokenInStorage(page)

    await page.reload()
    await new DashboardPage(page).expectLoaded()
    await expectAccessTokenInStorage(page)
  })

  test('shows error on invalid login', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login('invalid@example.com', 'WrongPass1!')
    await expect(page.getByText(/thất bại|không đúng|sai/i)).toBeVisible({ timeout: 10_000 })
    await expect(page).toHaveURL(/\/auth\/login/)
  })

  test('logout clears session', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    const dashboard = new DashboardPage(page)
    await dashboard.expectLoaded()
    await dashboard.logout()
    await expect(page).toHaveURL(/\/auth\/login/)
    const token = await page.evaluate(() => localStorage.getItem('access_token'))
    expect(token).toBeFalsy()
  })
})

test('redirects unauthenticated users from dashboard', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page).toHaveURL(/\/auth\/login/, { timeout: 15_000 })
})
