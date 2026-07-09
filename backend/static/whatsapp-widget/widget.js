/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 *  Floating WhatsApp Widget — Web Component
 *  Custom Element <wa-widget>
 *  ES Module — Shadow DOM — Fetch API
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

const STORAGE_LANG_KEY = 'ioque-lang';
const API_ENDPOINT = '/api/contact/widget/';

/* ── SVG icons ───────────────────────────── */
const ICONS = {
  whatsapp: `<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M19.05 4.91A9.82 9.82 0 0 0 12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01zm-7.01 15.24c-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.26 8.26 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.24-8.24 2.2 0 4.27.86 5.82 2.42a8.18 8.18 0 0 1 2.41 5.83c.01 4.54-3.69 8.23-8.22 8.23zm4.52-6.16c-.25-.12-1.47-.72-1.7-.8-.23-.08-.39-.12-.56.12-.17.24-.64.8-.78.96-.14.16-.28.18-.53.06-.25-.12-1.05-.39-2-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.44.12-.15.16-.25.24-.42.08-.17.04-.31-.02-.43-.06-.12-.56-1.35-.77-1.85-.2-.49-.4-.42-.56-.43-.14-.01-.31-.01-.48-.01-.17 0-.44.06-.67.31-.23.25-.87.85-.87 2.08 0 1.22.89 2.4 1.02 2.57.13.17 1.75 2.68 4.25 3.76.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.08.15-1.18-.06-.1-.22-.16-.47-.28z"/></svg>`,
  close: `<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>`,
  minimize: `<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M19 13H5v-2h14v2z"/></svg>`,
  send: `<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>`,
  store: `<svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M18.36 9l.6-4H5.04l.6 4h12.72M20 4l-1 6H5L4 4h16m-5 8c0 1.66-1.34 3-3 3s-3-1.34-3-3"/></svg>`,
};

/* ── Default texts (ES/EN/PT/FR) ─────────── */
const TEXTS = {
  es: {
    title: 'WhatsApp',
    subtitle: 'Estamos para ayudarte',
    name: 'Nombre',
    phone: 'Teléfono',
    email: 'Correo',
    company: 'Empresa',
    message: 'Mensaje',
    submit: 'Enviar por WhatsApp',
    privacy: 'Acepto las políticas de privacidad',
    nameReq: 'El nombre es obligatorio',
    privacyReq: 'Debes aceptar las políticas de privacidad',
    online: 'En línea',
    writeUs: 'Escríbenos',
  },
  en: {
    title: 'WhatsApp',
    subtitle: 'We are here to help',
    name: 'Name',
    phone: 'Phone',
    email: 'Email',
    company: 'Company',
    message: 'Message',
    submit: 'Send via WhatsApp',
    privacy: 'I accept the privacy policy',
    nameReq: 'Name is required',
    privacyReq: 'You must accept the privacy policy',
    online: 'Online',
    writeUs: 'Write to us',
  },
  pt: {
    title: 'WhatsApp',
    subtitle: 'Estamos aqui para ajudar',
    name: 'Nome',
    phone: 'Telefone',
    email: 'E-mail',
    company: 'Empresa',
    message: 'Mensagem',
    submit: 'Enviar pelo WhatsApp',
    privacy: 'Aceito as políticas de privacidade',
    nameReq: 'O nome é obrigatório',
    privacyReq: 'Você deve aceitar as políticas de privacidade',
    online: 'Online',
    writeUs: 'Escreva para nós',
  },
  fr: {
    title: 'WhatsApp',
    subtitle: 'Nous sommes là pour vous aider',
    name: 'Nom',
    phone: 'Téléphone',
    email: 'E-mail',
    company: 'Entreprise',
    message: 'Message',
    submit: 'Envoyer via WhatsApp',
    privacy: "J'accepte la politique de confidentialité",
    nameReq: 'Le nom est obligatoire',
    privacyReq: 'Vous devez accepter la politique de confidentialité',
    online: 'En ligne',
    writeUs: 'Écrivez-nous',
  },
};

/* ── Web Component ──────────────────────── */
class WhatsAppWidget extends HTMLElement {
  /* ── observed attributes ──────────────── */
  static get observedAttributes() {
    return ['lang'];
  }

  constructor() {
    super();
    this._open = false;
    this._config = null;
    this._loading = true;
    this._listeners = [];

    this.attachShadow({ mode: 'open' });
    this.shadowRoot.appendChild(document.createElement('slot'));
  }

  /* ── Lifecycle ────────────────────────── */
  connectedCallback() {
    this._injectCSS();
    this._renderSkeleton();
    this._fetchConfig();
    this._observeLang();
  }

