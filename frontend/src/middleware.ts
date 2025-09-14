import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Pages publiques qui ne nécessitent pas d'authentification
  const publicPages = ['/login'];

  // Vérifier si la page actuelle est publique
  const isPublicPage = publicPages.some(page => pathname.startsWith(page));

  // Pour les pages publiques, laisser passer
  if (isPublicPage) {
    return NextResponse.next();
  }

  // Pour toutes les autres pages, l'AuthProvider côté client gérera la redirection
  // Le middleware ne peut pas accéder au localStorage côté serveur
  return NextResponse.next();
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