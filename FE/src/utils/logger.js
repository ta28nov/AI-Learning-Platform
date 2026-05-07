const isDev = import.meta.env.DEV

const toErrorPayload = (error, context = {}) => {
  if (!error) return { message: 'Unknown error', context }
  return {
    message: error.message || String(error),
    stack: error.stack || null,
    context
  }
}

export const appLogger = {
  info(message, context = {}) {
    if (isDev) console.info('[APP][INFO]', message, context)
  },
  warn(message, context = {}) {
    if (isDev) console.warn('[APP][WARN]', message, context)
  },
  error(error, context = {}) {
    const payload = toErrorPayload(error, context)
    console.error('[APP][ERROR]', payload)
  }
}

export default appLogger