  disconnectedCallback() {
    this._listeners.forEach(([el, type, fn]) => el.removeEventListener(type, fn));
    this._listeners = [];
    if (this._langObserver) this._langObserver.disconnect();
  }

  attributeChangedCallback(name, oldVal, newVal) {
    if (name === 'lang' && oldVal !== newVal && this._config) {
      this._renderCard();
    }
  }

  /* ── Get current language ─────────────── */
  get _lang() {
    const attr = this.getAttribute('lang');
    if (attr && TEXTS[attr]) return attr;
    const stored = localStorage.getItem(STORAGE_LANG_KEY);
    if (stored && TEXTS[stored]) return stored;
    const html = document.documentElement.getAttribute('lang');
    if (html && TEXTS[html]) return html;
    return 'es';
  }

  /* ── Get texts for current lang ────────── */
  _texts() {
    const lang = this._lang;
    const defaults = TEXTS[lang] || TEXTS.en;
    const cfg = this._config;
    if (!cfg || !cfg.translations) return defaults;
    const t = cfg.translations.find(x => x.language === lang);
    if (!t) return defaults;
    return {
      ...defaults,
      title: t.form_title || defaults.title,
      subtitle: t.welcome_message || defaults.subtitle,
      submit: t.submit_button_text || defaults.submit,
      privacy: t.privacy_policy_text || defaults.privacy,
    };
  }

  /* ── CSS injection ────────────────────── */
  _injectCSS() {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = new URL('widget.css', import.meta.url).href;
    link.setAttribute('wa-css', '');
    const slot = this.shadowRoot.querySelector('slot');
    if (slot) slot.replaceWith(link);
    else this.shadowRoot.prepend(link);
  }

  /* ── Skeleton (loading state) ─────────── */
  _renderSkeleton() {
    const css = this.shadowRoot.querySelector('[wa-css]');
    this.shadowRoot.replaceChildren(
      css,
      this._fabTemplate(),
      this._cardTemplate(true),
    );
  }

  /* ── API fetch ────────────────────────── */
  async _fetchConfig() {
    try {
      const res = await fetch(API_ENDPOINT);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (!data.enabled) {
        this.style.display = 'none';
        return;
      }
      this._config = data;
      this._loading = false;
      this._applyConfig();
    } catch (err) {
      console.warn('[wa-widget] Error loading config:', err);
      this._loading = false;
      this._renderError();
    }
  }

  /* ── Apply config & render ────────────── */
  _applyConfig() {
    const cfg = this._config;
    if (!cfg) return;

    /* Set CSS custom properties */
    const color = cfg.theme_color || '#25D366';
    const darker = this._darken(color, 25);
    this.style.setProperty('--wa-color', color);
    this.style.setProperty('--wa-color-dark', darker);

    /* Re-render */
    this._renderFAB();
    this._renderCard();
    this._bindEvents();
  }

  /* ── FAB template ─────────────────────── */
  _fabTemplate() {
    const cfg = this._config;
    const pos = cfg ? cfg.position : 'right';
    const fab = document.createElement('button');
    fab.className = `fab fab--${pos}`;
    fab.setAttribute('part', 'fab');
    fab.setAttribute('aria-label', 'Abrir WhatsApp');
    fab.innerHTML = `
      <span class="icon-chat">${ICONS.whatsapp}</span>
      <span class="icon-close">${ICONS.close}</span>
    `;
    return fab;
  }

  _renderFAB() {
    let fab = this.shadowRoot.querySelector('.fab');
    if (!fab) {
      fab = this._fabTemplate();
      this.shadowRoot.appendChild(fab);
    } else {
      const pos = this._config.position || 'right';
      fab.className = `fab fab--${pos}`;
    }
  }

