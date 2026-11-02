// Mirrors storyarc/catalog.py and storyarc/models/story_model.py, plus browser-only types.

export interface Option {
  id: string;
  label: string;
  emoji: string;
  hint?: string;
  blurb?: string;
  color?: string;
  minutes?: string;
  guidance?: string;
}

export interface LanguageOption {
  code: string;
  label: string;
  native: string;
  emoji: string;
}

export interface ProviderInfo {
  provider: string;
  model: string;
  enabled: 'true' | 'false';
  cloning?: 'true' | 'false';
  error?: string;
}

export interface Catalog {
  languages: LanguageOption[];
  themes: Option[];
  feelings: Option[];
  age_groups: Option[];
  lengths: Option[];
  narrators: Option[];
  providers: Record<'llm' | 'tts' | 'stt' | 'video', ProviderInfo>;
}

export interface Character {
  name: string;
  trait: string;
}

export interface StoryRequest {
  theme: string;
  feeling: string;
  age_group: string;
  length: string;
  language: string;
  narrator: string;
  characters: Character[];
  idea: string;
}

export interface StoryMeta {
  theme: string;
  feeling: string;
  age_group: string;
  length: string;
  language: string;
  narrator: string;
  characters: string[];
  word_count: number;
  estimated_minutes: number;
  provider: string;
  model: string;
}

export interface StoryResponse {
  title: string;
  story_text: string;
  meta: StoryMeta;
}

export interface NarrationResponse {
  audio_url: string;
  provider: string;
  voice: string;
}

export interface TranscriptionResponse {
  text: string;
  language: string | null;
  provider: string;
}

export interface VoiceCloneResponse {
  voice_id: string;
  name: string;
  provider: string;
}

export interface VaultItem {
  story_id: string;
  user_id: string;
  story_text: string;
  audio_url: string | null;
  meta: Record<string, unknown> & { title?: string };
  created_at: string;
}

/** A story kept in this browser's library (and best-effort in the vault). */
export interface SavedStory {
  id: string;
  story: StoryResponse;
  audioUrl: string | null;
  voiceName: string | null;
  createdAt: string;
}

/** A family voice cloned from a short recording. */
export interface CustomVoice {
  id: string;
  name: string;
  language: string;
  createdAt: string;
}
