import React, { useState } from 'react';
import { 
  StoryGenerationRequest, 
  StoryGenerationResponse, 
  StoryType, 
  Mood, 
  NarratorStyle, 
  Language,
  Character,
  MoodOption,
  StoryTypeOption
} from '../types/api';
import { apiService } from '../services/apiService';
import './StoryGenerator.css';

const StoryGenerator: React.FC = () => {
  const [formData, setFormData] = useState<StoryGenerationRequest>({
    story_type: StoryType.ADVENTURE,
    mood: Mood.SOOTHING,
    narrator_style: NarratorStyle.WISE_GRANDPARENT,
    language: Language.ENGLISH,
    custom_characters: [],
    private_prompt: '',
  });

  const [characters, setCharacters] = useState<Character[]>([]);
  const [story, setStory] = useState<StoryGenerationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showResult, setShowResult] = useState(false);

  const storyTypeOptions: StoryTypeOption[] = [
    { value: StoryType.ADVENTURE, emoji: '🗺️', label: 'Adventure', description: 'Exciting journeys and quests', color: '#FF6B6B' },
    { value: StoryType.MORAL, emoji: '💭', label: 'Moral', description: 'Life lessons and wisdom', color: '#4ECDC4' },
    { value: StoryType.FANTASY, emoji: '🧙‍♂️', label: 'Fantasy', description: 'Magic and mythical worlds', color: '#45B7D1' },
    { value: StoryType.COMEDY, emoji: '😄', label: 'Comedy', description: 'Fun and laughter', color: '#FFA07A' },
    { value: StoryType.MYSTERY, emoji: '🕵️', label: 'Mystery', description: 'Puzzles and secrets', color: '#9B59B6' },
    { value: StoryType.SCIFI, emoji: '🚀', label: 'Sci-Fi', description: 'Future and technology', color: '#3498DB' },
    { value: StoryType.HISTORICAL, emoji: '🏛️', label: 'Historical', description: 'Past times and cultures', color: '#E67E22' },
    { value: StoryType.FAIRY_TALE, emoji: '🧚‍♀️', label: 'Fairy Tale', description: 'Classic magical stories', color: '#E91E63' },
    { value: StoryType.DRAMA, emoji: '🎭', label: 'Drama', description: 'Emotional narratives', color: '#795548' },
  ];

  const moodOptions: MoodOption[] = [
    { value: Mood.SOOTHING, emoji: '😌', label: 'Soothing', color: '#A8E6CF', bgGradient: 'linear-gradient(135deg, #A8E6CF 0%, #7FCDCD 100%)' },
    { value: Mood.JOYFUL, emoji: '😊', label: 'Joyful', color: '#FFD93D', bgGradient: 'linear-gradient(135deg, #FFD93D 0%, #FF6B6B 100%)' },
    { value: Mood.MAGICAL, emoji: '✨', label: 'Magical', color: '#DDA0DD', bgGradient: 'linear-gradient(135deg, #DDA0DD 0%, #9370DB 100%)' },
    { value: Mood.INTENSE, emoji: '⚡', label: 'Intense', color: '#FF6B6B', bgGradient: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)' },
    { value: Mood.HEALING, emoji: '🌿', label: 'Healing', color: '#98FB98', bgGradient: 'linear-gradient(135deg, #98FB98 0%, #90EE90 100%)' },
    { value: Mood.INSPIRING, emoji: '🌟', label: 'Inspiring', color: '#87CEEB', bgGradient: 'linear-gradient(135deg, #87CEEB 0%, #4682B4 100%)' },
    { value: Mood.SUSPENSEFUL, emoji: '🌙', label: 'Suspenseful', color: '#708090', bgGradient: 'linear-gradient(135deg, #708090 0%, #2F4F4F 100%)' },
  ];

  const narratorStyles = [
    { value: NarratorStyle.WISE_GRANDPARENT, label: '👴 Wise Grandparent', description: 'Warm and experienced voice' },
    { value: NarratorStyle.CHILDS_VOICE, label: '👶 Child\'s Voice', description: 'Innocent and playful' },
    { value: NarratorStyle.CELEBRITY, label: '🌟 Celebrity-style', description: 'Charismatic and engaging' },
    { value: NarratorStyle.NEUTRAL_AI, label: '🤖 Neutral AI', description: 'Clear and professional' },
    { value: NarratorStyle.INDIAN_ENGLISH, label: '🇮🇳 Indian English', description: 'Cultural and melodic' },
    { value: NarratorStyle.SELF, label: '👤 Self', description: 'Personal narrative style' },
  ];

  const addCharacter = () => {
    const newCharacter: Character = { name: '', age: 5, trait: '' };
    setCharacters([...characters, newCharacter]);
  };

  const updateCharacter = (index: number, field: keyof Character, value: string | number) => {
    const updatedCharacters = characters.map((char, i) => 
      i === index ? { ...char, [field]: value } : char
    );
    setCharacters(updatedCharacters);
    setFormData({ ...formData, custom_characters: updatedCharacters.filter(c => c.name.trim() !== '') });
  };

  const removeCharacter = (index: number) => {
    const updatedCharacters = characters.filter((_, i) => i !== index);
    setCharacters(updatedCharacters);
    setFormData({ ...formData, custom_characters: updatedCharacters });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const requestData = {
        ...formData,
        custom_characters: characters.filter(c => c.name.trim() !== ''),
      };
      
      const response = await apiService.generateStory(requestData);
      setStory(response);
      setShowResult(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      story_type: StoryType.ADVENTURE,
      mood: Mood.SOOTHING,
      narrator_style: NarratorStyle.WISE_GRANDPARENT,
      language: Language.ENGLISH,
      custom_characters: [],
      private_prompt: '',
    });
    setCharacters([]);
    setStory(null);
    setShowResult(false);
    setError(null);
  };

  return (
    <div className="story-generator">
      <div className="container">
        <header className="hero-section">
          <div className="hero-content">
            <h1 className="hero-title">
              <span className="gradient-text">StoryMood</span>
              <span className="sparkle">✨</span>
            </h1>
            <p className="hero-subtitle">
              Create magical stories that touch hearts and inspire minds
            </p>
          </div>
          <div className="floating-shapes">
            <div className="shape shape-1"></div>
            <div className="shape shape-2"></div>
            <div className="shape shape-3"></div>
          </div>
        </header>

        {!showResult ? (
          <form onSubmit={handleSubmit} className="story-form">
            <div className="form-grid">
              {/* Story Type Selection */}
              <div className="form-section">
                <h3 className="section-title">
                  Choose Your Story Type
                </h3>
                <div className="story-type-grid">
                  {storyTypeOptions.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      className={`story-type-card ${formData.story_type === option.value ? 'selected' : ''}`}
                      onClick={() => setFormData({ ...formData, story_type: option.value })}
                      style={{ '--card-color': option.color } as React.CSSProperties}
                    >
                      <div className="card-emoji">{option.emoji}</div>
                      <div className="card-label">{option.label}</div>
                      <div className="card-description">{option.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Mood Selection */}
              <div className="form-section">
                <h3 className="section-title">
                  Set the Mood
                </h3>
                <div className="mood-grid">
                  {moodOptions.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      className={`mood-card ${formData.mood === option.value ? 'selected' : ''}`}
                      onClick={() => setFormData({ ...formData, mood: option.value })}
                      style={{ '--mood-bg': option.bgGradient } as React.CSSProperties}
                    >
                      <div className="mood-emoji">{option.emoji}</div>
                      <div className="mood-label">{option.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Narrator Style */}
              <div className="form-section">
                <h3 className="section-title">
                  <span className="section-icon">🎙️</span>
                  Choose Narrator Voice
                </h3>
                <div className="narrator-grid">
                  {narratorStyles.map((style) => (
                    <div
                      key={style.value}
                      className={`narrator-card ${formData.narrator_style === style.value ? 'selected' : ''}`}
                      onClick={() => setFormData({ ...formData, narrator_style: style.value })}
                    >
                      <div className="narrator-label">{style.label}</div>
                      <div className="narrator-description">{style.description}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Language Selection */}
              <div className="form-section">
                <h3 className="section-title">
                  <span className="section-icon">🌍</span>
                  Language
                </h3>
                <select
                  className="language-select"
                  value={formData.language}
                  onChange={(e) => setFormData({ ...formData, language: e.target.value as Language })}
                >
                  {Object.values(Language).map((lang) => (
                    <option key={lang} value={lang}>{lang}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Advanced Options */}
            <div className="advanced-section">
              <button
                type="button"
                className="advanced-toggle"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                <span>Advanced Options</span>
                <span className={`toggle-icon ${showAdvanced ? 'open' : ''}`}>▼</span>
              </button>

              {showAdvanced && (
                <div className="advanced-content">
                  {/* Custom Characters */}
                  <div className="form-section">
                    <h3 className="section-title">
                      <span className="section-icon">👥</span>
                      Custom Characters
                    </h3>
                    <div className="characters-container">
                      {characters.map((character, index) => (
                        <div key={index} className="character-row">
                          <div className="character-field">
                            <label className="character-field-label">Name</label>
                            <input
                              type="text"
                              placeholder="e.g. Arjun"
                              value={character.name}
                              onChange={(e) => updateCharacter(index, 'name', e.target.value)}
                              className="character-input"
                            />
                          </div>
                          <div className="character-field character-field-age">
                            <label className="character-field-label">Age</label>
                            <input
                              type="number"
                              placeholder="e.g. 8"
                              value={character.age}
                              onChange={(e) => updateCharacter(index, 'age', parseInt(e.target.value) || 0)}
                              className="character-input age-input"
                              min="1"
                              max="100"
                            />
                          </div>
                          <div className="character-field">
                            <label className="character-field-label">Trait</label>
                            <input
                              type="text"
                              placeholder="e.g. brave, curious"
                              value={character.trait}
                              onChange={(e) => updateCharacter(index, 'trait', e.target.value)}
                              className="character-input"
                            />
                          </div>
                          <button
                            type="button"
                            className="remove-character"
                            onClick={() => removeCharacter(index)}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                      <button type="button" className="add-character" onClick={addCharacter}>
                        + Add Character
                      </button>
                    </div>
                  </div>

                  {/* Private Prompt */}
                  <div className="form-section">
                    <h3 className="section-title">
                      <span className="section-icon">✍️</span>
                      Special Instructions
                    </h3>
                    <textarea
                      className="private-prompt"
                      placeholder="Include specific elements, themes, or details you'd like in the story..."
                      value={formData.private_prompt}
                      onChange={(e) => setFormData({ ...formData, private_prompt: e.target.value })}
                      rows={4}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Error Display */}
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                <span className="error-text">{error}</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="form-actions">
              <button type="submit" className="generate-btn" disabled={loading}>
                {loading ? (
                  <>
                    <div className="loading-spinner"></div>
                    <span>Creating Magic...</span>
                  </>
                ) : (
                  <>
                    <span className="btn-icon">✨</span>
                    <span>Generate Story</span>
                  </>
                )}
              </button>
              <button type="button" className="reset-btn" onClick={resetForm}>
                <span className="btn-icon">🔄</span>
                <span>Reset</span>
              </button>
            </div>
          </form>
        ) : (
          <div className="story-result">
            <div className="result-header">
              <h2 className="result-title">Your Story is Ready!</h2>
              <div className="result-metadata">
                <span className="metadata-item">
                  <span className="metadata-icon">📚</span>
                  {story?.meta.story_type}
                </span>
                <span className="metadata-item">
                  <span className="metadata-icon">🎭</span>
                  {story?.meta.mood}
                </span>
                <span className="metadata-item">
                  <span className="metadata-icon">⏱️</span>
                  {story?.meta.estimated_duration}
                </span>
              </div>
            </div>

            <div className="story-content">
              <div className="story-text">
                {story?.story_text.split('\n').map((paragraph, index) => (
                  <p key={index} className="story-paragraph">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>

            <div className="result-actions">
              <button className="action-btn primary" onClick={() => setShowResult(false)}>
                <span className="btn-icon">🔄</span>
                Create Another Story
              </button>
              <button className="action-btn secondary">
                <span className="btn-icon">💾</span>
                Save Story
              </button>
              <button className="action-btn secondary">
                <span className="btn-icon">📤</span>
                Share
              </button>
              <button className="action-btn secondary">
                <span className="btn-icon">🎵</span>
                Generate Audio
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StoryGenerator;