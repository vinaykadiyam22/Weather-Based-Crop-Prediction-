import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from '../locales/en.json'
import hi from '../locales/hi.json'
import ta from '../locales/ta.json'
import te from '../locales/te.json'
import bn from '../locales/bn.json'
import mr from '../locales/mr.json'
import gu from '../locales/gu.json'

const LANG_KEY = 'app_language'

export const SUPPORTED_LANGS = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी' },
  { code: 'ta', label: 'தமிழ்' },
  { code: 'te', label: 'తెలుగు' },
  { code: 'bn', label: 'বাংলা' },
  { code: 'mr', label: 'मराठी' },
  { code: 'gu', label: 'ગુજરાતી' },
]

export function getStoredLanguage() {
  return localStorage.getItem(LANG_KEY) || 'en'
}

export function setStoredLanguage(lang) {
  localStorage.setItem(LANG_KEY, lang)
}

/** Use for API calls: prefers current UI language (i18n) so generated content matches selected language. */
export function getEffectiveLanguage(user) {
  return i18n.language || user?.language || getStoredLanguage() || 'en'
}

i18n
  .use(initReactI18next)
  .init({
    resources: { en: { translation: en }, hi: { translation: hi }, ta: { translation: ta }, te: { translation: te }, bn: { translation: bn }, mr: { translation: mr }, gu: { translation: gu } },
    lng: getStoredLanguage(),
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  })

export default i18n
