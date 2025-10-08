/**
 * Utilitaires de gestion des tokens JWT côté client
 *
 * CRITICAL: Validation de l'expiration pour éviter requêtes avec tokens expirés
 */

interface JWTPayload {
  sub: string;
  exp: number;
  type: 'access' | 'refresh';
}

/**
 * Décode un JWT sans vérification de signature (client-side only)
 *
 * ⚠️ WARNING: Ne jamais utiliser pour validation de sécurité
 * Utilisé uniquement pour lire l'expiration et éviter requêtes inutiles
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    const payload = parts[1];
    // Convertir base64url en base64 standard
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload) as JWTPayload;
  } catch (error) {
    console.warn('Failed to decode JWT:', error);
    return null;
  }
}

/**
 * Vérifie si un token JWT est expiré
 *
 * @param token - Token JWT à vérifier
 * @param bufferSeconds - Temps de grâce avant expiration (défaut: 60s)
 * @returns true si expiré ou invalide, false sinon
 *
 * @example
 * ```ts
 * const token = localStorage.getItem('access_token');
 * if (isTokenExpired(token)) {
 *   // Rafraîchir le token avant la requête
 *   await refreshToken();
 * }
 * ```
 */
export function isTokenExpired(
  token: string | null | undefined,
  bufferSeconds: number = 60
): boolean {
  if (!token) {
    return true;
  }

  const payload = decodeJWT(token);
  if (!payload || !payload.exp) {
    return true;
  }

  // exp est en secondes, Date.now() en millisecondes
  const expirationTime = payload.exp * 1000;
  const currentTime = Date.now();
  const bufferTime = bufferSeconds * 1000;

  // Token expiré si : exp - buffer < maintenant
  return expirationTime - bufferTime < currentTime;
}

/**
 * Récupère le token d'accès depuis localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const authTokens = localStorage.getItem('auth_tokens');
    if (!authTokens) {
      return null;
    }

    const tokens = JSON.parse(authTokens) as { access_token?: string };
    return tokens.access_token || null;
  } catch (error) {
    console.warn('Failed to get access token:', error);
    return null;
  }
}

/**
 * Vérifie si l'utilisateur a des tokens valides (non expirés)
 *
 * @returns true si token présent et valide, false sinon
 */
export function hasValidToken(): boolean {
  const token = getAccessToken();
  return !isTokenExpired(token);
}

/**
 * Calcule le temps restant avant expiration (en secondes)
 *
 * @returns Secondes avant expiration, ou 0 si expiré/invalide
 */
export function getTokenTimeRemaining(
  token: string | null | undefined
): number {
  if (!token) {
    return 0;
  }

  const payload = decodeJWT(token);
  if (!payload || !payload.exp) {
    return 0;
  }

  const expirationTime = payload.exp * 1000;
  const currentTime = Date.now();
  const remaining = Math.floor((expirationTime - currentTime) / 1000);

  return Math.max(0, remaining);
}
