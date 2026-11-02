import { API_BASE_URL, API_PREFIX } from '../config';
import {
  Catalog,
  NarrationResponse,
  StoryRequest,
  StoryResponse,
  TranscriptionResponse,
  VaultItem,
  VoiceCloneResponse,
} from '../types';

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${API_PREFIX}${path}`, init);
  } catch {
    throw new ApiError(0, 'Cannot reach the story server. Is the backend running?');
  }
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === 'string') detail = body.detail;
      else if (Array.isArray(body.detail) && body.detail[0]?.msg) detail = body.detail[0].msg;
    } catch {
      /* keep default */
    }
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}

const json = (body: unknown): RequestInit => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});

export const api = {
  catalog: () => request<Catalog>('/catalog'),

  generateStory: (body: StoryRequest) => request<StoryResponse>('/story/generate', json(body)),

  /** Read text aloud. `voiceId` (a cloned family voice) overrides the narrator when given. */
  narrate: (text: string, narrator: string, language: string, voiceId?: string | null) =>
    request<NarrationResponse>('/voice/narrate', json({ text, narrator, language, voice_id: voiceId || undefined })),

  transcribe: (audio: Blob, filename: string, language?: string) => {
    const form = new FormData();
    form.append('file', audio, filename);
    if (language) form.append('language', language);
    return request<TranscriptionResponse>('/voice/transcribe', { method: 'POST', body: form });
  },

  cloneVoice: (clip: Blob, filename: string, name: string, language: string) => {
    const form = new FormData();
    form.append('file', clip, filename);
    form.append('name', name);
    form.append('language', language);
    return request<VoiceCloneResponse>('/voice/clone', { method: 'POST', body: form });
  },

  saveStory: (userId: string, story: StoryResponse, audioUrl: string | null) =>
    request<{ story_id: string }>(
      '/vault/save',
      json({
        user_id: userId,
        story_text: story.story_text,
        audio_url: audioUrl,
        meta: { title: story.title, ...story.meta },
      })
    ),

  listStories: async (userId: string): Promise<VaultItem[]> => {
    const data = await request<{ stories: VaultItem[] }>(`/vault/${encodeURIComponent(userId)}`);
    return data.stories ?? [];
  },

  /** Absolute URL for a file the backend serves from /static. */
  mediaUrl: (path: string) => (path.startsWith('http') ? path : `${API_BASE_URL}${path}`),
};
