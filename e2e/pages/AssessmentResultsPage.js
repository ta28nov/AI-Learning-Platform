export class AssessmentResultsPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page
    this.heading = page.getByRole('heading', { name: /Kết quả đánh giá/i })
  }

  async expectLoaded() {
    await this.heading.waitFor({ timeout: 120_000 })
  }
}