  /* ── Card template ────────────────────── */
  _cardTemplate(loading) {
    const cfg = this._config;
    const t = this._texts();
    const pos = cfg ? cfg.position : 'right';
    const card = document.createElement('aside');
    card.className = `card card--${pos}`;
    card.setAttribute('part', 'card');
    card.setAttribute('role', 'dialog');
    card.setAttribute('aria-label', t.title);

    if (loading) {
      card.innerHTML = `<div class="loader"><div class="spinner"></div></div>`;
      return card;
    }

    const logo = cfg.logo_url
      ? `<img src="${cfg.logo_url}" alt="${cfg.company_name || ''}" loading="lazy">`
      : ICONS.store;

    const phoneField = cfg.show_phone_field !== false;
    const emailField = cfg.show_email_field !== false;

    card.innerHTML = `
      <header class="header">
        <div class="header-brand">
          <div class="avatar">${logo}</div>
          <div class="header-text">
            <span class="company-name">${cfg.company_name || 'IOQUE'}</span>
            <span class="status">
              <span class="status-dot"></span>
              ${t.online}
            </span>
          </div>
        </div>
        <button class="btn-minimize" data-action="close" aria-label="Minimizar">
          ${ICONS.minimize}
        </button>
      </header>

      <div class="body">
        <p class="welcome">${t.subtitle}</p>

        <form class="form" novalidate>
          <div class="form-group">
            <label for="wa-name">${t.name} *</label>
            <input
              type="text"
              id="wa-name"
              class="form-input"
              placeholder="${t.name}"
              required
              data-required
              autocomplete="name"
            />
            <div class="form-error" data-error="name">${t.nameReq}</div>
          </div>

          ${
            phoneField
              ? `<div class="form-group">
            <label for="wa-phone">${t.phone}</label>
            <input
              type="tel"
              id="wa-phone"
              class="form-input"
              placeholder="${t.phone}"
              ${cfg.require_phone ? 'required data-required' : ''}
              autocomplete="tel"
            />
            <div class="form-error" data-error="phone">${t.phone} ${t.nameReq.toLowerCase()}</div>
          </div>`
              : ''
          }

          ${
            emailField
              ? `<div class="form-group">
            <label for="wa-email">${t.email}</label>
            <input
              type="email"
              id="wa-email"
              class="form-input"
              placeholder="${t.email}"
              ${cfg.require_email ? 'required data-required' : ''}
              autocomplete="email"
            />
            <div class="form-error" data-error="email">${t.email} ${t.nameReq.toLowerCase()}</div>
          </div>`
              : ''
          }

          <div class="form-group">
            <label for="wa-message">${t.message}</label>
            <textarea
              id="wa-message"
              class="form-input"
              placeholder="${t.message}"
              rows="3"
            ></textarea>
          </div>

          <div class="checkbox-group">
            <input type="checkbox" id="wa-privacy" required />
            <div class="checkbox-label-group">
              <label for="wa-privacy">${t.privacy}</label>
              ${
                cfg.privacy_policy_url
                  ? `<a href="${cfg.privacy_policy_url}" target="_blank" rel="noopener" class="privacy-link">Leer políticas</a>`
                  : ''
              }
            </div>
          </div>
          <div class="checkbox-error" data-error="privacy">${t.privacyReq}</div>

          <button type="submit" class="btn-submit">
            ${ICONS.send}
            ${t.submit}
          </button>
        </form>
      </div>

      <footer class="footer">
        ${t.title} · ${cfg.company_name || 'IOQUE'}
      </footer>
    `;

    return card;
  }

  _renderCard() {
    let oldCard = this.shadowRoot.querySelector('.card');
    const newCard = this._cardTemplate(false);

    if (oldCard) {
      const wasOpen = oldCard.classList.contains('card--open');
      oldCard.replaceWith(newCard);
      if (wasOpen) {
        /* Re-apply open state in next frame */
        requestAnimationFrame(() => {
          newCard.classList.add('card--open');
        });
      }
    } else {
      this.shadowRoot.appendChild(newCard);
    }

    this._bindEvents();
  }

  _renderError() {
    const card = this.shadowRoot.querySelector('.card');
    if (card) {
      card.innerHTML = `
        <div class="body" style="display:flex;align-items:center;justify-content:center;min-height:160px;">
          <p style="color:var(--wa-on-surface-variant);font-size:14px;text-align:center;">
            No se pudo cargar el widget
          </p>
        </div>
      `;
    }
  }

  /* ── Event binding ────────────────────── */
  _bindEvents() {
    /* Clear old listeners */
    this._listeners.forEach(([el, type, fn]) => el.removeEventListener(type, fn));
    this._listeners = [];

    /* FAB click */
    const fab = this.shadowRoot.querySelector('.fab');
    if (fab) {
      this._addListener(fab, 'click', () => this._toggle());
    }

    /* Minimize button */
    const minimize = this.shadowRoot.querySelector('[data-action="close"]');
    if (minimize) {
      this._addListener(minimize, 'click', () => this._close());
    }

    /* Form submit */
    const form = this.shadowRoot.querySelector('.form');
    if (form) {
      this._addListener(form, 'submit', (e) => this._submit(e));
    }

    /* Close on Escape */
    this._addListener(document, 'keydown', (e) => {
      if (e.key === 'Escape' && this._open) this._close();
    });
  }

  _addListener(el, type, fn) {
    el.addEventListener(type, fn);
    this._listeners.push([el, type, fn]);
  }

  /* ── Toggle / Open / Close ────────────── */
  _toggle() {
    this._open ? this._close() : this._openCard();
  }

