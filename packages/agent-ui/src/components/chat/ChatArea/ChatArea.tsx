'use client'

import ChatInput from './ChatInput'
import MessageArea from './MessageArea'

const ChatArea = () => {
  return (
    <main className="relative m-1.5 flex h-full flex-col overflow-hidden rounded-xl bg-background">
      <div className="min-h-0 flex-1">
        <MessageArea />
      </div>
      <div className="shrink-0 border-t border-border bg-background px-4 pb-4 pt-3">
        <ChatInput />
      </div>
    </main>
  )
}

export default ChatArea
