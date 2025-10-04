import { toHttpError } from './errors';

const REFRESH_ENDPOINT = '/api/auth/refresh';

/**
 * Rafraîchissement des tokens avec système hybride
 *
 * Le refresh_token est envoyé automatiquement via cookie HttpOnly
 * (credentials: 'include'), donc pas besoin de l'inclure dans le body.
 *
 * Le backend retourne un nouveau access_token + met à jour le cookie.
 */
export async function tryRefresh(): Promise<boolean> {
  try {
    const res = await fetch(REFRESH_ENDPOINT, {
      method: 'POST',
      credentials: 'include', // ✅ Envoie automatiquement cookie refresh_token
    });

    if (!res.ok) {
      if (res.status >= 500) {
        throw await toHttpError(res);
      }
      return false;
    }

    if (typeof window !== 'undefined') {
      try {
        const data = await res
          .clone()
          .json()
          .catch(() => null);
        if (data && typeof data === 'object' && 'access_token' in data) {
          /**
           * ✅ OPTIMISÉ : Ne stocker QUE l'access_token
           * refresh_token est déjà mis à jour dans le cookie par le backend
           */
          window.localStorage.setItem(
            'auth_tokens',
            JSON.stringify({
              access_token: data.access_token,
              // refresh_token omis → sécurisé dans cookie HttpOnly
            })
          );
        }
      } catch (error) {
        console.warn('Unable to persist refreshed tokens', error);
      }
    }

    return true;
  } catch (error) {
    console.warn('Auth refresh failed', error);
    return false;
  }
}
