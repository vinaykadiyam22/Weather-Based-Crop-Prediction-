import ReactMarkdown from 'react-markdown'
import TextToSpeech from './TextToSpeech'

/** Renders structured advisory content (markdown) for UI display. Optional TTS when language is provided. */
export default function AdvisoryMarkdown({ content, className = '', language }) {
  if (!content || typeof content !== 'string') return null
  return (
    <div className={`advisory-markdown-wrapper ${className}`}>
      {language && (
        <div className="advisory-tts-row">
          <TextToSpeech text={content} language={language} />
        </div>
      )}
      <div className="advisory-markdown">
        <ReactMarkdown
          components={{
            h2: ({ children }) => <h3 className="advisory-heading">{children}</h3>,
            h3: ({ children }) => <h4 className="advisory-subheading">{children}</h4>,
            ul: ({ children }) => <ul className="advisory-list">{children}</ul>,
            p: ({ children }) => <p className="advisory-para">{children}</p>,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  )
}
