'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { createWikiPage, Message } from '@/lib/api';
import { toast } from 'sonner';

interface CreateWikiFromMessagesDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  messages: Message[];
  defaultTitle: string;
}

/**
 * メッセージをWikiコンテンツに変換する関数
 */
function convertMessagesToWikiContent(messages: Message[]): string {
  if (messages.length === 0) {
    return '';
  }

  // メッセージを時系列順にソート（古い順）
  const sortedMessages = [...messages].sort((a, b) =>
    new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  );

  let content = '# 会話履歴\n\n';
  content += `このWikiは会話履歴から自動生成されました。\n\n`;
  content += `---\n\n`;

  sortedMessages.forEach((message, index) => {
    const date = new Date(message.created_at);
    const timeStr = date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });

    content += `## ${index + 1}. ${message.sender_username} (${timeStr})\n\n`;
    content += `${message.content}\n\n`;
  });

  return content;
}

export function CreateWikiFromMessagesDialog({
  open,
  onOpenChange,
  messages,
  defaultTitle,
}: CreateWikiFromMessagesDialogProps) {
  const router = useRouter();
  const [title, setTitle] = useState(defaultTitle);
  const [content, setContent] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  // ダイアログが開かれたときにコンテンツを生成
  const handleOpenChange = (newOpen: boolean) => {
    if (newOpen && messages.length > 0) {
      setContent(convertMessagesToWikiContent(messages));
    }
    onOpenChange(newOpen);
  };

  // Wiki作成
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      toast.error('タイトルを入力してください');
      return;
    }

    if (messages.length === 0) {
      toast.error('メッセージがありません');
      return;
    }

    setIsCreating(true);

    try {
      const newPage = await createWikiPage({
        title: title.trim(),
        content: content.trim(),
      });

      toast.success('Wikiページを作成しました');
      onOpenChange(false);

      // 作成したWikiページに遷移
      router.push(`/wiki/${newPage.id}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        toast.error('Wikiの作成に失敗しました: ' + err.message);
      } else {
        toast.error('Wikiの作成に失敗しました');
      }
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>会話をWikiにまとめる</DialogTitle>
          <DialogDescription>
            会話履歴からWikiページを作成します。タイトルと内容を確認・編集してください。
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleCreate} className="space-y-4 py-4">
          {/* タイトル */}
          <div className="space-y-2">
            <label htmlFor="title" className="text-sm font-medium">
              タイトル <span className="text-red-500">*</span>
            </label>
            <Input
              id="title"
              type="text"
              placeholder="Wikiページのタイトル"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={isCreating}
              required
            />
          </div>

          {/* コンテンツプレビュー */}
          <div className="space-y-2">
            <label htmlFor="content" className="text-sm font-medium">
              内容（編集可能）
            </label>
            <Textarea
              id="content"
              placeholder="Wikiページの内容"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              disabled={isCreating}
              rows={12}
              className="font-mono text-sm"
            />
            <p className="text-xs text-gray-500">
              {messages.length}件のメッセージから生成されました
            </p>
          </div>

          {/* ボタン */}
          <div className="flex justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isCreating}
            >
              キャンセル
            </Button>
            <Button type="submit" disabled={isCreating}>
              {isCreating ? '作成中...' : 'Wikiを作成'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
