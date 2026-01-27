import React from 'react'
import Card, { CardHeader, CardBody } from '@components/ui/Card'
import Button from '@components/ui/Button'
import Input from '@components/ui/Input'

/**
 * Component ChatPage - Trang trò chuyện
 */
const ChatPage = () => {
  return (
    <div className="chat-page">
      <div className="page-header">
        <h1>Trò chuyện</h1>
        <p>Tương tác với AI và cộng đồng</p>
      </div>

      <div className="chat-content">
        <Card className="chat-container">
          <CardHeader>
            <h3>Chat với AI Assistant</h3>
          </CardHeader>
          <CardBody>
            <div className="chat-messages">
              <div className="message ai-message">
                <div className="message-content">
                  Xin chào! Tôi có thể giúp gì cho bạn hôm nay?
                </div>
                <div className="message-time">Vừa xong</div>
              </div>
            </div>
            
            <div className="chat-input">
              <div className="input-group">
                <Input 
                  placeholder="Nhập tin nhắn của bạn..."
                  className="chat-text-input"
                />
                <Button>Gửi</Button>
              </div>
            </div>
          </CardBody>
        </Card>

        <Card className="chat-sidebar">
          <CardHeader>
            <h3>Các cuộc trò chuyện</h3>
          </CardHeader>
          <CardBody>
            <div className="chat-list">
              <div className="chat-item active">
                <div className="chat-title">Chat với AI</div>
                <div className="chat-preview">Xin chào! Tôi có thể...</div>
              </div>
            </div>
            <Button variant="outline" className="new-chat-btn">
              Cuộc trò chuyện mới
            </Button>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

export default ChatPage