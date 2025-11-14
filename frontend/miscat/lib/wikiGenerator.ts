import { Message } from './api';

/**
 * メッセージからキーワードを抽出
 */
function extractKeywords(messages: Message[]): string[] {
  const allText = messages.map(m => m.content).join(' ');
  const words = allText.toLowerCase().split(/\s+/);

  // 頻出単語を抽出（簡易版）
  const wordCount: { [key: string]: number } = {};
  words.forEach(word => {
    // 3文字以上の単語のみカウント
    if (word.length >= 3) {
      wordCount[word] = (wordCount[word] || 0) + 1;
    }
  });

  // 頻度順にソートして上位5つを返す
  return Object.entries(wordCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([word]) => word);
}

/**
 * メッセージを日付ごとにグループ化
 */
function groupMessagesByDate(messages: Message[]): { [date: string]: Message[] } {
  const grouped: { [date: string]: Message[] } = {};

  messages.forEach(message => {
    const date = new Date(message.created_at);
    const dateKey = date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });

    if (!grouped[dateKey]) {
      grouped[dateKey] = [];
    }
    grouped[dateKey].push(message);
  });

  return grouped;
}

/**
 * メッセージを話者ごとにグループ化
 */
function groupMessagesBySpeaker(messages: Message[]): { [speaker: string]: Message[] } {
  const grouped: { [speaker: string]: Message[] } = {};

  messages.forEach(message => {
    const speaker = message.sender_username;
    if (!grouped[speaker]) {
      grouped[speaker] = [];
    }
    grouped[speaker].push(message);
  });

  return grouped;
}

/**
 * 会話のサマリーを生成
 */
function generateSummary(messages: Message[]): string {
  if (messages.length === 0) return '';

  const speakers = new Set(messages.map(m => m.sender_username));
  const dateRange = getDateRange(messages);
  const keywords = extractKeywords(messages);

  let summary = `## 概要\n\n`;
  summary += `- 参加者: ${Array.from(speakers).join('、')}\n`;
  summary += `- 期間: ${dateRange}\n`;
  summary += `- メッセージ数: ${messages.length}件\n`;
  if (keywords.length > 0) {
    summary += `- 主なキーワード: ${keywords.join('、')}\n`;
  }
  summary += `\n`;

  return summary;
}

/**
 * 日付範囲を取得
 */
function getDateRange(messages: Message[]): string {
  if (messages.length === 0) return '';

  const dates = messages.map(m => new Date(m.created_at).getTime());
  const minDate = new Date(Math.min(...dates));
  const maxDate = new Date(Math.max(...dates));

  const format = (date: Date) => date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });

  if (format(minDate) === format(maxDate)) {
    return format(minDate);
  }

  return `${format(minDate)} 〜 ${format(maxDate)}`;
}

/**
 * 基本的な会話履歴形式でWikiコンテンツを生成
 */
export function convertMessagesToWikiContent(messages: Message[]): string {
  if (messages.length === 0) {
    return '';
  }

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

/**
 * 高度な自動分析でWikiコンテンツを生成
 */
export function autoGenerateWikiContent(messages: Message[]): string {
  if (messages.length === 0) {
    return '';
  }

  const sortedMessages = [...messages].sort((a, b) =>
    new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  );

  let content = '# 会話記録\n\n';
  content += `このWikiは${sortedMessages.length}件のメッセージから自動生成されました。\n\n`;

  // サマリーを追加
  content += generateSummary(sortedMessages);
  content += `---\n\n`;

  // 日付ごとにグループ化
  const groupedByDate = groupMessagesByDate(sortedMessages);
  const dates = Object.keys(groupedByDate).sort();

  dates.forEach((date) => {
    const dayMessages = groupedByDate[date];
    content += `## ${date}\n\n`;
    content += `**${dayMessages.length}件のメッセージ**\n\n`;

    dayMessages.forEach((message) => {
      const time = new Date(message.created_at).toLocaleTimeString('ja-JP', {
        hour: '2-digit',
        minute: '2-digit',
      });

      content += `### ${time} - ${message.sender_username}\n\n`;
      content += `${message.content}\n\n`;
    });
  });

  // 話者別統計を追加
  content += `---\n\n`;
  content += `## 参加者別統計\n\n`;
  const groupedBySpeaker = groupMessagesBySpeaker(sortedMessages);

  Object.entries(groupedBySpeaker)
    .sort((a, b) => b[1].length - a[1].length)
    .forEach(([speaker, msgs]) => {
      content += `- **${speaker}**: ${msgs.length}件のメッセージ\n`;
    });

  return content;
}

/**
 * タイトルを自動生成
 */
export function generateWikiTitle(
  messages: Message[],
  prefix: string = '会話記録'
): string {
  if (messages.length === 0) {
    return `${prefix} - ${new Date().toLocaleDateString('ja-JP')}`;
  }

  const dateRange = getDateRange(messages);
  const speakers = new Set(messages.map(m => m.sender_username));

  if (speakers.size <= 2) {
    return `${prefix}: ${Array.from(speakers).join(' と ')} (${dateRange})`;
  } else {
    return `${prefix}: ${speakers.size}名の会話 (${dateRange})`;
  }
}
