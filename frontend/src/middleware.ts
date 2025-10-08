import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { isPublicPath, isProtectedRoute } from './constants/routes';

/**
 * Middleware SSR Next.js - Protection des routes
 *
 * Logique :
 * 1. Whitelist : ressources statiques, Next.js internals
 * 2. Vérification auth : lecture du cookie refresh_token
 * 3. Redirection SSR si route protégée sans authentification
 * 4. Redirection inverse si utilisateur auth sur route publique
 *
 * CRITICAL: Next.js supprime les route groups des URLs
 * - Fichier: app/(app)/dashboard/page.tsx
 * - URL réelle: /dashboard (PAS /(app)/dashboard)
 * - Donc on utilise isProtectedRoute() au lieu de pathname.startsWith()
 *
 * Avantages SSR :
 * - Pas de flash côté client
 * - Redirection instantanée avant hydration React
 * - Sécurité renforcée (pas de contenu protégé envoyé au client)
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  /**
   * Whitelist : ressources autorisées sans vérification
   *
   * Regex : /^\/(_next|favicon\.ico|public|api\/.*)/
   *
   * Explications :
   * - _next : Assets Next.js (static, image optimization, etc.)
   * - favicon.ico : Favicon du site
   * - public : Dossier static files (/public/*)
   * - api/.* : API routes Next.js (/api/*)
   */
  const isWhitelisted = /^\/(_next|favicon\.ico|public|api\/.*)/.test(pathname);

  if (isWhitelisted) {
    return NextResponse.next();
  }

  /**
   * Vérification authentification via cookie HttpOnly
   *
   * Note : refresh_token stocké en cookie sécurisé par le backend
   */
  const refreshToken = request.cookies.get('refresh_token')?.value;
  const isAuthenticated = !!refreshToken;

  /**
   * Détection route publique via patterns regex
   * Voir constants/routes.ts pour la définition des patterns
   *
   * CRITICAL: Vérifier les routes publiques EN PREMIER pour éviter
   * les boucles de redirection (ex: /login détecté comme protégé)
   */
  const isPublic = isPublicPath(pathname);

  /**
   * 1. ROUTES PUBLIQUES : laisser passer, avec redirection inverse si déjà auth
   */
  if (isPublic) {
    // Redirection inverse : utilisateur déjà authentifié sur /login
    if (isAuthenticated && pathname !== '/logout') {
      if (process.env.NODE_ENV === 'development') {
        console.log(
          `[Middleware SSR] ✅ Redirect: ${pathname} → /dashboard (already authenticated)`
        );
      }
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }

    // Route publique + pas authentifié (ou logout) → laisser passer
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Middleware SSR] ✅ Allow: ${pathname} (public route)`);
    }
    return NextResponse.next();
  }

  /**
   * 2. ROUTES PROTÉGÉES : vérifier authentification
   *
   * CRITICAL: Ne PAS utiliser pathname.startsWith('/(app)') car route groups
   * n'apparaissent pas dans les URLs Next.js
   */
  const isProtected = isProtectedRoute(pathname);

  if (isProtected && !isAuthenticated) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);

    if (process.env.NODE_ENV === 'development') {
      console.log(
        `[Middleware SSR] ❌ Redirect: ${pathname} → /login (not authenticated)`
      );
    }

    return NextResponse.redirect(loginUrl);
  }

  /**
   * Headers de debug pour développement
   */
  const response = NextResponse.next();
  if (process.env.NODE_ENV === 'development') {
    response.headers.set('x-pathname', pathname);
    response.headers.set('x-is-public', isPublic.toString());
    response.headers.set('x-is-protected', isProtected.toString());
    response.headers.set('x-is-authenticated', isAuthenticated.toString());
    console.log(
      `[Middleware SSR] ✅ Allow: ${pathname} (public=${isPublic}, protected=${isProtected}, auth=${isAuthenticated})`
    );
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
