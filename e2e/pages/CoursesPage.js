export class CoursesPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page
    this.heading = page.getByRole('heading', { name: /Khám phá khóa học/i })
  }

  async goto() {
    await this.page.goto('/dashboard/courses')
    await this.heading.waitFor({ timeout: 30_000 })
  }

  async openFirstCourse() {
    const card = this.page.locator('.course-card').first()
    const count = await card.count()
    if (!count) return false
    await card.click()
    await this.page.waitForURL(/\/dashboard\/courses\//, { timeout: 15_000 })
    return true
  }

  async enrollIfAvailable() {
    const btn = this.page.getByRole('button', { name: /Đăng ký khóa học/i })
    if (await btn.isVisible().catch(() => false)) {
      await btn.click()
      return true
    }
    return false
  }
}
