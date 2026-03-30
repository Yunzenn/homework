const { createUIMessageStream, pipeUIMessageStreamToResponse } = require('ai')

const DEFAULT_DJANGO_API_BASE_URL = 'http://localhost:8000'

function splitText(text, size = 24) {
  if (!text) return ['']
  const chunks = []
  for (let i = 0; i < text.length; i += size) {
    chunks.push(text.slice(i, i + size))
  }
  return chunks
}

function parseBody(body) {
  if (!body) return {}
  if (typeof body === 'string') {
    try {
      return JSON.parse(body)
    } catch {
      return {}
    }
  }
  return body
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const body = parseBody(req.body)
  const message = body.message || ''
  const context = body.context || {}
  const aiConfig = body.ai_config || null

  if (!message) {
    return res.status(400).json({ error: 'message is required' })
  }

  const djangoApiBaseUrl = (process.env.DJANGO_API_BASE_URL || DEFAULT_DJANGO_API_BASE_URL).replace(/\/$/, '')
  const chatUrl = `${djangoApiBaseUrl}/api/ai/chat/`

  try {
    const headers = {
      'Content-Type': 'application/json'
    }

    if (req.headers.authorization) {
      headers.Authorization = req.headers.authorization
    }

    const djangoResponse = await fetch(chatUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message,
        context,
        ai_config: aiConfig
      })
    })

    if (!djangoResponse.ok) {
      const errorText = await djangoResponse.text()
      return res.status(djangoResponse.status).json({
        error: `Django AI API error: ${errorText || djangoResponse.statusText}`
      })
    }

    const payload = await djangoResponse.json()
    const aiText =
      payload?.data?.data?.message ||
      payload?.data?.message ||
      payload?.message ||
      '处理完成'

    const stream = createUIMessageStream({
      execute: ({ writer }) => {
        const textId = `text-${Date.now()}`
        writer.write({ type: 'text-start', id: textId })

        for (const chunk of splitText(aiText)) {
          writer.write({ type: 'text-delta', id: textId, delta: chunk })
        }

        writer.write({ type: 'text-end', id: textId })
      },
      onError: error => (error instanceof Error ? error.message : 'Stream error')
    })

    pipeUIMessageStreamToResponse({
      response: res,
      stream,
      status: 200,
      headers: {
        'Cache-Control': 'no-cache, no-transform'
      }
    })
  } catch (error) {
    return res.status(500).json({
      error: `Streaming bridge failed: ${error instanceof Error ? error.message : 'unknown error'}`
    })
  }
}
