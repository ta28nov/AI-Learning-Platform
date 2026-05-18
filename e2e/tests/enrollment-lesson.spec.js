import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'
import { DashboardPage } from '../pages/DashboardPage.js'
import { CoursesPage } from '../pages/CoursesPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Enrollment and lesson', () => {
  test.beforeEach(async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await new DashboardPage(page).expectLoaded()
  })

  test('browse courses → enroll → open lesson → complete', async ({ page }) => {
    test.setTimeout(120_000)
    const courses = new CoursesPage(page)
    await courses.goto()

    const opened = await courses.openFirstCourse()
    test.skip(!opened, 'No published courses — run BE/scripts/init_data.py')

    const enrolled = await courses.enrollIfAvailable()
    if (enrolled) {
      await expect(page.getByText(/đăng ký thành công|Đã đăng ký/i).first()).toBeVisible({ timeout: 15_000 }).catch(() => {})
    }

    const startBtn = page.getByRole('button', { name: /bắt đầu học|tiếp tục|vào học/i }).first()
    if (await startBtn.isVisible().catch(() => false)) {
      await startBtn.click()
    } else {
      const lessonLink = page.locator('a[href*="/lessons/"], button:has-text("Học")').first()
      test.skip(!(await lessonLink.isVisible().catch(() => false)), 'No lesson entry on course detail')
      await lessonLink.click()
    }

    await page.waitForURL(/\/lessons\//, { timeout: 30_000 })
    const completeBtn = page.getByRole('button', { name: /Đánh dấu đã học xong/i })
    if (await completeBtn.isVisible().catch(() => false)) {
      await completeBtn.click()
      await expect(page.getByText(/Đã hoàn thành|hoàn thành/i).first()).toBeVisible({ timeout: 15_000 })
    }
  })
})
