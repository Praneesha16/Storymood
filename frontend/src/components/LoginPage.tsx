import React, { useState } from 'react';
import { auth, AuthError, passwordProblem, Session } from '../auth';
import Scenery from './Scenery';

interface Props {
  onSignedIn: (session: Session) => void;
}

type Tab = 'signin' | 'create' | 'forgot';

/**
 * The front door. Nothing else in the app is shown until a grown-up has signed in here.
 * Left: the storybook world. Right: a plain, calm form. Email + password; Google when
 * connected; a reset flow for forgotten passwords.
 */
const LoginPage: React.FC<Props> = ({ onSignedIn }) => {
  const [tab, setTab] = useState<Tab>('signin');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [code, setCode] = useState('');
  const [codeSent, setCodeSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);

  const switchTab = (next: Tab) => {
    setTab(next);
    setError(null);
    setNote(null);
    setCodeSent(false);
    setCode('');
  };

  const run = async (work: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    setNote(null);
    try {
      await work();
    } catch (err) {
      setError(err instanceof AuthError ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setBusy(false);
    }
  };

  const signIn = () => run(async () => onSignedIn(await auth.signIn(email, password)));
  const create = () => run(async () => onSignedIn(await auth.signUp(name, email, password)));
  const sendReset = () =>
    run(async () => {
      await auth.forgot(email);
      setCodeSent(true);
      setNote('We emailed you a reset code.');
    });
  const reset = () =>
    run(async () => {
      await auth.resetPassword(email, code, password);
      onSignedIn(await auth.signIn(email, password));
    });

  const pwHint = tab === 'create' && password ? passwordProblem(password) : null;

  return (
    <div className="login" id="login">
      <aside className="login__side" aria-hidden="true">
        <Scenery variant="hero" />
        <div className="login__sky">
          <div className="login__side-text">
            <h1 className="hero__logo">StoryMood</h1>
            <p className="login__tag">Say an idea. Pick a world. Hear your story.</p>
            <ul className="login__points">
              <li>New stories written for your child, in five languages</li>
              <li>Read aloud by storybook voices, or in your own</li>
              <li>Pictures on every page, music underneath</li>
            </ul>
          </div>
        </div>
      </aside>

      <main className="login__main">
        <div className="login__card" role="region" aria-labelledby="login-heading">
          <div className="login__tabs" role="tablist">
            <button type="button" role="tab" aria-selected={tab === 'signin'} className={`login__tab ${tab === 'signin' ? 'is-active' : ''}`} onClick={() => switchTab('signin')}>
              Sign in
            </button>
            <button type="button" role="tab" aria-selected={tab === 'create'} className={`login__tab ${tab === 'create' ? 'is-active' : ''}`} onClick={() => switchTab('create')}>
              Create account
            </button>
          </div>

          {tab === 'signin' && (
            <form className="login__form" onSubmit={(e) => { e.preventDefault(); void signIn(); }}>
              <h2 id="login-heading" className="login__heading">Welcome back</h2>
              <p className="login__lead">Grown-ups sign in here. The stories are waiting.</p>
              <label className="field">
                <span>Email</span>
                <input type="email" autoComplete="username" inputMode="email" value={email} onChange={(e) => setEmail(e.target.value)} disabled={busy} required />
              </label>
              <label className="field">
                <span>Password</span>
                <span className="field__pw">
                  <input type={showPassword ? 'text' : 'password'} autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} disabled={busy} required />
                  <button type="button" className="field__eye" onClick={() => setShowPassword((s) => !s)} aria-label={showPassword ? 'Hide password' : 'Show password'}>
                    {showPassword ? 'hide' : 'show'}
                  </button>
                </span>
              </label>
              <button type="submit" className="login__primary" disabled={busy || !email.trim() || !password}>
                {busy ? 'Signing in…' : 'Sign in'}
              </button>
              <button type="button" className="login__link" onClick={() => switchTab('forgot')} disabled={busy}>
                Forgot your password?
              </button>
              {auth.googleEnabled && (
                <>
                  <div className="login__or"><span>or</span></div>
                  <button type="button" className="login__secondary" disabled={busy} onClick={() => void auth.loginWithGoogle()}>
                    Continue with Google
                  </button>
                </>
              )}
            </form>
          )}

          {tab === 'create' && (
            <form className="login__form" onSubmit={(e) => { e.preventDefault(); void create(); }}>
              <h2 id="login-heading" className="login__heading">Create your account</h2>
              <p className="login__lead">One account per family, held by a grown-up.</p>
              <label className="field">
                <span>Your name</span>
                <input type="text" autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} disabled={busy} maxLength={60} required />
              </label>
              <label className="field">
                <span>Email</span>
                <input type="email" autoComplete="username" inputMode="email" value={email} onChange={(e) => setEmail(e.target.value)} disabled={busy} required />
              </label>
              <label className="field">
                <span>Password</span>
                <span className="field__pw">
                  <input type={showPassword ? 'text' : 'password'} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} disabled={busy} required />
                  <button type="button" className="field__eye" onClick={() => setShowPassword((s) => !s)} aria-label={showPassword ? 'Hide password' : 'Show password'}>
                    {showPassword ? 'hide' : 'show'}
                  </button>
                </span>
                <small className={`field__hint ${pwHint ? '' : password ? 'is-ok' : ''}`}>
                  {pwHint || (password ? 'Good password.' : 'At least 8 characters, with a capital letter and a number.')}
                </small>
              </label>
              <button type="submit" className="login__primary" disabled={busy || !name.trim() || !email.trim() || !!passwordProblem(password)}>
                {busy ? 'Creating…' : 'Create account'}
              </button>
              <p className="login__fine">By creating an account you agree that only grown-ups use it, and that we keep your email to find your stories and nothing more.</p>
            </form>
          )}

          {tab === 'forgot' && (
            <form className="login__form" onSubmit={(e) => { e.preventDefault(); void (codeSent ? reset() : sendReset()); }}>
              <h2 id="login-heading" className="login__heading">Reset your password</h2>
              <p className="login__lead">{codeSent ? 'Enter the code from the email and choose a new password.' : 'We will email you a code to set a new password.'}</p>
              <label className="field">
                <span>Email</span>
                <input type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} disabled={busy || codeSent} required />
              </label>
              {codeSent && (
                <>
                  <label className="field">
                    <span>Reset code</span>
                    <input inputMode="numeric" autoComplete="one-time-code" value={code} onChange={(e) => setCode(e.target.value)} disabled={busy} required />
                  </label>
                  <label className="field">
                    <span>New password</span>
                    <input type={showPassword ? 'text' : 'password'} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} disabled={busy} required />
                  </label>
                </>
              )}
              <button type="submit" className="login__primary" disabled={busy || !email.trim() || (codeSent && (!code.trim() || !!passwordProblem(password)))}>
                {busy ? 'Please wait…' : codeSent ? 'Set new password' : 'Email me a code'}
              </button>
              <button type="button" className="login__link" onClick={() => switchTab('signin')} disabled={busy}>
                Back to sign in
              </button>
            </form>
          )}

          {note && <p className="login__note" role="status">{note}</p>}
          {error && <p className="login__error" role="alert">{error}</p>}
        </div>
      </main>
    </div>
  );
};

export default LoginPage;
