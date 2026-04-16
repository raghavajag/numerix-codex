export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  videoUrl?: string;
  isError?: boolean;
  isStreaming?: boolean;
  timestamp: Date;
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

export interface ApiResponse {
  result: string;
  status: 'success' | 'non_animation' | 'error';
}
