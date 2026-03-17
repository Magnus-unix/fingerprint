import 'dotenv/config'
import { mkdir } from 'node:fs/promises'
import { join } from 'node:path'
import { writeFile } from 'node:fs/promises'
import { chromium } from 'playwright'
import { z } from 'zod'
import { Output } from 'ai'
import { openai } from '@ai-sdk/openai'
import LLMScraper from 'llm-scraper'

const LOGIN_URL = 'https://magnus-unix.github.io/fingerprint/login.html'
const USERNAME = 'test'
const PASSWORD = 'test'
const MODEL_NAME = 'gpt-5.2'

if (!process.env.OPENAI_API_KEY) {
  throw new Error('Missing OPENAI_API_KEY in environment (.env)')
}

const model = openai(MODEL_NAME)
const scraper = new LLMScraper(model)
const browser = await chromium.launch({ headless: false })

try {
  const page = await browser.newPage()
  await page.goto(LOGIN_URL, { waitUntil: 'domcontentloaded' })

  await page.waitForSelector('#username', { timeout: 15000 })
  await page.waitForSelector('#password', { timeout: 15000 })
  await page.waitForSelector('#loginButton', { timeout: 15000 })

  await page.fill('#username', USERNAME)
  await page.fill('#password', PASSWORD)
  await page.click('#loginButton')

  await page.waitForLoadState('domcontentloaded')
  await page.waitForTimeout(1500)

  const imageStats = await page.evaluate(() => {
    const images = Array.from(document.images || [])
    const total = images.length
    const loaded = images.filter((img) => img.complete && img.naturalWidth > 0).length
    const failed = images.filter((img) => img.complete && img.naturalWidth === 0).length
    return { total, loaded, failed }
  })

  await mkdir('outputs', { recursive: true })
  const ts = new Date().toISOString().replace(/[:.]/g, '-')
  const screenshotPath = join('outputs', `login_after_${ts}.png`)
  const reportPath = join('outputs', `llm_crawl_${ts}.json`)
  const extractedPath = join('outputs', `llm_extracted_${ts}.json`)
  await page.screenshot({ path: screenshotPath, fullPage: true })

  const crawlSchema = z.object({
    page: z.object({
      title: z.string(),
      url: z.string(),
      language: z.string().nullable(),
      summary: z.string(),
    }),
    auth: z.object({
      isLikelyLoggedIn: z.boolean(),
      loginFormPresent: z.boolean(),
      logoutControlPresent: z.boolean(),
      userHintText: z.string().nullable(),
      evidence: z.array(z.string()).max(8),
    }),
    content: z.object({
      headings: z.array(z.string()).max(20),
      keyTexts: z.array(z.string()).max(20),
      links: z
        .array(
          z.object({
            text: z.string(),
            href: z.string(),
          })
        )
        .max(30),
      images: z
        .array(
          z.object({
            src: z.string(),
            alt: z.string().nullable(),
          })
        )
        .max(30),
      forms: z
        .array(
          z.object({
            action: z.string().nullable(),
            method: z.string().nullable(),
            fieldNames: z.array(z.string()).max(20),
          })
        )
        .max(10),
    }),
    nextActions: z.array(z.string()).max(10),
  })

  let data = null
  let llmError = null
  try {
    const result = await scraper.run(page, Output.object({ schema: crawlSchema }), {
      format: 'html',
      temperature: 0,
      system:
        'You are a crawler extraction engine. Return only factual data from visible DOM after login. Never invent missing fields; use empty arrays or null.',
    })
    data = result.data
    await writeFile(extractedPath, JSON.stringify(data, null, 2), 'utf-8')
  } catch (error) {
    llmError = error instanceof Error ? error.message : String(error)
  }

  const state = await page.evaluate(() => ({
    href: location.href,
    title: document.title,
    loginButtonVisible: !!document.querySelector('#loginButton'),
    usernameValue: document.querySelector('#username')?.value || '',
    passwordValue: document.querySelector('#password')?.value || '',
  }))

  const report = {
    timestamp: new Date().toISOString(),
    engine: 'playwright + llm-scraper',
    model: MODEL_NAME,
    login: {
      url: LOGIN_URL,
      username: USERNAME,
      successLikely: !state.loginButtonVisible,
      state,
    },
    imageStats,
    screenshotPath,
    extractedPath: data ? extractedPath : null,
    llmError,
    extracted: data,
  }

  await writeFile(reportPath, JSON.stringify(report, null, 2), 'utf-8')

  console.log('=== llm-scraper login run ===')
  console.log('url:', state.href)
  console.log('title:', state.title)
  console.log('loginButtonVisible:', state.loginButtonVisible)
  console.log('images:', imageStats)
  console.log('screenshot:', screenshotPath)
  console.log('report:', reportPath)
  console.log('extracted:', data ? extractedPath : 'none')
  console.log('llmError:', llmError)
  console.log('extracted.summary:', data?.page?.summary)

  await page.close()
} finally {
  await browser.close()
}