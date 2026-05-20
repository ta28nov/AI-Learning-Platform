export class LoginPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page
    this.email = page.getByLabel('Email')
    this.password = page.getByLabel('Mật khẩu')
    this.submit = page.getByRole('button', { name: 'Đăng nhập', exact: true })
  }

  async goto() {
    await this.page.goto('/auth/login')
  }

  async login(email, password) {
    await this.goto()
    await this.email.fill(email)
    await this.password.fill(password)
    await this.submit.click()
  }
}
