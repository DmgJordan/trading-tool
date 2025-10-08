#!/usr/bin/env python3
"""
Script de migration : Copier les clés API de la table users vers user_profiles
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.core import SessionLocal

def main():
    db = SessionLocal()

    try:
        print("=" * 80)
        print("MIGRATION DES CLÉS API : users → user_profiles")
        print("=" * 80)

        # 1. Vérifier les clés dans users
        result = db.execute(text("""
            SELECT
                id,
                email,
                CASE WHEN hyperliquid_api_key IS NOT NULL THEN 'SET' ELSE 'NULL' END as hyper_key,
                CASE WHEN anthropic_api_key IS NOT NULL THEN 'SET' ELSE 'NULL' END as anthro_key,
                CASE WHEN coingecko_api_key IS NOT NULL THEN 'SET' ELSE 'NULL' END as coin_key
            FROM users
        """))

        users_with_keys = []
        for row in result:
            if row.hyper_key == 'SET' or row.anthro_key == 'SET' or row.coin_key == 'SET':
                users_with_keys.append(row)
                print(f"\n✅ User ID {row.id} ({row.email}) a des clés dans 'users':")
                print(f"   - Hyperliquid: {row.hyper_key}")
                print(f"   - Anthropic: {row.anthro_key}")
                print(f"   - CoinGecko: {row.coin_key}")

        if not users_with_keys:
            print("\n❌ Aucune clé API trouvée dans la table 'users'")
            print("Les clés doivent être enregistrées via l'interface /account")
            return

        # 2. Copier vers user_profiles
        print("\n" + "=" * 80)
        print("COPIE DES CLÉS VERS user_profiles")
        print("=" * 80)

        for user in users_with_keys:
            # Vérifier si un profil existe
            profile_result = db.execute(
                text("SELECT id FROM user_profiles WHERE user_id = :user_id"),
                {"user_id": user.id}
            )
            profile = profile_result.fetchone()

            if profile:
                # Update
                db.execute(text("""
                    UPDATE user_profiles
                    SET
                        hyperliquid_api_key = (SELECT hyperliquid_api_key FROM users WHERE id = :user_id),
                        hyperliquid_public_address = (SELECT hyperliquid_public_address FROM users WHERE id = :user_id),
                        anthropic_api_key = (SELECT anthropic_api_key FROM users WHERE id = :user_id),
                        coingecko_api_key = (SELECT coingecko_api_key FROM users WHERE id = :user_id)
                    WHERE user_id = :user_id
                """), {"user_id": user.id})
                print(f"✅ Clés copiées pour User ID {user.id} (UPDATE)")
            else:
                # Insert
                db.execute(text("""
                    INSERT INTO user_profiles (user_id, hyperliquid_api_key, hyperliquid_public_address, anthropic_api_key, coingecko_api_key)
                    SELECT id, hyperliquid_api_key, hyperliquid_public_address, anthropic_api_key, coingecko_api_key
                    FROM users
                    WHERE id = :user_id
                """), {"user_id": user.id})
                print(f"✅ Clés copiées pour User ID {user.id} (INSERT)")

        db.commit()

        # 3. Vérification
        print("\n" + "=" * 80)
        print("VÉRIFICATION")
        print("=" * 80)

        result = db.execute(text("""
            SELECT
                user_id,
                CASE WHEN hyperliquid_api_key IS NOT NULL THEN 'SET' ELSE 'NULL' END as hyper_key,
                CASE WHEN anthropic_api_key IS NOT NULL THEN 'SET' ELSE 'NULL' END as anthro_key,
                CASE WHEN coingecko_api_key IS NOT NULL THEN 'SET' ELSE 'NULL' END as coin_key
            FROM user_profiles
        """))

        for row in result:
            print(f"\n✅ UserProfile for User ID {row.user_id}:")
            print(f"   - Hyperliquid: {row.hyper_key}")
            print(f"   - Anthropic: {row.anthro_key}")
            print(f"   - CoinGecko: {row.coin_key}")

        print("\n" + "=" * 80)
        print("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
        print("=" * 80)
        print("\nRECHARGEZ votre page /account pour voir les clés !")

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    main()
