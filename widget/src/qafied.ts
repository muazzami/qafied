import html2canvas from 'html2canvas'

interface QafiedConfig {
  website_id: number
  show_by_default: boolean
  enabled: boolean
}

interface BrowserInfo {
  name: string
  version: string
}

interface FeedbackPayload {
  page_url: string
  content: string
  feedback_type: string
  commenter_name?: string
  commenter_email?: string
  x_position: number
  y_position: number
  browser_info: BrowserInfo
  os_info: BrowserInfo
  screen_width: number
  screen_height: number
  viewport_width: number
  viewport_height: number
  include_screenshot: boolean
  screenshot_data?: string
}

const STORAGE_USER = 'qafied:commenter'

class QafiedWidget {
  private config: QafiedConfig | null = null
  private isActive = false
  private isPlacing = false
  private button: HTMLElement | null = null
  private readonly key: string
  private readonly apiUrl: string

  constructor() {
    const script = document.currentScript as HTMLScriptElement | null
    this.key = script?.getAttribute('data-key') ?? ''
    this.apiUrl = script?.getAttribute('data-api') ?? 'http://localhost:8000'
    void this.init()
  }

  private async init(): Promise<void> {
    if (!this.key) {
      console.error('Qafied: missing data-key attribute')
      return
    }

    const urlParams = new URLSearchParams(window.location.search)
    const forceShow = urlParams.get('feedback') === 'on'

    try {
      const response = await fetch(
        `${this.apiUrl}/widget/config?key=${encodeURIComponent(this.key)}`,
      )
      if (!response.ok) throw new Error('Invalid key')
      this.config = (await response.json()) as QafiedConfig

      if (this.config.show_by_default || forceShow) {
        this.activate()
      }
    } catch (error) {
      console.error('Qafied: Failed to initialize', error)
    }
  }

  private activate(): void {
    if (this.isActive) return
    this.isActive = true

    this.injectStyles()
    this.createButton()
  }

  private createButton(): void {
    this.button = document.createElement('div')
    this.button.className = 'qafied-widget-button'
    this.button.setAttribute('role', 'button')
    this.button.setAttribute('aria-label', 'Add feedback')
    this.button.innerHTML = '💬'
    this.button.addEventListener('click', (e) => {
      e.stopPropagation()
      this.enterPlacementMode()
    })
    document.body.appendChild(this.button)
  }

  private enterPlacementMode(): void {
    if (this.isPlacing) {
      this.exitPlacementMode()
      return
    }
    this.isPlacing = true
    document.body.classList.add('qafied-placing')
    document.addEventListener('click', this.handlePageClick, true)
  }

  private exitPlacementMode(): void {
    this.isPlacing = false
    document.body.classList.remove('qafied-placing')
    document.removeEventListener('click', this.handlePageClick, true)
  }

  private handlePageClick = (e: MouseEvent): void => {
    if (!this.isPlacing) return
    const target = e.target as HTMLElement
    if (target.closest('.qafied-widget-button, .qafied-modal, .qafied-marker')) {
      return
    }

    e.preventDefault()
    e.stopPropagation()

    this.exitPlacementMode()

    const marker = document.createElement('div')
    marker.className = 'qafied-marker'
    marker.style.left = `${e.pageX - 12}px`
    marker.style.top = `${e.pageY - 12}px`
    document.body.appendChild(marker)

    this.showFeedbackForm(e.pageX, e.pageY, target, marker)
  }