  _openCard() {
    this._open = true;
    const fab = this.shadowRoot.querySelector('.fab');
    const card = this.shadowRoot.querySelector('.card');
    if (fab) fab.classList.add('fab--open');
    if (card) card.classList.add('card--open');
    /* Focus first input */
    const firstInput = this.shadowRoot.querySelector('.form-input');
    if (firstInput) setTimeout(() => firstInput.focus(), 300);
  }

  _close() {
    this._open = false;
    const fab = this.shadowRoot.querySelector('.fab');
    const card = this.shadowRoot.querySelector('.card');
    if (fab) fab.classList.remove('fab--open');
    if (card) card.classList.remove('card--open');
  }

  /* ── Form validation ──────────────────── */
  _validate() {
    const form = this.shadowRoot.querySelector('.form');
    if (!form) return false;
    const inputs = form.querySelectorAll('[data-required]');
    let valid = true;

    inputs.forEach((input) => {
      const err = form.querySelector(`[data-error="${input.id.replace('wa-', '')}"]`);
      if (!input.value.trim()) {
        input.classList.add('error');
        if (err) err.classList.add('form-error--visible');
        valid = false;
      } else {
        input.classList.remove('error');
        if (err) err.classList.remove('form-error--visible');
      }
    });

    /* Privacy checkbox */
    const privacy = this.shadowRoot.getElementById('wa-privacy');
    const privacyErr = this.shadowRoot.querySelector('[data-error="privacy"]');
    if (privacy && !privacy.checked) {
      if (privacyErr) privacyErr.classList.add('checkbox-error--visible');
      valid = false;
    } else {
      if (privacyErr) privacyErr.classList.remove('checkbox-error--visible');
    }

    return valid;
  }

  /* ── Submit ───────────────────────────── */
  _submit(e) {
    e.preventDefault();
    if (!this._validate()) return;
    if (!this._config) return;

    const cfg = this._config;
    const t = this._texts();
    const form = this.shadowRoot.querySelector('.form');

    const name = form.querySelector('#wa-name').value.trim();
    const phone = form.querySelector('#wa-phone')?.value.trim() || '';
    const email = form.querySelector('#wa-email')?.value.trim() || '';
    const msg = form.querySelector('#wa-message').value.trim();
    const number = cfg.whatsapp_number || '573177695006';

    const now = new Date();
    const dateStr = now.toLocaleDateString();
    const timeStr = now.toLocaleTimeString();

    const lines = [
      `*Hola ${cfg.company_name || 'IOQUE'}!*`,
      '',
      'Me comunico desde su página web.',
      '',
      `*${t.name}:* ${name}`,
    ];
    if (phone) lines.push(`*${t.phone}:* ${phone}`);
    if (email) lines.push(`*${t.email}:* ${email}`);
    lines.push(
      '',
      `*${t.message}:*`,
      msg || '(Sin mensaje)',
      '',
      `Idioma: ${this._lang.toUpperCase()}`,
      `Fecha: ${dateStr} ${timeStr}`,
    );

    const text = lines.join('\n');
    const url = `https://wa.me/${number}?text=${encodeURIComponent(text)}`;

    window.open(url, '_blank');
    form.reset();
    this._close();
  }

  /* ── Lang observer ────────────────────── */
  _observeLang() {
    this._langObserver = new MutationObserver(() => {
      const lang = this._lang;
      if (lang !== this.getAttribute('lang')) {
        this.setAttribute('lang', lang);
      }
    });
    this._langObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['lang'],
    });
    /* Also listen for storage changes */
    this._addListener(window, 'storage', (e) => {
      if (e.key === STORAGE_LANG_KEY) {
        const lang = this._lang;
        this.setAttribute('lang', lang);
      }
    });
  }

  /* ── Color utils ──────────────────────── */
  _darken(hex, percent) {
    const num = parseInt(hex.replace('#', ''), 16);
    const r = Math.max(0, (num >> 16) - Math.round((num >> 16) * (percent / 100)));
    const g = Math.max(0, ((num >> 8) & 0x00ff) - Math.round(((num >> 8) & 0x00ff) * (percent / 100)));
    const b = Math.max(0, (num & 0x0000ff) - Math.round((num & 0x0000ff) * (percent / 100)));
    return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, '0')}`;
  }
}

/* ── Register & auto-initialize ──────────── */
if (!customElements.get('wa-widget')) {
  customElements.define('wa-widget', WhatsAppWidget);
}

if (!document.querySelector('wa-widget')) {
  const el = document.createElement('wa-widget');
  if (document.body) {
    document.body.appendChild(el);
  } else {
    document.addEventListener('DOMContentLoaded', () => document.body.appendChild(el));
  }
}
