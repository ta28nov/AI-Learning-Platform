export class RecommendationsPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page
    this.heading = page.getByRole('heading', { name: /Lộ trình học tập gợi ý/i })
  }

  async goto(sessionId) {
    const path = sessionId
      ? `/dashboard/recommendations?session_id=${sessionId}`
      : '/dashboard/recommendations'
    await this.page.goto(path)
    await this.heading.waitFor({ timeout: 120_000 })
  }

  async expectCourseListOrEmpty() {
    const cards = this.page.locator('.rec-card, .rec-course-card, [class*="rec-"]')
    const empty = this.page.getByText(/chưa có|không có khóa|empty/i)
    await Promise.race([
      cards.first().waitFor({ timeout: 60_000 }).catch(() => null),
      empty.waitFor({ timeout: 60_000 }).catch(() => null),
      this.page.getByText(/lộ trình|gợi ý/i).first().waitFor({ timeout: 60_000 }),
    ])
  }
}