  private showFeedbackForm(
    x: number,
    y: number,
    target: HTMLElement,
    marker: HTMLElement,
  ): void {
    const stored = this.readStoredCommenter()

    const modal = document.createElement('div')
    modal.className = 'qafied-modal'
    modal.innerHTML = `
      <div class="qafied-modal-backdrop"></div>
      <div class="qafied-modal-content" role="dialog" aria-modal="true">
        <h3>Add feedback</h3>
        <form id="qafied-form">
          <label class="qafied-field">
            <span>Type</span>
            <select name="type">
              <option value="suggestion">Suggestion</option>
              <option value="change">Change</option>
              <option value="remove">Remove</option>
              <option value="replace">Replace</option>
              <option value="bug">Bug</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label class="qafied-field">
            <span>Comment</span>
            <textarea name="content" rows="4" required placeholder="Describe your feedback…"></textarea>
          </label>
          <label class="qafied-field qafied-checkbox">
            <input type="checkbox" name="screenshot" checked>
            Include screenshot
          </label>
          <label class="qafied-field">
            <span>Name (optional)</span>
            <input type="text" name="name" value="${this.escape(stored.name)}" placeholder="Your name">
          </label>
          <label class="qafied-field">
            <span>Email (optional)</span>
            <input type="email" name="email" value="${this.escape(stored.email)}" placeholder="your@email.com">
          </label>
          <div class="qafied-actions">
            <button type="button" class="qafied-cancel">Cancel</button>
            <button type="submit" class="qafied-submit">Submit</button>
          </div>
        </form>
      </div>
    `
    document.body.appendChild(modal)

    const cleanup = () => {
      modal.remove()
      marker.remove()
    }

    modal.querySelector('.qafied-modal-backdrop')?.addEventListener('click', cleanup)
    modal.querySelector('.qafied-cancel')?.addEventListener('click', cleanup)

    const form = modal.querySelector('#qafied-form') as HTMLFormElement
    form.addEventListener('submit', async (e) => {
      e.preventDefault()
      const submitBtn = form.querySelector('.qafied-submit') as HTMLButtonElement
      submitBtn.disabled = true
      submitBtn.textContent = 'Submitting…'
      try {
        await this.submitFeedback(form, x, y, target)
        cleanup()
        this.toast('Thanks for your feedback!')
      } catch (err) {
        console.error('Qafied: submit failed', err)
        submitBtn.disabled = false
        submitBtn.textContent = 'Submit'
        alert('Failed to submit feedback. Please try again.')
      }
    })
  }

