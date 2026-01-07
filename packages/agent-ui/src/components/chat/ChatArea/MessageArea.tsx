'use client'

import { useStore } from '../../../store'
import Messages from './Messages'
import ScrollToBottom from './ScrollToBottom'
import { StickToBottom } from 'use-stick-to-bottom'

const MessageArea = () => {
  const { messages } = useStore()

  return (
    <StickToBottom
      className="relative flex h-full flex-col"
      resize="smooth"
      initial="smooth"
    >
      <StickToBottom.Content className="flex flex-1 flex-col overflow-y-auto pt-4">
        <div className="mx-auto w-full max-w-2xl space-y-9 px-4 pb-4">
          <Messages messages={messages} />
        </div>
      </StickToBottom.Content>
      <ScrollToBottom />
    </StickToBottom>
  )
}

export default MessageArea
