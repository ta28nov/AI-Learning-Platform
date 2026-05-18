export class DashboardPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page
    this.logoutButton = page.getByRole('button', { name: /đăng xuất/i })
  }

  async expectLoaded() {
    await this.page.waitForURL(/\/dashboard/, { timeout: 30_000 })
    await this.page.getByRole('banner').waitFor({ state: 'visible' })
  }

  async logout() {
    await this.logoutButton.click()
    await this.page.waitForURL(/\/auth\/login/, { timeout: 15_000 })
  }
}
