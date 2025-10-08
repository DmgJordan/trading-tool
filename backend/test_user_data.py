#!/usr/bin/env python3
"""
Script de test pour vérifier les données utilisateur en base
"""
import os
import sys

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core import SessionLocal
from app.domains.auth.models import User
from app.domains.users.models import UserProfile
from app.domains.users.schemas import UserProfileResponse

def main():
    db: Session = SessionLocal()

    try:
        print("=" * 80)
        print("VÉRIFICATION DES DONNÉES UTILISATEUR")
        print("=" * 80)

        # Récupérer tous les utilisateurs
        users = db.query(User).all()

        if not users:
            print("\n❌ Aucun utilisateur trouvé en base de données")
            print("\n💡 Créez un compte via l'interface de login")
            return

        for user in users:
            print(f"\n📧 User: {user.email} (ID: {user.id})")

            # Récupérer le profil
            profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

            if not profile:
                print("   ⚠️  Aucun UserProfile associé")
                print("   💡 Le profil sera créé automatiquement au premier appel /users/me")
            else:
                print(f"   ✅ UserProfile ID: {profile.id}")

                # Vérifier les clés
                print("\n   🔑 Clés API:")
                print(f"      - Hyperliquid: {'✅ SET' if profile.hyperliquid_api_key else '❌ NULL'}")
                print(f"      - Anthropic:   {'✅ SET' if profile.anthropic_api_key else '❌ NULL'}")
                print(f"      - CoinGecko:   {'✅ SET' if profile.coingecko_api_key else '❌ NULL'}")

                # Tester la sérialisation
                print("\n   📦 Test UserProfileResponse:")
                response = UserProfileResponse.from_user_and_profile(user, profile)

                print(f"      - anthropic_api_key: {response.anthropic_api_key}")
                print(f"      - anthropic_api_key_status: {response.anthropic_api_key_status}")
                print(f"      - hyperliquid_api_key: {response.hyperliquid_api_key}")
                print(f"      - hyperliquid_api_key_status: {response.hyperliquid_api_key_status}")
                print(f"      - coingecko_api_key: {response.coingecko_api_key}")
                print(f"      - coingecko_api_key_status: {response.coingecko_api_key_status}")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    main()
