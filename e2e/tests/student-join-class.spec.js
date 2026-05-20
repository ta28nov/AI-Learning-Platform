import { test, expect } from '@playwright/test'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { LoginPage } from '../pages/LoginPage.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const users = JSON.parse(readFileSync(join(__dirname, '../fixtures/test-users.json'), 'utf-8'))
const API = process.env.E2E_API_URL || 'http://127.0.0.1:8000/api/v1'

test.describe('Student join class', () => {
  test('student opens join modal on /dashboard/classes', async ({ page }) => {
    const login = new LoginPage(page)
    await login.login(users.student.email, users.student.password)
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 })

    await page.goto('/dashboard/classes')
    await expect(page).not.toHaveURL(/\/unauthorized/)
    await expect(page.getByRole('heading', { name: /Lớp học của tôi/i })).toBeVisible({ timeout: 30_000 })
    await page.getByRole('button', { name: /Tham gia lớp/i }).click()
    await expect(page.getByRole('heading', { name: /Tham gia lớp học/i })).toBeVisible()
  })

  test('API join with fresh class invite code', async ({ request }) => {
    const today = new Date().toISOString().slice(0, 10)
    const nextMonth = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)

    const instLogin = await request.post(`${API}/auth/login`, {
      data: { email: users.instructor.email, password: users.instructor.password },
    })
    test.skip(!instLogin.ok(), 'Seed: instructor login')
    const instToken = (await instLogin.json()).access_token

    const coursesRes = await request.get(`${API}/courses/public`, {
      params: { limit: 50 },
      headers: { Authorization: `Bearer ${instToken}` },
    })
    const courses = (await coursesRes.json()).courses || []
    test.skip(courses.length === 0, 'Seed: public courses')

    const created = await request.post(`${API}/classes`, {
      headers: { Authorization: `Bearer ${instToken}` },
      data: {
        name: `E2E API Join ${Date.now()}`,
        description: 'API join',
        course_id: courses[0].id,
        start_date: today,
        end_date: nextMonth,
        max_students: 30,
      },
    })
    test.skip(!created.ok(), 'Create class failed')
    const inviteCode = (await created.json()).invite_code

    const stLogin = await request.post(`${API}/auth/login`, {
      data: { email: users.student.email, password: users.student.password },
    })
    test.skip(!stLogin.ok(), 'Seed: student login')
    const stToken = (await stLogin.json()).access_token

    const join = await request.post(`${API}/classes/join`, {
      headers: { Authorization: `Bearer ${stToken}` },
      data: { invite_code: inviteCode },
    })
    expect(join.ok()).toBeTruthy()

    const myClasses = await request.get(`${API}/classes/my-classes`, {
      headers: { Authorization: `Bearer ${stToken}` },
    })
    expect(myClasses.ok()).toBeTruthy()
    const body = await myClasses.json()
    const list = body.classes || body.data?.classes || []
    expect(list.length).toBeGreaterThanOrEqual(1)
  })
})