  private async submitFeedback(
    form: HTMLFormElement,
    x: number,
    y: number,
    target: HTMLElement,
  ): Promise<void> {
    const formData = new FormData(form)
    const includeScreenshot = formData.get('screenshot') === 'on'

    let screenshotData: string | undefined
    if (includeScreenshot) {
      try {
        const canvas = await html2canvas(document.body, { logging: false })
        screenshotData = canvas.toDataURL('image/png')
      } catch (err) {
        console.warn('Qafied: screenshot failed', err)
      }
    }

    const name = (formData.get('name') as string | null)?.trim() || undefined
    const email = (formData.get('email') as string | null)?.trim() || undefined
    this.persistCommenter(name, email)

    const payload: FeedbackPayload = {
      page_url: window.location.href,
      content: (formData.get('content') as string).trim(),
      feedback_type: formData.get('type') as string,
      commenter_name: name,
      commenter_email: email,
      x_position: x,
      y_position: y,
      browser_info: this.getBrowserInfo(),
      os_info: this.getOSInfo(),
      screen_width: window.screen.width,
      screen_height: window.screen.height,
      viewport_width: window.innerWidth,
      viewport_height: window.innerHeight,
      include_screenshot: includeScreenshot,
      screenshot_data: screenshotData,
    }

    const selector = this.buildSelector(target)
    if (selector) {
      ;(payload as any).element_selector = selector
    }

    const response = await fetch(
      `${this.apiUrl}/widget/feedback?key=${encodeURIComponent(this.key)}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      },
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
  }

  private getBrowserInfo(): BrowserInfo {
    const ua = navigator.userAgent
    let name = 'Unknown'
    let version = ''

    if (ua.includes('Firefox/')) {
      name = 'Firefox'
      version = ua.match(/Firefox\/(\d+\.\d+)/)?.[1] ?? ''
    } else if (ua.includes('Edg/')) {
      name = 'Edge'
      version = ua.match(/Edg\/(\d+\.\d+)/)?.[1] ?? ''
    } else if (ua.includes('Chrome/')) {
      name = 'Chrome'
      version = ua.match(/Chrome\/(\d+\.\d+)/)?.[1] ?? ''
    } else if (ua.includes('Safari/')) {
      name = 'Safari'
      version = ua.match(/Version\/(\d+\.\d+)/)?.[1] ?? ''
    }

    return { name, version }
  }

  private getOSInfo(): BrowserInfo {
    const ua = navigator.userAgent
    let name = 'Unknown'
    let version = ''

    if (ua.includes('Windows NT')) {
      name = 'Windows'
      version = ua.match(/Windows NT (\d+\.\d+)/)?.[1] ?? ''
    } else if (ua.includes('Mac OS X')) {
      name = 'macOS'
      version = ua.match(/Mac OS X (\d+[._]\d+)/)?.[1]?.replace('_', '.') ?? ''
    } else if (ua.includes('Android')) {
      name = 'Android'
      version = ua.match(/Android (\d+(\.\d+)?)/)?.[1] ?? ''
    } else if (ua.includes('iPhone') || ua.includes('iPad')) {
      name = 'iOS'
      version = ua.match(/OS (\d+[._]\d+)/)?.[1]?.replace('_', '.') ?? ''
    } else if (ua.includes('Linux')) {
      name = 'Linux'
    }

    return { name, version }
  }

  private buildSelector(el: HTMLElement | null): string | null {
    if (!el || el === document.body) return null
    if (el.id) return `#${el.id}`
    const parts: string[] = []
    let cur: HTMLElement | null = el
    let depth = 0
    while (cur && cur !== document.body && depth < 4) {
      const tag = cur.tagName.toLowerCase()
      const cls = cur.className && typeof cur.className === 'string'
        ? `.${cur.className.trim().split(/\s+/).slice(0, 2).join('.')}`
        : ''
      parts.unshift(`${tag}${cls}`)
      cur = cur.parentElement
      depth++
    }
    return parts.join(' > ')
  }

  private readStoredCommenter(): { name: string; email: string } {
    try {
      const raw = localStorage.getItem(STORAGE_USER)
      if (!raw) return { name: '', email: '' }
      const parsed = JSON.parse(raw)
      return { name: parsed.name ?? '', email: parsed.email ?? '' }
    } catch {
      return { name: '', email: '' }
    }
  }

  private persistCommenter(name?: string, email?: string): void {
    if (!name && !email) return
    try {
      localStorage.setItem(STORAGE_USER, JSON.stringify({ name, email }))
    } catch {
      /* ignore quota errors */
    }
  }

  private escape(s: string): string {
    return s
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
  }

  private toast(message: string): void {
    const el = document.createElement('div')
    el.className = 'qafied-toast'
    el.textContent = message
    document.body.appendChild(el)
    setTimeout(() => el.remove(), 3000)
  }

  private injectStyles(): void {
    if (document.getElementById('qafied-styles')) return
    const style = document.createElement('style')
    style.id = 'qafied-styles'
    style.textContent = `
      .qafied-widget-button {
        position: fixed; bottom: 20px; right: 20px;
        width: 56px; height: 56px;
        background: #111; color: #fff;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px; cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 2147483646;
        transition: transform 0.2s;
      }
      .qafied-widget-button:hover { transform: scale(1.1); }
      body.qafied-placing,
      body.qafied-placing * { cursor: crosshair !important; }
      .qafied-marker {
        position: absolute; width: 24px; height: 24px;
        background: #ef4444; border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        z-index: 2147483645; pointer-events: none;
      }
      .qafied-modal { position: fixed; inset: 0; z-index: 2147483647; font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; color: #111; }
      .qafied-modal-backdrop { position: absolute; inset: 0; background: rgba(0,0,0,0.4); }
      .qafied-modal-content {
        position: relative; margin: 60px auto; max-width: 440px;
        background: #fff; padding: 24px; border-radius: 12px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.25);
      }
      .qafied-modal-content h3 { margin: 0 0 16px; font-size: 18px; font-weight: 600; }
      .qafied-field { display: block; margin-bottom: 12px; }
      .qafied-field > span { display: block; font-size: 13px; margin-bottom: 4px; color: #444; }
      .qafied-field select, .qafied-field input, .qafied-field textarea {
        width: 100%; box-sizing: border-box; padding: 8px 10px;
        border: 1px solid #d1d5db; border-radius: 6px; font: inherit;
      }
      .qafied-field.qafied-checkbox { display: flex; align-items: center; gap: 8px; font-size: 14px; }
      .qafied-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
      .qafied-actions button { padding: 8px 14px; border-radius: 6px; cursor: pointer; font: inherit; border: 0; }
      .qafied-cancel { background: #f3f4f6; color: #111; }
      .qafied-submit { background: #111; color: #fff; }
      .qafied-submit:disabled { opacity: 0.6; cursor: not-allowed; }
      .qafied-toast {
        position: fixed; bottom: 90px; right: 20px;
        background: #111; color: #fff; padding: 10px 14px;
        border-radius: 8px; z-index: 2147483647;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2); font-size: 14px;
      }
    `
    document.head.appendChild(style)
  }
}

new QafiedWidget()
