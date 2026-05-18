import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'
import { DashboardPage } from '../pages/DashboardPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

const hasGemini = Boolean(process.env.GOOGLE_API_KEY && process.env.GOOGLE_API_KEY !== 'fake-key-not-used-in-tests')

test.describe('AI Chat', () => {
  test.beforeEach(async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await new DashboardPage(page).expectLoaded()
  })

  test('send message and see reply', async ({ page }) => {
    test.skip(!hasGemini, 'Requires GOOGLE_API_KEY for live chat responses')
    test.setTimeout(120_000)

    await page.goto('/dashboard/chat')
    await page.getByText(/AI Trợ giảng|Xin chào/i).first().waitFor()

    const courseSelect = page.locator('select').first()
    if (await courseSelect.isVisible().catch(() => false)) {
      const options = await courseSelect.locator('option').count()
      if (options > 1) await courseSelect.selectOption({ index: 1 })
    }

    await page.getByPlaceholder(/Nhập câu hỏi/i).fill('What is this course about?')
    await page.getByRole('button', { name: /Gửi/i }).click()

    await expect(page.locator('.chat-message, .chat-bubble, [class*="message"]').last()).toBeVisible({
      timeout: 90_000,
    })
  })
})
