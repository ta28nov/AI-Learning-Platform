import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'
import { DashboardPage } from '../pages/DashboardPage.js'
import { QuizListPage } from '../pages/QuizPage.js'
import { QuizAttemptPage } from '../pages/QuizAttemptPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

test.describe('Quiz flow', () => {
  test.beforeEach(async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await new DashboardPage(page).expectLoaded()
  })

  test('quiz list page loads', async ({ page }) => {
    const quiz = new QuizListPage(page)
    await quiz.goto()
    await expect(page.getByRole('heading', { name: /quiz/i })).toBeVisible()
  })

  test('open first quiz when available', async ({ page }) => {
    const quiz = new QuizListPage(page)
    const opened = await quiz.openFirstQuiz()
    test.skip(!opened, 'No quizzes in seed data — run BE/scripts/init_data.py first')
    await expect(page).toHaveURL(/\/dashboard\/quiz\//)
  })

  test('attempt quiz when start available', async ({ page }) => {
    test.setTimeout(90_000)
    const quiz = new QuizListPage(page)
    const opened = await quiz.openFirstQuiz()
    test.skip(!opened, 'No quizzes in seed data — run BE/scripts/init_data.py first')

    const startBtn = page.getByRole('button', { name: /bắt đầu|làm bài|attempt/i }).first()
    if (await startBtn.isVisible().catch(() => false)) {
      await startBtn.click()
    } else {
      await page.goto(page.url().replace(/\/$/, '') + '/attempt')
    }

    await page.waitForURL(/\/attempt/, { timeout: 15_000 })
    const attempt = new QuizAttemptPage(page)
    await attempt.attemptQuickly()
    await attempt.expectResultsOrDetail()
  })
})
