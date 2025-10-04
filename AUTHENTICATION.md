# Système d'Authentification Hybride

## Vue d'ensemble

Ce projet utilise un **système d'authentification hybride** combinant :
- **Cookies HttpOnly** pour les refresh tokens (sécurité maximale)
- **localStorage** pour les access tokens (performance client)

Cette approche offre le meilleur compromis entre **sécurité**, **performance** et **UX**.

---

## Architecture

### Flux d'Authentification Complet

```
┌──────────────────────────────────────────────────┐
│  1. Login/Register → Backend                     │
│     POST /auth/login ou /auth/register           │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│  2. Backend retourne                             │
│     - JSON: { access_token, refresh_token }      │
│     - Set-Cookie: refresh_token (HttpOnly)       │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│  3. Client stocke                                │
│     - localStorage: access_token uniquement      │
│     - Cookie: refresh_token (auto-géré browser)  │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│  4. Requêtes API authentifiées                   │
│     - Header: Authorization: Bearer {access}     │
│     - Cookie: refresh_token (auto-envoyé)        │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│  5. Middleware SSR Next.js                       │
│     - Lit cookie refresh_token                   │
│     - if (cookie) → utilisateur authentifié      │
│     - Affiche page directement → 0 FLASH         │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│  6. Refresh automatique (si access expiré)       │
│     POST /auth/refresh (cookie auto-envoyé)      │
│     - Retourne nouveau access_token              │
│     - Met à jour cookie refresh_token            │
└──────────────────────────────────────────────────┘
```

---

## Détails Techniques

### Backend (FastAPI)

#### Endpoints Modifiés

**1. POST /auth/login**
```python
@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    response: Response,  # ← Pour set_cookie
    db: Session = Depends(get_db)
):
    # ... authentification ...

    # Créer tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # ✅ Stocker refresh_token dans cookie HttpOnly
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,      # Protection XSS
        secure=False,       # True en production (HTTPS)
        samesite="lax",     # Protection CSRF
        max_age=7*24*60*60, # 7 jours
        path="/",
    )

    # Retourner TOUS les tokens dans JSON (compatibilité)
    return Token(access_token=access_token, refresh_token=refresh_token)
```

**2. POST /auth/register**
- Même logique que `/login`
- Set cookie après création utilisateur

**3. POST /auth/refresh**
```python
@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    token_data: TokenRefresh | None = None  # Fallback
):
    # Priorité 1 : Lire depuis cookie (recommandé)
    refresh_token_value = request.cookies.get("refresh_token")

    # Priorité 2 : Fallback body JSON (compatibilité mobile)
    if not refresh_token_value and token_data:
        refresh_token_value = token_data.refresh_token

    if not refresh_token_value:
        raise HTTPException(401, "Refresh token missing")

    # ... vérification token ...

    # Créer nouveaux tokens
    new_access = create_access_token(...)
    new_refresh = create_refresh_token(...)

    # ✅ Mettre à jour cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7*24*60*60,
        path="/",
    )

    return Token(access_token=new_access, refresh_token=new_refresh)
```

**4. POST /auth/logout**
```python
@router.post("/logout")
async def logout(response: Response):
    # Supprimer cookie
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="lax"
    )

    return {"message": "Successfully logged out"}
```

---

### Frontend (Next.js + React)

#### Client HTTP (services/http/client.ts)

```typescript
const init: RequestInit = {
  method,
  credentials: 'include',  // ✅ Envoie automatiquement cookies
  headers: requestHeaders,
  ...rest,
};
```

**Configuration déjà présente :**
- `credentials: 'include'` → envoie/reçoit cookies automatiquement
- Aucune modification nécessaire

---

#### Store Auth (features/auth/model/store.ts)

**Login/Register optimisés :**
```typescript
login: async (credentials) => {
  const tokens = await authApi.login(credentials);

  // ✅ Ne stocker QUE access_token
  localStorage.setItem('auth_tokens', JSON.stringify({
    access_token: tokens.access_token,
    // refresh_token omis → sécurisé dans cookie
  }));

  // ... suite ...
}
```

