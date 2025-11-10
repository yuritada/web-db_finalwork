import { Card, CardContent } from '@/components/ui/card';
import { Message } from '@/lib/api';

interface MessageCardProps {
  message: Message;
  isOwnMessage: boolean;
}

export function MessageCard({ message, isOwnMessage }: MessageCardProps) {
  return (
    <div className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-4`}>
      <Card className={`max-w-[70%] ${isOwnMessage ? 'bg-sky-50' : 'bg-white'}`}>
        <CardContent className="pt-4 pb-3 px-4">
          <div className="flex flex-col">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-semibold text-gray-900">
                {message.sender_username}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(message.created_at).toLocaleString('ja-JP', {
                  month: 'numeric',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{message.content}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
