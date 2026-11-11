// Mirrors backend/catalog.py and backend/models/story_model.py, plus browser-only types.

export interface Option {
  id: string;
  label: string;
  emoji: string;
  hint?: string;
  blurb?: string;
  color?: string;
  minutes?: string;
  guidance?: string;
  /** Narrators only: language codes this narrator can read with the active voice provider. */
  languages?: string[];
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

export interface MoodOption {
  id: string;
  label: string;
  emoji: string;
}

export interface Catalog {
  languages: LanguageOption[];
  themes: Option[];
  feelings: Option[];
  age_groups: Option[];
  lengths: Option[];
  narrators: Option[];
  moods: MoodOption[];
  providers: Record<'llm' | 'tts' | 'stt' | 'video' | 'music' | 'image', ProviderInfo>;
}

export interface Character {
  name: string;
  trait: string;
  /** Small JPEG data URL of a photo or drawing of this character; browser only, guides the paintings. */
  image?: string;
}

/** A character's picture handed to the painter so the pages take after it. */
export interface PictureReference {
  name: string;
  image: string;
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
  /** Titles of recent stories, so the writer does not repeat them. Filled in by the app. */
  avoid?: string[];
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

/** One paragraph and the mood a narrator should read it in (an id from Catalog.moods). */
export interface Paragraph {
  text: string;
  mood: string;
  /** What a picture of this paragraph shows. */
  scene?: string;
}

/** One book page: which paragraphs it holds and what its picture shows. */
export interface StoryPage {
  paragraphs: number[];
  scene: string;
}

export interface StoryArt {
  characters: string;
  cover: string;
}

export interface StoryResponse {
  /** Library record id on the server; empty for previews. */
  id?: string;
  title: string;
  story_text: string;
  meta: StoryMeta;
  /** Overall mood; picks the background music. Missing on stories saved before moods existed. */
  mood?: string;
  music_url?: string | null;
  paragraphs?: Paragraph[];
  pages?: StoryPage[];
  art?: StoryArt | null;
}

export interface IllustrateResponse {
  image_url: string;
  provider: string;
  model: string;
}

/** When narration segment `index` is heard, in seconds from the start of the recording. */
export interface NarrationCue {
  index: number;
  start: number;
  end: number;
}

/** A passage to read aloud with a mood. Mood may be empty for a plain reading. */
export interface NarrationSegment {
  text: string;
  mood: string;
}

export interface NarrationResponse {
  audio_url: string;
  provider: string;
  voice: string;
  /** True when background music is mixed into the file. */
  music: boolean;
  cues?: NarrationCue[];
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

export type ShareStatus = 'private' | 'pending' | 'published' | 'rejected';

/** A story record on the server: the family's copy with recording and pictures. */
export interface LibraryRecord extends StoryResponse {
  id: string;
  status: ShareStatus;
  audio_url: string | null;
  cues: NarrationCue[];
  pictures: Record<string, string>;
  has_personal_pictures: boolean;
  published_at: string | null;
  review_note: string;
  owner_name: string;
  created_at: string;
  language: string;
  voice_name?: string;
}

/** A published story's cover on the community shelf. */
export interface CommunityItem {
  id: string;
  title: string;
  meta: StoryMeta;
  mood: string;
  pictures: { cover?: string | null };
  published_at: string | null;
  owner_name: string;
  language: string;
  has_audio: boolean;
}

export interface Allowance {
  free_total: number;
  free_left: number;
  credits: number;
  unlimited: boolean;
  admin: boolean;
}

export interface Me {
  id: string;
  email: string;
  name: string;
  guest: boolean;
  allowance: Allowance;
}

/** A story kept in this browser's library (and best-effort in the vault). */
export interface SavedStory {
  id: string;
  story: StoryResponse;
  audioUrl: string | null;
  audioCues?: NarrationCue[];
  voiceName: string | null;
  createdAt: string;
  /** Picture URLs by key: "cover" and "page-0", "page-1", ... */
  pictures?: Record<string, string>;
}

/** A family voice cloned from a short recording. */
export interface CustomVoice {
  id: string;
  name: string;
  language: string;
  createdAt: string;
}