**Pourquoi ?**
- Refresh token (7 jours) protégé en HttpOnly → **pas accessible JS/XSS**
- Access token (30 min) dans localStorage → **risque limité** (courte durée)

---

#### Refresh Automatique (services/http/auth.ts)

```typescript
export async function tryRefresh(): Promise<boolean> {
  const res = await fetch('/api/auth/refresh', {
    method: 'POST',
    credentials: 'include',  // ✅ Cookie refresh_token envoyé auto
  });

  if (res.ok) {
    const data = await res.json();

    // ✅ Stocker nouveau access_token
    localStorage.setItem('auth_tokens', JSON.stringify({
      access_token: data.access_token,
      // refresh_token déjà mis à jour dans cookie par backend
    }));

    return true;
  }

  return false;
}
```

---

#### Middleware SSR (middleware.ts)

```typescript
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Lire cookie refresh_token
  const refreshToken = request.cookies.get('refresh_token')?.value;
  const isAuthenticated = !!refreshToken;

  // Redirection SSR si /(app)/* sans auth
  if (pathname.startsWith('/(app)') && !isAuthenticated) {
    return NextResponse.redirect(new URL('/(public)/login', request.url));
  }

  // ... reste ...
}
```

**Avantage :** Détection auth **AVANT** hydration React → **0 flash**

---

## Sécurité

### Protection XSS

| Token | Stockage | Durée | Exposition XSS |
|-------|----------|-------|----------------|
| **Refresh Token** | Cookie HttpOnly | 7 jours | ❌ **Impossible** (pas accessible JS) |
| **Access Token** | localStorage | 15-30 min | ⚠️ **Limitée** (courte durée) |

**Stratégie :**
- Token longue durée (refresh) = sécurité maximale (HttpOnly)
- Token courte durée (access) = impact XSS minimal (expire vite)

---

### Protection CSRF

**Cookie configuré avec :**
```python
samesite="lax"  # Bloque requêtes cross-site malveillantes
```

**Modes SameSite :**
- `strict` : Jamais envoyé en cross-site (trop strict pour OAuth, redirections)
- `lax` : Envoyé sur navigation GET, bloqué sur POST cross-site ✅ **Recommandé**
- `none` : Toujours envoyé (nécessite `secure=True`)

---

### HTTPS en Production

**⚠️ À activer en production :**

```python
# backend/app/routes/auth.py
response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    secure=True,        # ← ACTIVER en production
    samesite="lax",
    max_age=7*24*60*60,
    path="/",
)
```

**Raison :**
- `secure=True` → cookie envoyé UNIQUEMENT sur HTTPS
- Protection contre interception man-in-the-middle

---

## Configuration CORS

**Backend (main.py) :**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Développement
        "https://yourdomain.com",   # Production
    ],
    allow_credentials=True,  # ✅ Obligatoire pour cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Important :**
- `allow_credentials=True` **obligatoire** pour que le browser accepte les cookies
- `allow_origins` doit lister les origines **exactes** (pas de wildcard `*` avec credentials)

---

## Tests de Validation

### 1. Test Login avec Cookies

```bash
# Développement
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Vérifier réponse
# - JSON: { "access_token": "...", "refresh_token": "..." }
# - Header: Set-Cookie: refresh_token=...; HttpOnly; Path=/; SameSite=Lax
```

### 2. Test Refresh avec Cookie

```bash
# Simuler refresh avec cookie
curl -i -X POST http://localhost:8000/auth/refresh \
  -H "Cookie: refresh_token=VOTRE_REFRESH_TOKEN"

# Vérifier réponse
# - JSON: { "access_token": "nouveau...", "refresh_token": "nouveau..." }
# - Header: Set-Cookie: refresh_token=nouveau...; HttpOnly
```

### 3. Test Middleware SSR

```bash
# Sans cookie → doit rediriger
curl -I http://localhost:3000/(app)/dashboard
# → 307 Redirect vers /(public)/login

# Avec cookie → doit afficher
curl -I http://localhost:3000/(app)/dashboard \
  -H "Cookie: refresh_token=VALID_TOKEN"
# → 200 OK
```

---

## Debugging

### Vérifier Cookies dans DevTools

