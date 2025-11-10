import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { DMConversation } from '@/lib/api';

interface DMCardProps {
  dm: DMConversation;
  onClick: () => void;
}

export function DMCard({ dm, onClick }: DMCardProps) {
  // 最終更新時刻の相対表示
  const getRelativeTime = (dateString?: string) => {
    if (!dateString) return '';

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'たった今';
    if (diffMins < 60) return `${diffMins}分前`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}時間前`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}日前`;
  };

  return (
    <Card
      className="hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{dm.partner_username}</CardTitle>
        </div>
        <CardDescription>
          {dm.partner_id}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {dm.last_message && (
          <div className="space-y-1">
            <p className="text-sm text-gray-600 truncate">{dm.last_message}</p>
            {dm.last_message_at && (
              <p className="text-xs text-gray-400">{getRelativeTime(dm.last_message_at)}</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
