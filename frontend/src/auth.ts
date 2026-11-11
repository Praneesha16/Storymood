/**
 * Accounts for grown-ups: email + password, with Amazon Cognito holding the credentials.
 *
 * - Create account: our API creates it in Cognito (so no email code is needed) and the browser
 *   signs in straight away. The password is sent over HTTPS to Cognito and never stored by us.
 * - Sign in: the browser talks to Cognito's public user-pool API directly and gets signed tokens.
 * - Optional: Google sign-in when connected to the pool.
 * - Forgot password: Cognito emails a reset code; that is the one place a code is used.
 *
 * Tokens live in this browser only and are verified by the API on every request.
 */
import { API_BASE_URL, API_PREFIX } from './config';

export interface AuthConfig {
  mode: 'none' | 'cognito';
  region: string;
  user_pool_id: string;
  client_id: string;
  domain: string;
  /** Only set when testing against a local Cognito emulator. */
  endpoint?: string;
  google: boolean;
}

export interface Session {
  idToken: string;
  accessToken: string;
  refreshToken?: string;
  expiresAt: number; // ms since epoch, with a safety margin
  email: string;
  name: string;
}

const STORE = 'storymood.session';
const PKCE = 'storymood.pkce';
const TARGET = 'AWSCognitoIdentityProviderService.';

let session: Session | null = load();
let authConfig: AuthConfig | null = null;

function load(): Session | null {
  try {
    const raw = localStorage.getItem(STORE);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

function save(next: Session | null) {
  session = next;
  try {
    if (next) localStorage.setItem(STORE, JSON.stringify(next));
    else localStorage.removeItem(STORE);
  } catch {
    /* storage blocked: the session lives in memory for this tab */
  }
}

function base64url(bytes: ArrayBuffer): string {
  return btoa(Array.from(new Uint8Array(bytes), (b) => String.fromCharCode(b)).join(''))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function randomString(bytes = 32): string {
  const buf = new Uint8Array(bytes);
  crypto.getRandomValues(buf);
  return base64url(buf.buffer);
}

async function sha256(text: string): Promise<string> {
  return base64url(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text)));
}

function redirectUri(): string {
  return `${window.location.origin}/`;
}

function decodeClaims(idToken: string): { email?: string; name?: string; given_name?: string; exp?: number } {
  try {
    const payload = idToken.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(payload));
  } catch {
    return {};
  }
}

