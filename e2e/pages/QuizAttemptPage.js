export class QuizAttemptPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page
    this.nextButton = page.getByRole('button', { name: /Câu tiếp/i })
    this.submitButton = page.getByRole('button', { name: /Nộp bài/i })
  }

  async attemptQuickly() {
    for (let i = 0; i < 30; i++) {
      const option = this.page.locator('.quiz-attempt-option').first()
      if (await option.isVisible().catch(() => false)) {
        await option.click()
      }
      if (await this.submitButton.isVisible().catch(() => false)) {
        await this.submitButton.click()
        return
      }
      if (await this.nextButton.isVisible().catch(() => false)) {
        await this.nextButton.click()
        continue
      }
      break
    }
  }

  async expectResultsOrDetail() {
    await this.page.waitForURL(/\/dashboard\/quiz\//, { timeout: 30_000 })
  }
}
