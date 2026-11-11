/** Frontend settings. Values come from frontend/.env at build time (CRA exposes REACT_APP_*). */
export const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace(/\/$/, '');
export const API_PREFIX = '/api/v1';

/** Longest voice recording we accept before stopping automatically, in seconds. */
export const MAX_RECORDING_SECONDS = 60;
