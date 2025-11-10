import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ChannelPublic } from '@/lib/api';

interface ChannelCardProps {
  channel: ChannelPublic;
  onClick: () => void;
}

export function ChannelCard({ channel, onClick }: ChannelCardProps) {
  return (
    <Card
      className="hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">#{channel.name}</CardTitle>
          {channel.is_private && (
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              🔒 プライベート
            </span>
          )}
        </div>
        {channel.description && (
          <CardDescription className="mt-2">{channel.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent>
        <p className="text-xs text-gray-500">
          チャンネルID: {channel.id}
        </p>
      </CardContent>
    </Card>
  );
}
