import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { isPublicPath } from './constants/routes';

/**
 * Middleware SSR Next.js - Protection des routes
 *
 * Logique :
 * 1. Whitelist : ressources statiques, Next.js internals, routes publiques
 * 2. Vérification auth : lecture du cookie refresh_token
 * 3. Redirection SSR si /(app)/* sans authentification
 * 4. Redirection inverse si utilisateur auth sur /(public)/*
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
   * Regex : /^\/(\(public\)|_next|favicon\.ico|public|api\/.*)/
   *
   * Explications :
   * - /(public) : Route group Next.js pour pages publiques
   * - _next : Assets Next.js (static, image optimization, etc.)
   * - favicon.ico : Favicon du site
   * - public : Dossier static files (/public/*)
   * - api/.* : API routes Next.js (/api/*)
   */
  const isWhitelisted =
    /^\/(\(public\)|_next|favicon\.ico|public|api\/.*)/.test(pathname);

  if (isWhitelisted) {
    return NextResponse.next();
  }

  /**
   * Vérification authentification via cookie HttpOnly
   *
   * Note : refresh_token stocké en cookie sécurisé par le backend
   * (à implémenter côté API si pas encore fait)
   */
  const refreshToken = request.cookies.get('refresh_token')?.value;
  const isAuthenticated = !!refreshToken;

  /**
   * Détection route publique via patterns regex
   * Voir constants/routes.ts pour la définition des patterns
   */
  const isPublic = isPublicPath(pathname);

  /**
   * Protection SSR : redirection si accès /(app)/* sans auth
   *
   * Redirection vers /(public)/login avec paramètre redirect
   * pour revenir à la page demandée après connexion
   */
  if (pathname.startsWith('/(app)') && !isAuthenticated) {
    const loginUrl = new URL('/(public)/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);

    if (process.env.NODE_ENV === 'development') {
      console.log(`[Middleware SSR] Redirect: ${pathname} → /(public)/login`);
    }

    return NextResponse.redirect(loginUrl);
  }

  /**
   * Redirection inverse : utilisateur authentifié sur route publique
   *
   * Exception : /(public)/logout (déconnexion autorisée)
   */
  if (isPublic && isAuthenticated && pathname !== '/(public)/logout') {
    if (process.env.NODE_ENV === 'development') {
      console.log(
        `[Middleware SSR] Authenticated user on public route → /(app)/dashboard`
      );
    }

    return NextResponse.redirect(new URL('/(app)/dashboard', request.url));
  }

  /**
   * Headers de debug pour développement
   */
  const response = NextResponse.next();
  if (process.env.NODE_ENV === 'development') {
    response.headers.set('x-pathname', pathname);
    response.headers.set('x-is-public', isPublic.toString());
    response.headers.set('x-is-authenticated', isAuthenticated.toString());
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
