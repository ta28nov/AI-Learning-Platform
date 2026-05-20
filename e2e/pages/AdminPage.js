/** @param {import('@playwright/test').Page} page */
export class AdminPage {
  constructor(page) {
    this.page = page
    this.heading = page.getByRole('heading', { name: /Admin Console/i })
  }

  async expectLoaded() {
    await this.heading.waitFor({ state: 'visible', timeout: 30_000 })
  }

  /** @param {'users' | 'courses' | 'classes' | 'analytics'} tab */
  async gotoTab(tab) {
    const paths = {
      users: '/dashboard/admin/users',
      courses: '/dashboard/admin/courses',
      classes: '/dashboard/admin/classes',
      analytics: '/dashboard/admin/analytics',
    }
    await this.page.goto(paths[tab])
    await this.expectLoaded()
  }

  tabLink(name) {
    return this.page.getByRole('link', { name })
  }
}
