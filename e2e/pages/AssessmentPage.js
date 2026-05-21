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
    // Level: hidden radio inside label; default is Beginner — click visible card if needed.
    const beginnerCard = this.page.locator('label.asp-level-card').filter({ hasText: /^Beginner$/ })
    if (await beginnerCard.isVisible().catch(() => false)) {
      await beginnerCard.click()
    }
    await this.startButton.click()
    await this.page.waitForURL(/\/dashboard\/assessment\/[^/]+$/, { timeout: 240_000 })
  }
}