**Chrome/Edge/Firefox :**
1. F12 → Application/Stockage
2. Cookies → `http://localhost:3000`
3. Chercher `refresh_token`
4. Vérifier flags : `HttpOnly`, `SameSite=Lax`, `Path=/`

### Vérifier localStorage

**Console DevTools :**
```javascript
JSON.parse(localStorage.getItem('auth_tokens'))
// Devrait retourner : { access_token: "..." }
// PAS de refresh_token (sécurisé dans cookie)
```

### Logs Backend

**Développement : logs automatiques dans console :**
```
[Middleware SSR] Redirect: /(app)/dashboard → /(public)/login
[Auth] Login successful for user: test@example.com
[Auth] Refresh token from cookie: valid
```

---

## Migration depuis localStorage pur

### Avant (localStorage uniquement)

```typescript
// ❌ Ancien système
localStorage.setItem('auth_tokens', JSON.stringify({
  access_token: "...",
  refresh_token: "..."  // ← Exposé XSS
}));
```

### Après (Hybride)

```typescript
// ✅ Nouveau système
localStorage.setItem('auth_tokens', JSON.stringify({
  access_token: "...",
  // refresh_token omis → sécurisé dans cookie HttpOnly
}));
```

**Compatibilité :**
- Ancien code continue de fonctionner (backend retourne toujours les deux tokens en JSON)
- Nouveau code plus sécurisé (refresh_token pas stocké localStorage)
- Migration transparente pour les utilisateurs

---

## Résumé Avantages

| Aspect | Avant (localStorage) | Après (Hybride) |
|--------|---------------------|-----------------|
| **Sécurité** | ⚠️ XSS vulnérable | ✅ HttpOnly protégé |
| **Performance SSR** | ⚠️ Redirect systématique | ✅ Détection cookie (0 flash) |
| **UX** | ⚠️ Flash 100-300ms | ✅ Instantané |
| **Compatibilité** | ✅ Simple | ✅ Maintenue (fallback) |
| **Production-ready** | ⚠️ Risques XSS | ✅ Standards modernes |

---

## Prochaines Étapes (Optionnel)

### Token Blacklist (Révocation Immédiate)

**Actuellement :**
- Logout supprime cookie client
- Token reste valide jusqu'à expiration (7 jours max)

**Amélioration :**
```python
# Utiliser Redis pour blacklist tokens révoqués
@router.post("/logout")
async def logout(request: Request, response: Response, redis=Depends(get_redis)):
    token = request.cookies.get("refresh_token")
    if token:
        # Ajouter à blacklist
        redis.setex(f"revoked:{token}", 7*24*60*60, "1")

    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}

# Vérifier blacklist dans verify_token()
def verify_token(token: str, token_type: str):
    # ... validation JWT ...

    # Vérifier blacklist
    if redis.exists(f"revoked:{token}"):
        raise HTTPException(401, "Token revoked")

    return payload
```

### Rotation Automatique Refresh Token

**Chaque refresh génère nouveau refresh_token :**
- ✅ Déjà implémenté dans `/auth/refresh`
- Limite fenêtre d'attaque si token volé

---

## Maintenance

### Logs à Surveiller

**Erreurs courantes :**
```
Invalid refresh token → Cookie expiré ou invalide
Refresh token missing → Client sans cookie (première visite)
User not found → Utilisateur supprimé mais token valide
```

### Monitoring

**Métriques recommandées :**
- Taux de refresh (succès/échec)
- Durée moyenne refresh
- Tentatives login échouées
- Tokens révoqués

---

## Support

**Problèmes fréquents :**

1. **Cookie pas envoyé :**
   - Vérifier `credentials: 'include'` client
   - Vérifier `allow_credentials=True` backend
   - Vérifier domaine CORS exact

2. **Flash visible :**
   - Vérifier middleware SSR lit cookie
   - Vérifier cookie `Path=/` (pas `/api`)

3. **Logout ne fonctionne pas :**
   - Vérifier `delete_cookie()` path identique à `set_cookie()`
   - Vérifier client supprime également localStorage

**Contact :** Voir CLAUDE.md pour architecture complète
