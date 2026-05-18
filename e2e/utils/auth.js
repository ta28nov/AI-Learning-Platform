/**
 * Auth helpers for Playwright E2E tests.
 */

/**
 * @param {import('@playwright/test').Page} page
 * @param {{ email: string, password: string, rememberMe?: boolean }} credentials
 */
export async function loginViaUi(page, { email, password, rememberMe = false }) {
  await page.goto('/auth/login')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Mật khẩu').fill(password)
  if (rememberMe) {
    await page.getByRole('checkbox', { name: /ghi nhớ/i }).check()
  }
  await page.getByRole('button', { name: /đăng nhập/i }).click()
  await page.waitForURL(/\/dashboard/, { timeout: 30_000 })
}

/**
 * @param {import('@playwright/test').Page} page
 */
export async function logoutViaUi(page) {
  await page.getByRole('button', { name: /đăng xuất/i }).click()
  await page.waitForURL(/\/auth\/login/, { timeout: 15_000 })
}

/**
 * @param {import('@playwright/test').Page} page
 */
export async function expectAccessTokenInStorage(page) {
  const token = await page.evaluate(() => localStorage.getItem('access_token'))
  if (!token) throw new Error('access_token missing from localStorage')
  return token
}
