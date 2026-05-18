export class QuizListPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page
  }

  async goto() {
    await this.page.goto('/dashboard/quiz')
    await this.page.getByRole('heading', { name: /quiz/i }).waitFor({ timeout: 30_000 })
  }

  async openFirstQuiz() {
    await this.goto()
    const card = this.page.locator('.qp-card, [class*="quiz"]').first()
    const hasQuiz = await card.count()
    if (!hasQuiz) return false
    await card.click()
    await this.page.waitForURL(/\/dashboard\/quiz\//, { timeout: 15_000 })
    return true
  }
}