export class AuthError extends Error {
  code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

/** Rules a new password must meet (the pool enforces the same). */
export function passwordProblem(password: string): string | null {
  if (password.length < 8) return 'At least 8 characters.';
  if (!/[a-z]/.test(password)) return 'Add a lowercase letter.';
  if (!/[A-Z]/.test(password)) return 'Add a capital letter.';
  if (!/[0-9]/.test(password)) return 'Add a number.';
  return null;
}

/** One call to the Cognito user-pool API. These endpoints are public by design; the client id is not a secret. */
async function cognito<T>(action: string, body: Record<string, unknown>): Promise<T> {
  if (!authConfig) throw new AuthError('NotConfigured', 'Sign-in is not set up yet.');
  const resp = await fetch(`${authConfig.endpoint || `https://cognito-idp.${authConfig.region}.amazonaws.com`}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-amz-json-1.1', 'X-Amz-Target': TARGET + action },
    body: JSON.stringify({ ClientId: authConfig.client_id, ...body }),
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const code = String(data.__type || data.code || 'Error').split('#').pop() || 'Error';
    throw new AuthError(code, friendly(code, data.message));
  }
  return data as T;
}

function friendly(code: string, message?: string): string {
  switch (code) {
    case 'NotAuthorizedException':
      return 'Wrong email or password.';
    case 'UserNotFoundException':
      return 'No account with that email yet. Create one first.';
    case 'UsernameExistsException':
      return 'There is already an account with that email. Sign in instead.';
    case 'InvalidPasswordException':
      return 'That password is too simple. Use 8+ characters with a capital letter and a number.';
    case 'CodeMismatchException':
      return 'That code is not right. Check the email and try again.';
    case 'ExpiredCodeException':
      return 'That code has expired. Ask for a new one.';
    case 'LimitExceededException':
    case 'TooManyRequestsException':
      return 'Too many tries. Please wait a few minutes.';
    case 'InvalidParameterException':
      return 'Please check the email address.';
    case 'UserNotConfirmedException':
      return 'This account is not active yet. Please contact us.';
    default:
      return message || 'Something went wrong with sign-in.';
  }
}

interface AuthResult {
  AuthenticationResult?: { IdToken: string; AccessToken: string; RefreshToken?: string; ExpiresIn: number };
  ChallengeName?: string;
  Session?: string;
  ChallengeParameters?: Record<string, string>;
}

function accept(result: AuthResult, email = ''): Session {
  const r = result.AuthenticationResult;
  if (!r) throw new AuthError('NoTokens', 'Sign-in did not finish. Try again.');
  const claims = decodeClaims(r.IdToken);
  const next: Session = {
    idToken: r.IdToken,
    accessToken: r.AccessToken,
    refreshToken: r.RefreshToken || session?.refreshToken,
    expiresAt: (claims.exp ? claims.exp * 1000 : Date.now() + r.ExpiresIn * 1000) - 30_000,
    email: claims.email || email,
    name: claims.name || claims.given_name || '',
  };
  save(next);
  return next;
}

export const auth = {
  /** Fetch how the server signs people in. Called once at start. */
  async configure(): Promise<AuthConfig> {
    const resp = await fetch(`${API_BASE_URL}${API_PREFIX}/auth/config`);
    authConfig = (await resp.json()) as AuthConfig;
    return authConfig;
  },

  /** Development only: show the login page with a pretend pool, to design it. */
  preview(config: AuthConfig): void {
    authConfig = config;
  },

  get enabled(): boolean {
    return authConfig?.mode === 'cognito';
  },

  get googleEnabled(): boolean {
    return !!authConfig?.google;
  },

  get session(): Session | null {
    return session;
  },

  /** Create the account (through our API, so it is active at once) and sign in. */
  async signUp(name: string, email: string, password: string): Promise<Session> {
    const clean = email.trim().toLowerCase();
    const problem = passwordProblem(password);
    if (problem) throw new AuthError('InvalidPasswordException', problem);
    const resp = await fetch(`${API_BASE_URL}${API_PREFIX}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name.trim(), email: clean, password }),
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new AuthError(String(data.code || 'SignUpFailed'), friendly(String(data.code || ''), data.detail));
    return auth.signIn(clean, password);
  },

  /** Email + password, checked by Cognito. */
  async signIn(email: string, password: string): Promise<Session> {
    const clean = email.trim().toLowerCase();
    const result = await cognito<AuthResult>('InitiateAuth', {
      AuthFlow: 'USER_AUTH',
      AuthParameters: { USERNAME: clean, PREFERRED_CHALLENGE: 'PASSWORD', PASSWORD: password },
    });
    if (result.ChallengeName === 'NEW_PASSWORD_REQUIRED') {
      throw new AuthError('NewPassword', 'Please set a new password with "Forgot password".');
    }
    return accept(result, clean);
  },

  /** Forgot password: Cognito emails a reset code. */
  async forgot(email: string): Promise<void> {
    await cognito('ForgotPassword', { Username: email.trim().toLowerCase() });
  },

  async resetPassword(email: string, code: string, password: string): Promise<void> {
    const problem = passwordProblem(password);
    if (problem) throw new AuthError('InvalidPasswordException', problem);
    await cognito('ConfirmForgotPassword', { Username: email.trim().toLowerCase(), ConfirmationCode: code.trim(), Password: password });
  },

  /** Google: Cognito's hosted redirect, straight to Google's own sign-in, with PKCE. */
  async loginWithGoogle(): Promise<void> {
    if (!authConfig || authConfig.mode !== 'cognito') return;
    const verifier = randomString(48);
    const state = randomString(16);
    sessionStorage.setItem(PKCE, JSON.stringify({ verifier, state }));
    const params = new URLSearchParams({
      client_id: authConfig.client_id,
      response_type: 'code',
      scope: 'openid email profile',
      redirect_uri: redirectUri(),
      state,
      identity_provider: 'Google',
      code_challenge: await sha256(verifier),
      code_challenge_method: 'S256',
    });
    window.location.assign(`https://${authConfig.domain}/oauth2/authorize?${params}`);
  },

  /** On return from Google (?code=...&state=...): exchange the code for tokens. */
  async completeLogin(): Promise<boolean> {
    if (!authConfig || authConfig.mode !== 'cognito') return false;
    const url = new URL(window.location.href);
    const code = url.searchParams.get('code');
    const state = url.searchParams.get('state');
    if (!code) return false;
    const stored = sessionStorage.getItem(PKCE);
    sessionStorage.removeItem(PKCE);
    url.searchParams.delete('code');
    url.searchParams.delete('state');
    window.history.replaceState({}, '', url.pathname + url.search + url.hash);
    if (!stored) return false;
    const { verifier, state: expected } = JSON.parse(stored);
    if (state !== expected) return false;
    const body = new URLSearchParams({ grant_type: 'authorization_code', client_id: authConfig.client_id, code, code_verifier: verifier, redirect_uri: redirectUri() });
    const resp = await fetch(`https://${authConfig.domain}/oauth2/token`, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body });
    if (!resp.ok) return false;
    const t = await resp.json();
    accept({ AuthenticationResult: { IdToken: t.id_token, AccessToken: t.access_token, RefreshToken: t.refresh_token, ExpiresIn: t.expires_in } });
    return true;
  },

  /** A valid ID token for the API, refreshed quietly when it is about to expire. */
  async token(): Promise<string | null> {
    if (!session || !authConfig || authConfig.mode !== 'cognito') return null;
    if (Date.now() < session.expiresAt) return session.idToken;
    return (await auth.refresh())?.idToken || null;
  },

  async accessToken(): Promise<string | null> {
    if (!session) return null;
    if (Date.now() >= session.expiresAt) await auth.refresh();
    return session?.accessToken || null;
  },

  async refresh(): Promise<Session | null> {
    if (!session?.refreshToken) {
      save(null);
      return null;
    }
    try {
      const result = await cognito<AuthResult>('InitiateAuth', {
        AuthFlow: 'REFRESH_TOKEN_AUTH',
        AuthParameters: { REFRESH_TOKEN: session.refreshToken },
      });
      return accept(result, session.email);
    } catch {
      save(null);
      return null;
    }
  },

  /** Forget the tokens here and tell Cognito to end the session everywhere. */
  async logout(): Promise<void> {
    const access = session?.accessToken;
    save(null);
    if (access && authConfig?.mode === 'cognito') {
      await cognito('GlobalSignOut', { AccessToken: access }).catch(() => undefined);
    }
  },
};
