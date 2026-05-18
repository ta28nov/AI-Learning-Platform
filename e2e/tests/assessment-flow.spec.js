import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'
import { DashboardPage } from '../pages/DashboardPage.js'
import { AssessmentPage } from '../pages/AssessmentPage.js'
import { AssessmentQuizPage } from '../pages/AssessmentQuizPage.js'
import { AssessmentResultsPage } from '../pages/AssessmentResultsPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))

const hasGemini = Boolean(process.env.GOOGLE_API_KEY && process.env.GOOGLE_API_KEY !== 'fake-key-not-used-in-tests')

test.describe('Assessment full flow', () => {
  test.beforeEach(async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await new DashboardPage(page).expectLoaded()
  })

  test('setup → generate → answer → submit → results', async ({ page }) => {
    test.skip(!hasGemini, 'Requires GOOGLE_API_KEY for live assessment generation')
    test.setTimeout(180_000)

    const assessment = new AssessmentPage(page)
    await assessment.startBeginnerPythonAssessment()

    const quiz = new AssessmentQuizPage(page)
    await quiz.answerAllQuestionsQuickly()

    const results = new AssessmentResultsPage(page)
    await results.expectLoaded()
    await expect(page).toHaveURL(/\/results/)
  })
})
