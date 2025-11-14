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
import {
  convertMessagesToWikiContent,
  autoGenerateWikiContent,
  generateWikiTitle,
} from '@/lib/wikiGenerator';
import { Sparkles } from 'lucide-react';

interface CreateWikiFromMessagesDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  messages: Message[];
  defaultTitle: string;
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
  const [generationMode, setGenerationMode] = useState<'basic' | 'auto'>('basic');

  // ダイアログが開かれたときにコンテンツを生成
  const handleOpenChange = (newOpen: boolean) => {
    if (newOpen && messages.length > 0) {
      setContent(convertMessagesToWikiContent(messages));
      setTitle(defaultTitle);
      setGenerationMode('basic');
    }
    onOpenChange(newOpen);
  };

  // 自動生成モードに切り替え
  const handleAutoGenerate = () => {
    if (messages.length === 0) return;

    const autoContent = autoGenerateWikiContent(messages);
    const autoTitle = generateWikiTitle(messages, defaultTitle.split(':')[0]);

    setContent(autoContent);
    setTitle(autoTitle);
    setGenerationMode('auto');
    toast.success('高度な分析でWikiを自動生成しました');
  };

  // 基本モードに戻す
  const handleBasicGenerate = () => {
    if (messages.length === 0) return;

    const basicContent = convertMessagesToWikiContent(messages);
    setContent(basicContent);
    setTitle(defaultTitle);
    setGenerationMode('basic');
    toast.success('基本形式でWikiを生成しました');
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
          {/* 生成モード切り替え */}
          <div className="flex gap-2">
            <Button
              type="button"
              variant={generationMode === 'basic' ? 'default' : 'outline'}
              size="sm"
              onClick={handleBasicGenerate}
              disabled={isCreating}
              className="flex-1"
            >
              基本形式
            </Button>
            <Button
              type="button"
              variant={generationMode === 'auto' ? 'default' : 'outline'}
              size="sm"
              onClick={handleAutoGenerate}
              disabled={isCreating}
              className="flex-1"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              自動分析
            </Button>
          </div>

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
              {generationMode === 'auto' && ' | 自動分析モード'}
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
