import { auth } from '../auth';
import { API_BASE_URL, API_PREFIX } from '../config';
import {
  Catalog,
  CommunityItem,
  IllustrateResponse,
  LibraryRecord,
  Me,
  NarrationResponse,
  PictureReference,
  NarrationSegment,
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

/** Hooks the app sets so every request carries who is asking. */
export const requestContext: { guestId: string; onUnauthorized: () => void } = { guestId: '', onUnauthorized: () => undefined };

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  const headers = new Headers(init.headers || {});
  const token = await auth.token();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  else if (requestContext.guestId) headers.set('X-User-Id', requestContext.guestId);
  try {
    response = await fetch(`${API_BASE_URL}${API_PREFIX}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(0, 'Cannot reach the story server. Is the backend running?');
  }
  if (response.status === 401) requestContext.onUnauthorized();
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

  generateStory: (body: StoryRequest) =>
    request<StoryResponse>(
      '/story/generate',
      json({ ...body, characters: body.characters.map(({ name, trait }) => ({ name, trait })) }) // pictures stay out of the story request
    ),

  /**
   * Read passages aloud, each in its mood, with mood-matched music mixed underneath when
   * `music` is on. `voiceId` (a cloned family voice) overrides the narrator when given.
   */
  narrate: (
    segments: NarrationSegment[],
    narrator: string,
    language: string,
    options: { voiceId?: string | null; music?: boolean; storyId?: string } = {}
  ) =>
    request<NarrationResponse>(
      '/voice/narrate',
      json({
        text: segments.map((s) => s.text).join('\n\n'),
        segments,
        narrator,
        language,
        voice_id: options.voiceId || undefined,
        music: options.music ?? true,
        story_id: options.storyId || '',
      })
    ),

  /** Paint one picture for a page or the cover, optionally guided by the characters' pictures. */
  illustrate: (body: {
    title: string;
    scene: string;
    characters: string;
    kind: 'page' | 'cover';
    references?: PictureReference[];
    story_id?: string;
    key?: string;
  }) => request<IllustrateResponse>('/story/illustrate', json(body)),

  me: () => request<Me>('/auth/me'),

  // ---- the family's library on the server, and the community shelf ----
  myStories: () => request<LibraryRecord[]>('/library/mine'),
  publish: (id: string, consent: boolean) => request<LibraryRecord>(`/library/${id}/publish`, json({ consent })),
  unpublish: (id: string) => request<LibraryRecord>(`/library/${id}/unpublish`, { method: 'POST' }),
  community: (language?: string) => request<CommunityItem[]>(`/community${language ? `?language=${language}` : ''}`),
  communityStory: (id: string) => request<LibraryRecord>(`/community/${id}`),
  report: (id: string, reason: string) => request<{ message: string }>(`/community/${id}/report`, json({ reason })),
  reviewQueue: () => request<LibraryRecord[]>('/admin/review'),
  review: (id: string, decision: 'approve' | 'reject', note = '') => request<LibraryRecord>(`/admin/review/${id}`, json({ decision, note })),

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
