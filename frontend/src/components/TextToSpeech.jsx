import { useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { FiVolume2, FiSquare } from 'react-icons/fi'
import './TextToSpeech.css'

/** Maps our language codes to Web Speech API lang codes */
const LANG_TO_SPEECH = {
  en: 'en-IN',
  hi: 'hi-IN',
  ta: 'ta-IN',
  te: 'te-IN',
  bn: 'bn-IN',
  mr: 'mr-IN',
  gu: 'gu-IN',
}

/** Strip markdown for plain-text TTS */
function stripMarkdown(text) {
  if (!text || typeof text !== 'string') return ''
  return text
    .replace(/^##\s+/gm, '')
    .replace(/^#\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/^-\s+/gm, '')
    .replace(/^\d+\.\s+/gm, '')
    .replace(/\n+/g, '. ')
    .trim()
}

function TextToSpeech({ text, language = 'en', className = '' }) {
  const { t } = useTranslation()
  const [speaking, setSpeaking] = useState(false)

  const handleSpeak = useCallback(() => {
    if (!text || typeof text !== 'string') return

    const plainText = stripMarkdown(text)
    if (!plainText) return

    if (speaking) {
      window.speechSynthesis.cancel()
      setSpeaking(false)
      return
    }

    if (!window.speechSynthesis) {
      console.warn('Speech synthesis not supported')
      return
    }

    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(plainText)
    utterance.lang = LANG_TO_SPEECH[language] || 'en-IN'
    utterance.rate = 0.9
    utterance.pitch = 1
    utterance.volume = 1

    utterance.onstart = () => setSpeaking(true)
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)

    window.speechSynthesis.speak(utterance)
  }, [text, language, speaking])

  if (!text || typeof text !== 'string') return null

  return (
    <button
      type="button"
      className={`tts-btn ${className} ${speaking ? 'speaking' : ''}`}
      onClick={handleSpeak}
      title={speaking ? t('common.stopReading') : t('common.listenToAdvisory')}
      aria-label={speaking ? t('common.stopReading') : t('common.listenToAdvisory')}
    >
      {speaking ? (
        <FiSquare size={18} aria-hidden />
      ) : (
        <FiVolume2 size={18} aria-hidden />
      )}
      <span>{speaking ? t('common.stop') : t('common.listen')}</span>
    </button>
  )
}

export default TextToSpeech
