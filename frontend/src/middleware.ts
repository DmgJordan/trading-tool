import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Routes publiques qui ne nécessitent pas d'authentification
  const publicRoutes = ['/login'];
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

  // Routes statiques et API à ignorer
  if (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/api/') ||
    pathname.includes('.') || // fichiers statiques
    pathname === '/favicon.ico'
  ) {
    return NextResponse.next();
  }

  // En SSR, on ne peut pas accéder au localStorage, mais on peut utiliser les cookies
  // Si un système de cookies JWT est implémenté plus tard

  // Pour l'instant, on laisse l'AuthProvider côté client gérer la logique
  // Mais on ajoute des headers pour optimiser le processus
  const response = NextResponse.next();

  // Ajouter des headers pour indiquer l'état de la route
  response.headers.set('x-pathname', pathname);
  response.headers.set('x-is-public-route', isPublicRoute.toString());

  // Log pour debug (à supprimer en production)
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Middleware] ${pathname} - Public: ${isPublicRoute}`);
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
