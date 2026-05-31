// TypeScript interfaces matching the backend models

export enum StoryType {
  ADVENTURE = "Adventure",
  MORAL = "Moral",
  COMEDY = "Comedy",
  SCIFI = "Sci-Fi",
  FANTASY = "Fantasy",
  HISTORICAL = "Historical",
  MYSTERY = "Mystery",
  FAIRY_TALE = "Fairy Tale",
  DRAMA = "Drama"
}

export enum Mood {
  SOOTHING = "Soothing",
  INTENSE = "Intense",
  JOYFUL = "Joyful",
  HEALING = "Healing",
  INSPIRING = "Inspiring",
  SUSPENSEFUL = "Suspenseful",
  MAGICAL = "Magical"
}

export enum Language {
  ENGLISH = "English",
  HINDI = "Hindi",
  TELUGU = "Telugu",
  TAMIL = "Tamil",
  MALAYALAM = "Malayalam"
}

export enum NarratorStyle {
  WISE_GRANDPARENT = "Wise Grandparent",
  CHILDS_VOICE = "Child's Voice",
  CELEBRITY = "Celebrity-style",
  NEUTRAL_AI = "Neutral AI",
  INDIAN_ENGLISH = "Indian English",
  SELF = "Self"
}

export interface Character {
  name: string;
  age: number;
  trait: string;
}

export interface StoryGenerationRequest {
  story_type: StoryType;
  mood: Mood;
  narrator_style: NarratorStyle;
  language?: Language;
  custom_characters?: Character[];
  private_prompt?: string;
}

export interface StoryMetadata {
  estimated_duration: string;
  story_type: StoryType;
  mood: Mood;
  narrator_style: NarratorStyle;
  language: Language;
  characters: string[];
}

export interface StoryGenerationResponse {
  story_text: string;
  meta: StoryMetadata;
}

export interface ApiError {
  detail: string;
}

// UI specific types
export interface MoodOption {
  value: Mood;
  emoji: string;
  label: string;
  color: string;
  bgGradient: string;
}

export interface StoryTypeOption {
  value: StoryType;
  emoji: string;
  label: string;
  description: string;
  color: string;
}