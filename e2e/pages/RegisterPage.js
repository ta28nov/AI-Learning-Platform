export class RegisterPage {
  /** @param {import('@playwright/test').Page} page */
  constructor(page) {
    this.page = page
    this.fullName = page.getByLabel('Họ và tên')
    this.email = page.getByLabel('Email')
    this.password = page.getByLabel('Mật khẩu', { exact: true })
    this.confirmPassword = page.getByLabel('Xác nhận mật khẩu')
    this.submit = page.getByRole('button', { name: /đăng ký/i })
  }

  async goto() {
    await this.page.goto('/auth/register')
  }

  async register({ fullName, email, password }) {
    await this.goto()
    await this.fullName.fill(fullName)
    await this.email.fill(email)
    await this.password.fill(password)
    await this.confirmPassword.fill(password)
    await this.submit.click()
  }
}
