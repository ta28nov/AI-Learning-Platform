export class AssessmentPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page
    this.startButton = page.getByRole('button', { name: /bắt đầu đánh giá/i })
    this.loading = page.getByText(/AI đang|đang tạo/i)
  }

  async goto() {
    await this.page.goto('/dashboard/assessment')
    await this.page.getByRole('heading', { name: /đánh giá năng lực/i }).waitFor()
  }

  async startBeginnerPythonAssessment() {
    await this.goto()
    await this.page.getByRole('button', { name: 'Programming' }).click()
    await this.page.getByRole('button', { name: 'Python' }).click()
    await this.page.getByRole('button', { name: 'Beginner' }).click()
    await this.startButton.click()
    await this.page.waitForURL(/\/dashboard\/assessment\/[^/]+$/, { timeout: 180_000 })
  }
}
